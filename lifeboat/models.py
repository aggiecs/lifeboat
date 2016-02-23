import re
import os
import glob
import types
import json
import sys
import inspect
import pytz

import datetime
import traceback
import logging
from socket import gethostname

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.db import models
from django.conf import settings

logger = logging.getLogger("lifeboat")


class Module(models.Model):
    file_name = models.CharField(max_length=256, blank=True, null=True)
    code_obj_name = models.CharField(max_length=128, blank=True, null=True)
    module_name = models.CharField(max_length=128, blank=True, null=True)
    max_errors = models.IntegerField(default=25)

    @property
    def name(self):
        if self.file_name:
            return self.file_name.split('/')[-1] + ": " + self.code_obj_name
        else:
            return self.module_name

    def __unicode__(self):
        if self.module_name:
            return self.module_name
        else:
            return "%s" % (self.file_name)




ERROR_STATUSES = (
    ("unhandled", "unhandled"),
    ("retrying", "retrying"),
    ("handled", "handled"),
    ("failed", "failed"),
)

CREATED_BY_CHOICES = (
    ("user", "user"),
    ("lifeboat", "lifeboat"),
)


class Error(models.Model):
    module = models.ForeignKey(Module)
    exception = models.CharField(blank=True, null=True, max_length=64,)
    traceback = models.TextField(max_length=1024, blank=True, null=True)
    traceback_msg = models.TextField(blank=True, null=True, )
    params = models.TextField(blank=True, null=True)
    vars = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=16, blank=True, null=True, choices=ERROR_STATUSES, default="unhandled", db_index=True)
    received = models.DateTimeField(auto_now_add=True, db_index=True)
    created_by = models.CharField(default="user", max_length=16)

    def __unicode__(self):
        return "{2}: {1} - {0}".format(self.module, self.received, self.status)

    @classmethod
    def report_error(cls, tb, params=None, vals=None,  traceback_msg=None, status="unhandled"):

        # get the calling module
        current_frame = inspect.currentframe()
        calling_frame = inspect.getouterframes(current_frame, 2)
        module_name = calling_frame[1][3]
        modules = Module.objects.filter(name=module_name)
        if modules.exists():
            module = modules[0]
        else:
            module = Module.objects.create(name=module_name)

        if module:
            cls.objects.create(module=module, params=params, vals=vals, status=status,
                               traceback=traceback.format_exc(tb), created_by="User",
                               traceback_msg=traceback_msg)

    @property
    def desc(self):
        return "{0} - {1} | {2}".format(self.exception_type, self.traceback_msg, self.received)

    @property
    def exception_type(self):
        return self.exception.split("'")[-2]

    def to_dict(self):
        return {
            "id": self.id,
            "module": self.module.name,
            "module_id": self.module.id,
            "exception": self.exception_type,
            "traceback": self.traceback,
            "tracback_msg": self.traceback_msg,
            "params": self.params,
            "vars": json.loads(self.vars),
            "status": self.status,
            "received": self.received.strftime("%m/%d/%y %H:%M:%S"),
            "received_pieces": [self.received.year, self.received.month, self.received.day, self.received.hour,
                                self.received.minute, self.received.second],
            "created_by": self.created_by,
            "desc": self.desc,
        }

RESCUE_TYPES = (
    ("ignore", "ignore"),
    ("email", "email"),
    ("callback", "callback"),
    ("log", "log"),
)


