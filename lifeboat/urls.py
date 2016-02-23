from django.conf.urls import include, url
from django.contrib import admin

from lifeboat import views

urlpatterns = [
    # Examples:
    # url(r'^$', 'lifeboat_test.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', views.LifeboatIndex.as_view(), name="lifeboat-index"),
    url(r'^module/(\d+)/$', views.LifeboatModule.as_view(), name="lifeboat-module"),
    url(r'^error/(\d+)/$', views.LifeboatError.as_view(), name="lifeboat-error"),
    url(r'^statistic/(\d+)/$', views.LifeboatStatistic.as_view(), name="lifeboat-statistic"),
    url(r'^rescue/(\d+)/$', views.LifeboatRescue.as_view(), name="lifeboat-rescue"),
    url(r'^rescue/(\d+)/(\d+)/$', views.LifeboatApplyRescue.as_view(), name="lifeboat-apply-rescue"),


    url(r'^json/error_list$', views.JSONErrorList.as_view(), name="lifeboat-json-errors"),
]
