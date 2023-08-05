import os

from django.utils.importlib import import_module
from django.utils.datastructures import SortedDict
from django.core.files.storage import FileSystemStorage
from django.contrib.staticfiles.finders import FileSystemFinder as \
    BaseFileSystemFinder, AppDirectoriesFinder as BaseAppDirectoriesFinder
from django.conf import settings


class FileSystemFinder(BaseFileSystemFinder):

    def __init__(self, apps=None, *args, **kwargs):
        super(FileSystemFinder, self).__init__(apps, *args, **kwargs)

        # Extend locations
        layers = list(settings.LAYERS['layers'])
        layers.reverse()
        processed = []
        new_locations = []
        for prefix, location in self.locations:
            for layer in layers:
                pth = os.path.join(location, layer)
                if os.path.exists(pth) and (pth not in processed):
                    processed.append(pth)
                    new_locations.append(('', pth))
        self.locations.extend(new_locations)

        for prefix, location in new_locations:
            filesystem_storage = FileSystemStorage(location=location)
            filesystem_storage.prefix = prefix
            self.storages[location] = filesystem_storage


class AppDirectoriesFinder(BaseAppDirectoriesFinder):

    def __init__(self, apps=None, *args, **kwargs):
        super(AppDirectoriesFinder, self).__init__(apps, *args, **kwargs)

        # Extends apps, add to storages
        layers = list(settings.LAYERS['layers'])
        layers.reverse()
        processed = []
        for k, v in self.storages.items():
            for layer in layers:
                pth = os.path.join(v.location, layer)
                if os.path.exists(pth) and (pth not in processed):
                    processed.append(pth)
                    # We're not really adding an app, but the superclass
                    # attaches no app specific logic to it so it is safe.
                    self.apps.append(pth)
                    filesystem_storage = FileSystemStorage(location=pth)
                    filesystem_storage.prefix = ''
                    self.storages[pth] = filesystem_storage
