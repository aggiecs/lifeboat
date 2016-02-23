# Lifeboat
Django application for error tracking and automated error handling in Django projects. When the lifeboat application and it's exception middleware are installed, exceptions in Django create error objects which can be tracked and handled via asynchronous Celery tasks. 

![Summary Page](https://cloud.githubusercontent.com/assets/3632074/13253577/5f4eca82-da02-11e5-9076-54729bd5a907.png)
![Summary Page for Particular Module](https://cloud.githubusercontent.com/assets/3632074/13253576/5f4e9f4e-da02-11e5-8eca-443f3fbd6f07.png)

When an exception occurs, an error object is created and can be viewed later. 

![View Error Page](https://cloud.githubusercontent.com/assets/3632074/13253578/5f4ff042-da02-11e5-8949-2184a2285657.png)

Errors are created in an "unhandled" state until they are "rescued." A Rescue object can be created to "handle" the error by either ignoring it, emailing a notification of the error, logging the error using a specified log handler, or by excecuting a user-created callback function. 

![Ignore all errors in test_app/views.py](https://cloud.githubusercontent.com/assets/3632074/13253579/5f4fe2b4-da02-11e5-9736-d0ced8ac0f7e.png)

![Email about Value Errors in test_app/views.py](https://cloud.githubusercontent.com/assets/3632074/13253580/5f50a816-da02-11e5-9e6c-5f5563093834.png)

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
BROKER_USER = “:app_user:"
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
