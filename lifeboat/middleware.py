import logging
import inspect
import traceback
import sys
import json

from django.conf import settings
from django import http
from django.core.urlresolvers import RegexURLResolver

from lifeboat.models import Module as Lb_Module
from lifeboat.models import Error as Lb_Error

logger = logging.getLogger("lifeboat-info")


def resolver(request):
    """
    Returns a RegexURLResolver for the request's urlconf.

    If the request does not have a urlconf object, then the default of
    settings.ROOT_URLCONF is used.e
    """
    from django.conf import settings
    urlconf = getattr(request, "urlconf", settings.ROOT_URLCONF)
    return RegexURLResolver(r'^/', urlconf)


class LifeboatExceptionMiddleware(object):
    def process_exception(self, request, exception):
        # Get the exception info now, in case another exception is thrown later.
        if isinstance(exception, http.Http404):
            return
        else:
            return self.handle_500(request, exception)

    def handle_500(self, request, exception):
        logger.info("Lifeboat handling exception.")
        exctype, exc_val, tb, = sys.exc_info()
        jsonable_local_vars = {}
        local_vars = inspect.trace()[-1][0].f_locals  # For now, just use the top of the trace stack
        for k, v in local_vars.items():
            if k == "self":
                jsonable_local_vars[k] = "self"
                continue
            try:
                jsonable_local_vars[k] = str(v)
            except ValueError:
                jsonable_local_vars[k] = "Un-serializable value of " + str(type(v))


        # Modules are identified by (file_name, code_obj_name). If it exists use that, otherwise create a module obj.
        error_file_name = inspect.trace()[-1][0].f_code.co_filename
        error_code_obj_name = inspect.trace()[-1][0].f_code.co_name

        lb_module_filter = Lb_Module.objects.filter(file_name=error_file_name,
                                                    code_obj_name=error_code_obj_name)
        if lb_module_filter:
            lb_module = lb_module_filter.get()
        else:
            lb_module = Lb_Module.objects.create(file_name=error_file_name,
                                                 code_obj_name=error_code_obj_name)

        Lb_Error.objects.create(module=lb_module, exception=str(exctype),
                                traceback=traceback.format_exc(tb),
                                vars=json.dumps(jsonable_local_vars),
                                traceback_msg=str(exc_val), created_by="Lifeboat")


