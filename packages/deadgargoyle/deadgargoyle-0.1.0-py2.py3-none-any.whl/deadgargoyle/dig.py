from optparse import make_option
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.template.defaultfilters import yesno
from django.utils import timezone

from gargoyle import models


"""
TODO - check for orphans in database, but gargoyle might remove them
"""

# TODO conditions for reporting:
#  A. The switch at global state hasn't been modified in six months (settable?)
#  B. The code base returns a 0


class GraveSearch(object):

    def __init__(self, path='.', ignore=''):

        self.cache_modules(path, ignore)

        self.results = []

        for key in sorted(settings.GARGOYLE_SWITCH_DEFAULTS.keys()):
            result = {
                        'key': key,
                        'record': None,
                        'count': 0,
                        'status': None,
                        'is_old': False
                }
            try:
                result['record'] = models.Switch.objects.get(
                    key=key,
                    status=models.GLOBAL
                )
            except models.Switch.DoesNotExist:
                # Either the switch exists and is not set to global.
                #   or the switch is not in the database.
                self.results.append(result)
                continue

            # List the status!
            result['status'] = result['record'].get_status_label()

            # Is the record too old?
            result['is_old'] = result['record'].date_modified < timezone.now() - timezone.timedelta(days=180)

            # Count how many times we can find the Gargoyle switch key in the code base.
            result['count'] = self.search_code_base(key)

            self.results.append(result)

    def display_results(self):
        display = """
Candidates for Removal
======================
Is Old?  Is Used?  Key\n"""
        for result in self.results:
            display += '   {0}        {1}      {2}\n'.format(
                    self.yes_no_cap(result['is_old']),
                    result['count'],
                    result['key']
                )
        return display

    def yes_no_cap(self, value):
        return yesno(value).upper()[0]

    def set_module(self, file_name):
        # Check if it's in the page cache
        if file_name in self.modules:
            return

        # grab it otherwise
        with open(file_name) as f:
            code = f.read()
        self.modules[file_name] = code

    def cache_modules(self, path, ignore):
        self.modules = {}
        for root, dirs, files in os.walk(path):
            for name in files:
                if name == ignore:
                    continue
                if name.endswith((".py", ".html")):
                    file_name = os.path.join(root, name)
                    self.set_module(file_name)

    def search_code_base(self, key):
        KEY = key.upper()
        count = 0

        for file_name, code in self.modules.items():
            if key in code or KEY in code:
                count += 1
        return count
