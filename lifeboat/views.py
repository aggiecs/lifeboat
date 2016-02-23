import json
import datetime

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.views.generic import View
from django.contrib import messages
from django.db.models import Q
from django.utils.html import escape
from django.core.paginator import Paginator, EmptyPage
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response as RF_Response
from rest_framework import status as RF_Status

from lifeboat import models
from lifeboat import forms


class LifeboatRestView(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)


# Create your views here.
class LifeboatIndex(View):

    @method_decorator(login_required)
    @method_decorator(user_passes_test(lambda user: user.is_staff))
    def get(self, request):
        failed_errors = models.Error.objects.filter(status="failed")
        unhandled_errors = models.Error.objects.filter(status="unhandled")
        handled_errors = models.Error.objects.filter(status="handled")

        stats = {
            # Counts must take place before setting the associated (k,v)
            # pairs otherwise queries get converted to list types implicitly.

            "handled_errors_count": handled_errors.count(),
            "unhandled_errors_count": unhandled_errors.count(),
            "failed_errors_count": failed_errors.count(),
            "errors_count": models.Error.objects.count(),

            "statistics": models.Statistic.objects.all(),
        }

        stat_form = forms.StatisticForm()

        return render(request, "lifeboat/info_panel/index.html", {"stats": stats, "stat_form": stat_form})

    @method_decorator(login_required)
    @method_decorator(user_passes_test(lambda user: user.is_staff))
    def post(self, request):
        failed_errors = models.Error.objects.filter(status="failed")
        unhandled_errors = models.Error.objects.filter(status="unhandled")
        handled_errors = models.Error.objects.filter(status="handled")

        stats = {
            # Counts must take place before setting the associated (k,v)
            # pairs otherwise queries get converted to list types implicitly.

            "handled_errors_count": handled_errors.count(),
            "unhandled_errors_count": unhandled_errors.count(),
            "failed_errors_count": failed_errors.count(),
            "errors_count": models.Error.objects.count(),

            "statistics": models.Statistic.objects.all(),
        }

        stat_form = forms.StatisticForm(request.POST)
        if stat_form.is_valid():
            stat_form.save()
            messages.add_message(request, messages.SUCCESS, "Statistic Created.")
            return redirect("lifeboat-index")
        else:
            messages.add_message(request, messages.ERROR, "Statistic not created.")
        return render(request, "lifeboat/info_panel/index.html", {"stats": stats})


class LifeboatError(View):
    @method_decorator(login_required)
    @method_decorator(user_passes_test(lambda user: user.is_staff))
    def get(self, request, error_id):
        # TODO supply list of rescues which apply to an error
        module_id = request.GET.get("module_id", None)
        module = None
        if module_id:
            module = get_object_or_404(models.Module, id=module_id)

        error = get_object_or_404(models.Error, id=error_id)
        rescue_form = forms.RescueForm(error=error)
        rescue_callback_choices = json.dumps(models.Rescue.get_callback_choices() or [])

        rescues = [rescue for rescue in models.Rescue.objects.all() if rescue.rescue_applies_to_error(error)]
        applied_rescues = models.AppliedRescue.objects.filter(error=error)

        return render(request, "lifeboat/info_panel/error_info.html", {"error": error, "rescue_form": rescue_form,
                                                                            "rescue_callback_choices": rescue_callback_choices,
                                                                            "rescues": rescues, "applied_rescues": applied_rescues,
                                                                            "module": module})
    @method_decorator(login_required)
    @method_decorator(user_passes_test(lambda user: user.is_staff))
    def post(self, request, error_id):
        module_id = request.GET.get("module_id", None)
        module = None
        if module_id:
            module = get_object_or_404(models.Module, id=module_id)

        error = get_object_or_404(models.Error, id=error_id)
        rescue_form = forms.RescueForm(request.POST, error=error)
        rescue_callback_choices = json.dumps(models.Rescue.get_callback_choices() or [])

        rescues = [rescue for rescue in models.Rescue.objects.all() if rescue.rescue_applies_to_error(error)]
        applied_rescues = models.AppliedRescue.objects.filter(error=error)

        if rescue_form.is_valid():
            rescue_form.save()
            messages.add_message(request, messages.SUCCESS, "Rescue Created.")
            return redirect("lifeboat-error", error_id)
        messages.add_message(request, messages.ERROR, "Rescue not valid")
        return render(request, "lifeboat/info_panel/error_info.html", {"error": error, "rescue_form": rescue_form,
                                                                            "rescue_callback_choices": rescue_callback_choices,
                                                                            "rescues": rescues, "applied_rescues": applied_rescues,
                                                                            "module": module})
