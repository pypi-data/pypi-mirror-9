from django.shortcuts import render_to_response
from django.template import RequestContext

import logging
log = logging.getLogger('djinn_core')

def djinn_server_error(request, template_name="500.html"):
    return render_to_response(template_name, {},
                        context_instance=RequestContext(request),)
