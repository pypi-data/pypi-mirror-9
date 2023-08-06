from django.contrib.staticfiles import finders
from django.conf import settings


def add_ignores(ignore_patterns):
    ignore = settings.STATICFILES_FINDERS_IGNORE

    if ignore:
        if ignore_patterns:
            ignore_patterns.extend(ignore)
        else:
            ignore_patterns = ignore

    return ignore_patterns


class FileSystemFinder(finders.FileSystemFinder):
    def list(self, ignore_patterns):
        return super(FileSystemFinder, self).list(add_ignores(ignore_patterns))