class LifeboatRescue(View):
    @method_decorator(login_required)
    @method_decorator(user_passes_test(lambda user: user.is_staff))
    def get(self, request, rescue_id):
        module_id = request.GET.get("module_id", None)
        module = None
        if module_id:
            module = get_object_or_404(models.Module, id=module_id)
        rescue = get_object_or_404(models.Rescue, id=rescue_id)
        rescue_form = forms.RescueForm(instance=rescue)
        rescue_callback_choices = json.dumps(models.Rescue.get_callback_choices() or [])

        applied_rescues = models.AppliedRescue.objects.filter(rescue=rescue)

        return render(request, "lifeboat/info_panel/edit_rescue.html", {"rescue_form": rescue_form, "module": module,
                                                                            "rescue_callback_choices": rescue_callback_choices,
                                                                             "applied_rescues": applied_rescues})
    @method_decorator(login_required)
    @method_decorator(user_passes_test(lambda user: user.is_staff))
    def post(self, request, rescue_id):
        module_id = request.GET.get("module_id", None)
        module = None
        if module_id:
            module = get_object_or_404(models.Module, id=module_id)
        rescue = get_object_or_404(models.Rescue, id=rescue_id)
        rescue_form = forms.RescueForm(request.POST, instance=rescue)
        rescue_callback_choices = json.dumps(models.Rescue.get_callback_choices() or [])

        applied_rescues = models.AppliedRescue.objects.filter(rescue=rescue)

        if rescue_form.is_valid():
            rescue_form.save()
            messages.add_message(request, messages.SUCCESS, "Rescue Updated.")
            return redirect("lifeboat-rescue", rescue_id)

        return render(request, "lifeboat/info_panel/edit_rescue.html", {"rescue_form": rescue_form, "module": module,
                                                                            "rescue_callback_choices": rescue_callback_choices,
                                                                             "applied_rescues": applied_rescues})

