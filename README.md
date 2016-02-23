# Lifeboat
Django application for error tracking and automated error handling in Django projects.


# Installing
Rabbitmq Setup(If missing):

zypper install rabbitmq-server
sudo systemctl start rabbitmq
sudo rabbitmqctl add_user :app_user: :app_password:
sudo rabbitmqctl add_vhost :app:
sudo rabbitmqctl set_permissions -p :app: :app_user: “.*" “.*" ".*"

Celery Setup(If missing):
pip install celery
pip install django-celery

settings.py
BROKER_HOST = “127.0.0.1"
BROKER_PORT = 5672
BROKER_USER = “:app_user :"
BROKER_PASSWORD = “:app_password:"
BROKER_VHOST = “:app:"
CELERY_BACKEND = “ampq"

BROKER_URL = CELERY_BACKEND +"://"+_BROKER_USER+":"+_BROKER_PASSWORD+"@"+_BROKER_HOST+":"+str(_BROKER_PORT)+"/"+_BROKER_VHOST

CELERY_RESULT_BACKEND = “djcelery.backends.database:DatabaseBackend"
CELERYBEAT_SCHEDULER = “djcelery.schedulers.DatabaseScheduler"
INSTALLED_APPS = ( … , “djcelery”, “lifeboat”,  “rest_framework”, “rest_framework.authtoken”)
MIDDLEWARE_CLASSES = ( … , “lifeboat.middleware.LifeboatExceptionMiddleware )
REST_FRAMEWORK = { ‘DEFAULT_AUTHENTICATION_CLASSES’: ( ‘rest_framework.authentication.BasicAuthentication’, ‘rest_framework.authentication.SessionAuthentication’, ‘rest_framework.authentication.TokenAuthentication’) }

Install App:
python setup.py install

Root URL CONF urls.py
urlpatterns add url(r’^lifeboat/‘, include(‘lifeboat.urls”)),