class Rescue(models.Model):
    module = models.ForeignKey(Module, blank=True, null=True)
    error_tb_pattern = models.CharField(max_length=100, blank=True, null=True, verbose_name="Traceback Pattern:")
    error_exception_msg_pattern = models.CharField(max_length=100, blank=True, null=True, verbose_name="Exception Msg Pattern:")
    error_exception_type = models.CharField(max_length=100, blank=True, null=True, verbose_name="Exception Type:")
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=RESCUE_TYPES)
    max_retries = models.IntegerField(default=0)
    priority = models.IntegerField(default=1)
    destination = models.CharField(max_length=200, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    delay = models.IntegerField(default=0)

    def __unicode__(self):
        return "{0} - {1}".format(self.name, self.type,)

    @classmethod
    def rescue(cls, error):
        for rescue in cls.objects.all():
            if not rescue.rescue_applies_to_error(error):
                continue

            logger.debug("Attempting {0} rescue using {1} id: {2}".format(rescue.type, rescue.name, rescue.id))
            # if we've made it this far, this error needs to be handled by the current rescue.
            try:
                rescue.apply_to_error(error)
            except Exception:
                retry_count = Retry.objects.filter(error=error, rescue=rescue).count()
                if retry_count >= rescue.max_retries:
                    ex_type, ex, tb = sys.exc_info()
                    Error.report_error(None, None, tb, traceback_msg="Failed to handle rescue(id=%s)" % rescue.id,
                                       status="failed")
                else:
                    Retry.objects.create(error=error, rescue=rescue)

    def apply_to_error(self, error):
        if self.rescue_applies_to_error(error):
            applied = True
            if self.type == "ignore":
                self.handle_ignore(error)
            elif self.type == "email":
                self.handle_email(error)
            elif self.type == "callback":
                self.handle_callback(error)
            elif self.type == "log":
                self.handle_log(error)
            else:
                applied = False
            if applied:
                  AppliedRescue.objects.create(rescue=self, error=error)
            return applied
        return False


    def rescue_applies_to_error(self, error):
        rescue_applies = True
        if not (self.error_tb_pattern or self.error_exception_msg_pattern or self.error_exception_type):
            if self.module and self.module == error.module:
                rescue_applies = True
            else:
                rescue_applies = False
        if self.error_tb_pattern and not re.search (self.error_tb_pattern, error.traceback):
            rescue_applies = False
        if self.error_exception_msg_pattern and \
                not re.search(self.error_exception_msg_pattern, error.traceback_msg):
            rescue_applies = False
        if self.error_exception_type and not re.search(self.error_exception_type, error.exception):
            rescue_applies = False
        if self.module and self.module != error.module:
            rescue_applies = False
        return rescue_applies

    @classmethod
    def get_callback_choices(cls):
        cbs = []
        for app_name in settings.INSTALLED_APPS:
            app_rescues = []
            try:
                m = __import__(app_name)
            except ImportError:
                pass
            else:
                if hasattr(m, "rescues"):
                    app_rescues = [k for k, v in getattr(m, "rescues").__dict__.items()
                                   if isinstance(v, types.FunctionType)]
                for ar in app_rescues:
                    cbs.append("%s.rescues.%s" % (m.__name__, ar))
        return cbs

    def handle_ignore(self, error):
        error.status = "handled"
        error.save()

    def handle_email(self, error):
        msg_html = render_to_string('lifeboat/email/rescue_email.html', error.to_dict())

        send_mail("%s %s" % (error.module, error.received),
                  msg_html,
                  "lifeboat-no-reply@%s" % gethostname(),
                  [x.strip() for x in self.destination.split(',')],
                  html_message=msg_html,
                  )
        error.status = "handled"
        error.save()

    def handle_callback(self, error):
        available_callbacks = Rescue.get_callback_choices()
        if self.destination not in Rescue.get_callback_choices():
            Error.report_error(None, None, None,
                               traceback_msg="Unable to complete requested call back to %s.\
                                Function not in list of available callbacks: %s" %
                                             (self.destination, available_callbacks),
                                status="failed")
            error.status = ""
        else:
            m = __import__(self.destination.split(".")[0])
            getattr(getattr(m, "rescues"), self.destination.split(".")[-1])(error)  # m.rescues.function(error)
            error.status = "handled"

    def handle_log(self, error):
        if self.destination not in logging.Logger.manager.loggerDict.keys():
            Error.report_error(None, None, None,
                               traceback_msg="Unable to log to %s.\
                               destination not in list of available loggers: %s" %
                                             (self.destination, logging.Logger.manager.loggerDict.keys()),
                               status="failed")
        else:
            logger = logging.getLogger(self.destination)
            logger.error(error.as_dict())


class AppliedRescue(models.Model):
    rescue = models.ForeignKey(Rescue)
    error = models.ForeignKey(Error)
    applied = models.DateTimeField(auto_now_add=True)


class Retry(models.Model):
    rescue = models.ForeignKey(Rescue)
    error = models.ForeignKey(Error)
    result = models.CharField(max_length=20, blank=True, null=True)
    attempted = models.DateTimeField(auto_now_add=True)


STAT_TYPES = (
    ("count", "Count Matches"),
    ("sum", "Sum Over Matches"),
    ("save_most_recent", "Store Most Recent Match"),
)


class Statistic(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=STAT_TYPES)
    date_format = models.CharField(max_length=100, default="%Y-%m-%d %H:%M:%S,%f",
                                   help_text="Python datetime strptime format")
    pattern = models.CharField(max_length=512, blank=True, null=True, help_text="regular expression")
    log_path = models.CharField(max_length=200)
    value_int = models.BigIntegerField(default=0)
    value_str = models.CharField(max_length=128, blank=True, null=True)
    last_reset = models.DateTimeField(blank=True, null=True)
    last_read = models.DateTimeField(blank=True, null=True)
    active = models.BooleanField(blank=True, default=True)
    reset_every = models.IntegerField(default=0, help_text="hours (default=0 never resets)")

    def __init__(self, *args, **kwargs):
        self.last_reset = datetime.datetime.now()
        self.last_read = datetime.datetime(year=1970, month=1, day=1)
        super(Statistic, self).__init__(*args, **kwargs)

    def __unicode__(self):
        return self.name

    @classmethod
    def python_datetime_format_to_regex(cls, date_format):
        p_to_r = {
            "%%": r'%',
            "%d": r'\d{2}',
            "%m": r'\d{2}',
            "%y": r'\d{2}',
            "%Y": r'\d{4}',
            "%H": r'\d{2}',
            "%M": r'\d{2}',
            "%f": r'\d{3,6}',
            "%S": r'\d{2}',
            "%I": r'\d{2}',
            "%p": r'[AM|PM]',
            "%Z": r'\w{3}?',
            "%z": r'[\+\d{4}]?',
        }
        i = 0
        dt_pattern = date_format
        re_pattern = ''
        while i < len(dt_pattern) - 1:
            if dt_pattern[i:i+2] in p_to_r:
                re_pattern += p_to_r[dt_pattern[i:i+2]]
                i += 2
            else:
                re_pattern += dt_pattern[i]
                i += 1
        return re_pattern

    @classmethod
    def gather_stat(cls, statistic):
        log_paths = sorted(glob.glob(statistic.log_path + "*"), key=lambda k: os.stat(k).st_mtime, reverse=True)
        for log_path in log_paths:
            file_stats = os.stat(log_path)

            m_time = datetime.datetime.fromtimestamp(file_stats.st_mtime).replace(tzinfo=timezone.get_current_timezone())
            if (not statistic.last_read) or statistic.last_read.replace(tzinfo=timezone.get_current_timezone()) < m_time:
                re_date = re.compile(r'(' + Statistic.python_datetime_format_to_regex(statistic.date_format) + r')')
                with open(log_path, 'r') as f:
                    lines = f.readlines()
                for line in lines:
                    re_date_search_results = re_date.search(line)
                    if not re_date_search_results:
                        continue
                    dt_str = re_date_search_results.group(1)
                    dt = datetime.datetime.strptime(dt_str, statistic.date_format).replace(tzinfo=timezone.get_current_timezone())  # Might fail, allow exception to propagate.
                    if (not statistic.last_read) or dt > statistic.last_read.replace(tzinfo=timezone.get_current_timezone()):
                        re_pattern = re.compile(statistic.pattern)
                        re_pattern_search_results = re_pattern.search(line)
                        if re_pattern_search_results:
                            if statistic.type == "count":
                                Poll.objects.create(statistic=statistic, value_int=1)
                            if statistic.type == "sum":
                                Poll.objects.create(statistic=statistic, value_int=int(re_pattern_search_results.group(1)))
                            if statistic.type == "save_most_recent":
                                Poll.objects.create(statistic=statistic, value_str=re_pattern_search_results.group(1))
                        statistic.last_read = dt
                        statistic.save()

    def try_reset_value(self):
        if not self.last_reset:
            self.last_reset = datetime.datetime(1970, 1, 1, tzinfo=timezone.get_current_timezone())
            self.save()
        if self.reset_every:
            td = datetime.timedelta(hours=self.reset_every)
            if (datetime.datetime.now() - td).replace(tzinfo=timezone.get_current_timezone()) < self.last_reset:
                StatisticHistory.objects.create(statistic=self, value_int=self.value_int, value_str=self.value_str)
                self.last_reset = datetime.datetime.now()
                self.value_int = 0
                self.value_str = ""
                self.save()

    @property
    def value(self):
        time = self.last_reset or datetime.datetime(1970, 1, 1, tzinfo=timezone.get_current_timezone())

        if self.type == "count":
            return sum([x.value_int for x in self.poll_set.filter(polled_at__gte=time)])
        if self.type == "sum":
            return sum([x.value_int for x in self.poll_set.filter(polled_at__gte=time)])
        if self.type == "save_most_recent":
            return self.poll_set.latest("polled_at").value_str



class Poll(models.Model):
    statistic = models.ForeignKey(Statistic)
    polled_at = models.DateTimeField(auto_now=True, db_index=True)
    value_int = models.BigIntegerField(default=0)
    value_str = models.CharField(max_length=128, blank=True, null=True)


class StatisticHistory(models.Model):
    statistic = models.ForeignKey(Statistic)
    value_int = models.BigIntegerField(default=0)
    value_str = models.CharField(max_length=128, blank=True, null=True)