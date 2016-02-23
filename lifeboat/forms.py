__author__ = 'boredom23309'

from django.forms import ModelForm
from django.core.validators import ValidationError
from django.core.validators import validate_email

from lifeboat import models


class StatisticForm(ModelForm):
    class Meta:
        model = models.Statistic
        fields = ["name", "type", "log_path", "date_format", "pattern", "reset_every"]

class RescueForm(ModelForm):
    class Meta:
        model = models.Rescue
        fields = ["name", "module", "error_tb_pattern", "error_exception_msg_pattern", "error_exception_type",
                  "type", "destination"]

    def __init__(self, *args, **kwargs):
        error = None
        if "error" in kwargs:
            error = kwargs["error"]
            del kwargs['error']
        module = None
        if "module" in kwargs:
            module = kwargs["module"]
            del kwargs['module']
        super(RescueForm, self).__init__(*args, **kwargs)
        if error:
            try:
                error_type = error.exception.split("'")[1].split(".")[-1]
            except IndexError:
                pass
            else:
                self.fields["error_exception_type"].initial = error_type
            self.fields["module"].initial = error.module
            if error.traceback_msg:
                self.fields["error_exception_msg_pattern"].initial = ".*" + error.traceback_msg + ".*"
        if module:
            self.fields["module"].initial = module

    def clean(self, *args, **kwargs):
        cleaned_data = super(RescueForm, self).clean()
        type = cleaned_data.get("type")
        destination = cleaned_data.get("destination")

        if type != "ignore" and not destination:
            raise ValidationError('Destination is required for resuce type %s' % type, code="invalid")
        if type == "email":
            email_addresses = destination.split(',')
            for email in email_addresses:
                validate_email(email.strip())
        if type == "callback":
            if destination not in models.Rescue.get_callback_choices():
                raise ValidationError('Invalid value in destination field for rescue of type callback.', code="invalid")
        #if not (cleaned_data.get("error_tb_pattern") or cleaned_data.get("error_exception_msg_pattern") or cleaned_data.get("error_exception_type")):
        #   raise ValidationError('At least one of the following must be provided: Traceback Pattern, Exception Msg Pattern, Exception Type', code="invalid")

        return cleaned_data