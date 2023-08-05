import os, sys
import pkg_resources
from django.template.loaders.app_directories import Loader as BaseLoader
from django.utils.importlib import import_module
from django.core.exceptions import ImproperlyConfigured


fs_encoding = sys.getfilesystemencoding() or sys.getdefaultencoding()

app_template_dirs = []

for entrypoint in pkg_resources.iter_entry_points(group="djinn.skin"):
        
    app = entrypoint.module_name

    try:
        mod = import_module(app)
    except ImportError, e:
        raise ImproperlyConfigured('ImportError %s: %s' % (app, e.args[0]))

    template_dir = os.path.join(os.path.dirname(mod.__file__), 'templates')

    if os.path.isdir(template_dir):
        app_template_dirs.append(template_dir.decode(fs_encoding))


app_template_dirs = tuple(app_template_dirs)


class SkinTemplateLoader(BaseLoader):

    def load_template(self, template_name, template_dirs=None):

        return super(SkinTemplateLoader, self).load_template(
            template_name, template_dirs=app_template_dirs)


_loader = SkinTemplateLoader()
