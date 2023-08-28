import os.path
import time
import redis
from celery import shared_task
import logging

from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


@app.task(name="image_processing_task_v2", bind=True)
def image_processing_task_v2(self, *args, **kwargs):
   pass


