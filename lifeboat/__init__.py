from __future__ import absolute_import

import sys
import os
import glob
import re
import datetime
import json
import traceback
import inspect
import logging

from django.conf import settings

from .models import Error as Lb_Error
from .models import Module as Lb_Module
from .celery import app as celery_app

# Ensure required settings are available in settings module
REQUIRED_SETTINGS = []  # TODO LIFEBOAT__STMP_RELAY?
for s in REQUIRED_SETTINGS:
    if not hasattr(settings, s):
        raise AttributeError("Lifeboat requires %s be present in the Django Settings" % s)