class LifeboatApplyRescue(View):
    @method_decorator(login_required)
    @method_decorator(user_passes_test(lambda user: user.is_staff))
    def post(self, request, rescue_id, error_id):
        rescue = get_object_or_404(models.Rescue, id=rescue_id)
        error = get_object_or_404(models.Error, id=error_id)
        try:
            rescue.apply_to_error(error)
        except Exception:
            messages.add_message(request, messages.ERROR, "Unable to apply rescue to error")
        else:
            messages.add_message(request, messages.SUCCESS, "Rescue applied to error.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

class LifeboatModule(View):
    @method_decorator(login_required)
    @method_decorator(user_passes_test(lambda user: user.is_staff))
    def get(self, request, module_id):
        module = get_object_or_404(models.Module, id=module_id)

        rescue_form = forms.RescueForm(module=module)
        rescue_callback_choices = json.dumps(models.Rescue.get_callback_choices() or [])

        rescues = models.Rescue.objects.filter(module=module)

        return render(request, "lifeboat/info_panel/module_info.html",
                      {"module": module, "rescue_form": rescue_form, "rescue_callback_choices": rescue_callback_choices,
                       "rescues": rescues})

    @method_decorator(login_required)
    @method_decorator(user_passes_test(lambda user: user.is_staff))
    def post(self, request, module_id):
        module = get_object_or_404(models.Module, id=module_id)
        rescue_form = forms.RescueForm(request.POST, module=module)
        rescue_callback_choices = json.dumps(models.Rescue.get_callback_choices() or [])
        rescues = models.Rescue.objects.filter(module=module)
        if rescue_form.is_valid():
            rescue_form.save()
            messages.add_message(request, messages.SUCCESS, "Rescue Created.")
            return redirect('lifeboat-module', module_id)
        messages.add_message(request, messages.ERROR, "Rescue not valid. Please try again.")
        return render(request, "lifeboat/info_panel/module_info.html",
                      {"module": module, "rescue_form": rescue_form, "rescue_callback_choices": rescue_callback_choices,
                       "rescues": rescues})

class LifeboatStatistic(View):
    @method_decorator(login_required)
    @method_decorator(user_passes_test(lambda user: user.is_staff))
    def get(self, request, statistic_id):
        statistic = get_object_or_404(models.Statistic, id=statistic_id)
        stat_form = forms.StatisticForm(instance=statistic)
        return render(request, "lifeboat/info_panel/statistic_info.html", {"stat_form": stat_form})

    @method_decorator(login_required)
    @method_decorator(user_passes_test(lambda user: user.is_staff))
    def get(self, request, statistic_id):
        statistic = get_object_or_404(models.Statistic, id=statistic_id)
        stat_form = forms.StatisticForm(request.POST, instance=statistic)
        if stat_form.is_valid():
            stat_form.save()
            messages.add_message(request, messages.SUCCESS, "Statistic Updated.")
            return redirect("lifeboat-statistic", statistic_id)
        messages.add_message(request, messages.ERROR, "Statistic NOT updated. Please try again.")
        return render(request, "lifeboat/info_panel/statistic_info.html", {"stat_form": stat_form})



class JSONErrorList(LifeboatRestView):

    @method_decorator(login_required)
    @method_decorator(user_passes_test(lambda user: user.is_staff))
    def get(self, request):
        page = request.GET.get("page", 1)
        page_size = request.GET.get("page_size", 25)
        sort_by = request.GET.get("sort_by", "received")
        status = request.GET.get("status", None)
        module = request.GET.get("module", None)
        module_id = request.GET.get("module_id", None)
        rescue_id = request.GET.get("rescue_id", None)
        exception = request.GET.get("exception", None)
        include_stats = request.GET.get("include_stats", False)
        last_24_hours = request.GET.get("last_24_hours", False)
        search_terms = request.GET.get("search_term", "")

        rescue = None
        if rescue_id:
            rescue = get_object_or_404(models.Rescue, id=rescue)

        valid_fields = ["exception", "traceback", "traceback_msg", "module"
                        "params", "vars", "status", "received", "created_by", "id"]

        # Ensure that sort_by is valid
        if sort_by:
            sort_by_fields = sort_by.split(',')
            for field in sort_by_fields:
                valid_field = True
                if field.startswith('-'):
                    field = field[1:]
                if field not in valid_fields:
                    valid_fields = False
                if not valid_field:
                    if field not in valid_fields:
                        return RF_Response({"msg_type": "error", "msg": "%s is not a valid field." % field },
                                           status=RF_Status.HTTP_400_BAD_REQUEST)
        else:
            sort_by = "-received"
            sort_by_fields = sort_by.split(',')

        if "is:" in search_terms:
            for term in search_terms.split(" "):
                if term.startswith("is:"):
                    status = term[3:]

        search_term = " ".join([x for x in search_terms.split(" ") if not x.startswith("is:")])

        if last_24_hours:
            errors = models.Error.objects.filter(received__gt=(datetime.datetime.now() - datetime.timedelta(days=1)))
            page_size = 10000
            page = 1
        else:
            errors = models.Error.objects.all()
            if status is not None:
                errors = errors.filter(status=status)
            if module is not None:
                errors = errors.filter(module__name__contains=exception)
            if module_id is not None:
                errors = errors.filter(module__id=module_id)
            if search_term is not None:
                errors = errors.filter(Q(module__file_name__contains=search_term) | Q(exception__contains=search_term) |
                                       Q(traceback_msg__contains=search_term))
            if sort_by and sort_by_fields:
                errors = errors.order_by(*sort_by_fields)

        try:
            page_size = int(page_size)
            page = int(page)
        except:
            return RF_Response({"msg_type": "error", "msg": "Page number and Page must be integers."},
                               status=RF_Status.HTTP_400_BAD_REQUEST)

        if page_size < 2:
            RF_Response({"msg_type": "error", "msg": "Page size must be an integer greater than 2."},
                               status=RF_Status.HTTP_400_BAD_REQUEST)

        # fetch a page of pre-filtered errors
        paginator = Paginator(errors, page_size)
        try:
            page_of_errors = paginator.page(page)
        except EmptyPage:
            return RF_Response({}, status=RF_Status.HTTP_204_NO_CONTENT)

        next_page = page
        if page != paginator.num_pages:
            next_page += 1

        previous_page = page
        if page != 1:
            previous_page -= 1

        #TODO before this can be used a serializer for stats must be created
        #stats = None
        #if include_stats:
        #    stats = models.Statistic.objects.all()


        return RF_Response({
            "previous_page": previous_page,
            "current_page": page,
            "next_page": next_page,
            "last_page": paginator.num_pages,
            "errors": [x.to_dict() for x in page_of_errors],
            "sort_by": sort_by_fields,
            "page_size": page_size,
            "handled_errors_count": errors.filter(status="handled").count(),
            "unhandled_errors_count": errors.filter(status="unhandled").count(),
            "failed_errors_count": errors.filter(status="failed").count(),
            "errors_count": errors.count(),
            #"stats": stats,

        })
