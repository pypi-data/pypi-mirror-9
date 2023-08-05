from django.db import models
from django.conf import settings
from django.template import Context, Template

from cabot.cabotapp.alert import AlertPlugin, AlertPluginUserData

from os import environ as env
import requests

pushover_alert_url = "https://api.pushover.net/1/messages.json"

pushover_template = "Service {{ service.name }} {% if service.overall_status == service.PASSING_STATUS %}is back to normal{% else %}reporting {{ service.overall_status }} status{% endif %}: {{ scheme }}://{{ host }}{% url 'service' pk=service.id %}."

class PushoverAlert(AlertPlugin):
    name = "Pushover"
    author = "Daniel Nelson"

    def send_alert(self, service, users, duty_officers):

        # Pushover handles repeat alerts, so we can skip them
        if service.overall_status == service.old_overall_status:
            return

        for u in users:
            alert = True
            priority = 1
            try:
                data = AlertPluginUserData.objects.get(user=u, title=PushoverAlertUserData.name)
            except:
                pass

            if service.overall_status == service.WARNING_STATUS:
                if not data.alert_on_warn:
                    alert = False
                    priority = 0
            elif service.overall_status == service.ERROR_STATUS:
                priority = 1
            elif service.overall_status == service.CRITICAL_STATUS:
                priority = 2
            elif service.overall_status == service.PASSING_STATUS:
                priority = 0
                if service.old_overall_status == service.CRITICAL_STATUS:
                    # cancel the recurring crit
                    pass
            else:
                # something weird happened
                alert = False

            if not alert:
                return
            # now let's send
            c = Context({
                'service': service,
                'host': settings.WWW_HTTP_HOST,
                'scheme': settings.WWW_SCHEME,
                'jenkins_api': settings.JENKINS_API,
                })
            message = Template(pushover_template).render(c)
            self._send_pushover_alert(message, key=data.key, priority=priority)
    def _send_pushover_alert(self, message, key, priority=0):
        payload = {
                'token':env['PUSHOVER_TOKEN'],
                'user': key,
                'priority': priority,
                'title': 'Cabot ALERT',
                'message': message,
            }

        if priority == 2:
            payload['retry'] = 60
            payload['expire'] = 3600

        r = requests.post(pushover_alert_url, data=payload)



class PushoverAlertUserData(AlertPluginUserData):
    name = "Pushover Plugin"
    key = models.CharField(max_length=32, blank=False, verbose_name="User/Group Key")
    alert_on_warn = models.BooleanField(default=False)
