import pkg_resources
from django.views.generic import TemplateView
from django.core.urlresolvers import reverse


class AdminMixin(object):

    """ Mixin for admin views """

    def list_tools(self):

        tools = []

        for entrypoint in pkg_resources.iter_entry_points(group="djinn.tool",
                                                          name="info"):

            tool = entrypoint.load()()

            tool['url'] = reverse(tool['url'])

            tools.append(tool)

        return tools


class AdminView(TemplateView, AdminMixin):

    template_name = "djinn_core/admin.html"
