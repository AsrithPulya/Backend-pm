from .base import *
from .base import env


DATABASES = {
    'default': {
        'ENGINE': env('DB_ENGINE'),
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'), #env local
        'PASSWORD': env('DB_PASSWORD'), #env loca
        'HOST': env('DB_LOCALHOST'),  #env local
        'PORT': env('DB_PORT'),  #env local 
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com' # mail service smtp
EMAIL_HOST_USER = env('EMAIL_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_PASSWORD') #password #env local
EMAIL_PORT = 587
EMAIL_USE_TLS = True

FRONTEND_URL = 'http://localhost:3000/' #env local

import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:/Users/cron/Downloads/upheld-altar-216210-c7be04342362.json"
GCS_BUCKET_NAME = env('GCP_BUCKET_NAME')
GCS_UPLOAD_DIR = "documents-pm-test/"