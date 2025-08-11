import os
import sys
import django
import cpanel

import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("db")
log.setLevel(logging.DEBUG)

django_project_path = os.path.abspath(os.path.dirname(cpanel.__file__))
log.debug(f"django_project_path={django_project_path}")
log.debug(f"PATH={os.getenv('PATH')}")
sys.path.insert(0, django_project_path)
log.debug(f"PATH={os.getenv('PATH')}")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cpanel.settings")
log.debug(f"DJANGO_SETTINGS_MODULE={os.getenv('DJANGO_SETTINGS_MODULE')}")
django.setup()
log.debug("django.setup() completed")
log.debug(f"cpanel.setting.DATABASES={cpanel.settings.DATABASES}")

if cpanel.settings.DATABASES:
    from config.models import Option, Admin, Dialog, MessageTemplate


class Config:
    def __init__(self):
        self.token = lambda: Option.objects.get(name="token").value
        self.name = lambda: Option.objects.get(name="name").value
        self.greeting = lambda: Option.objects.get(name="greeting").value
        self.tpl = lambda: Option.objects.get(name="basic_template").value
        self.admins = lambda: Admin.objects.filter(active=True)

        self.dlg = Dialog.objects
        self.tpl = MessageTemplate.objects
