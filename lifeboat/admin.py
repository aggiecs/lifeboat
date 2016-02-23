from django.contrib import admin

from lifeboat import models

# Register your models here.
admin.site.register(models.Error)
admin.site.register(models.Module)
admin.site.register(models.Rescue)
admin.site.register(models.Retry)
admin.site.register(models.Statistic)
admin.site.register(models.AppliedRescue)
admin.site.register(models.StatisticHistory)
admin.site.register(models.Poll)