import os
import pkg_resources
from django.utils.datastructures import SortedDict
from django.contrib.staticfiles.finders import AppDirectoriesFinder
from django.contrib.staticfiles.storage import AppStaticStorage


class FlexiblePathStorage(AppStaticStorage):

    def __init__(self, app, *args, **kwargs):

        self.source_dir = kwargs.get("source_dir", "static")
        del kwargs['source_dir']

        super(FlexiblePathStorage, self).__init__(app, *args, **kwargs)

class PluginFilesFinder(AppDirectoriesFinder):

    def __init__(self, apps=None, *args, **kwargs):

        self.apps = []
        self.storages = SortedDict()

        for entrypoint in pkg_resources.iter_entry_points(group="djinn.app"):

            app = entrypoint.module_name

            if app in self.storages.keys():
                continue

            app_storage = self.storage_class(app)
            self.storages[app] = app_storage

        for entrypoint in pkg_resources.iter_entry_points(group="djinn.app",
                                                          name="statics"):
            path = entrypoint.load()()
            app = entrypoint.module_name

            self.storages[app] = FlexiblePathStorage(app, source_dir=path)

        for app in self.storages.keys():
            if os.path.isdir(self.storages[app].location):

                if app not in self.apps:
                    self.apps.append(app)
