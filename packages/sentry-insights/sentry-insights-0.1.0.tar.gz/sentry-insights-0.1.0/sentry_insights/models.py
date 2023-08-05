"""
sentry_insights.models
~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2011 by Linovia, see AUTHORS for more details.
:copyright: (c) 2014 by tinyclues, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from django import forms
from django.conf import settings

from sentry.plugins.bases.notify import NotifyPlugin

import sentry_insights

import requests
import json
import logging


DEFAULT_ENDPOINT = "https://insights-collector.newrelic.com/v1/accounts/{account_id}/events"


class InsightsOptionsForm(forms.Form):
    account_id = forms.CharField(help_text="Your insights account id.")
    key = forms.CharField(help_text="Your insights key.")
    event_type = forms.CharField(help_text="The event type.")


class InsightsMessage(NotifyPlugin):
    author = 'Boris Feld'
    author_url = 'https://github.com/tinyclues/sentry-insights'
    version = sentry_insights.VERSION
    description = "Event notification to Insights."
    resource_links = [
        ('Bug Tracker', 'https://github.com/tinyclues/sentry-insights/issues'),
        ('Source', 'https://github.com/tinyclues/sentry-insights'),
    ]
    slug = 'insights'
    title = 'Insights'
    conf_title = title
    conf_key = 'insights'
    project_conf_form = InsightsOptionsForm

    def is_configured(self, project):
        return all((self.get_option(k, project) for k in ('account_id', 'key', 'event_type')))

    def should_notify(self, group, event):
        if group.is_muted():
            return False

        return True

    def notify_users(self, group, event, fail_silently=False):
        project = event.project
        account_id = self.get_option('account_id', project)
        key = self.get_option('key', project)
        event_type = self.get_option('event_type', project)

        level = group.get_level_display().upper()

        if account_id and key and event_type:
            self.send_payload(account_id, key, event_type, event, level)

    def send_payload(self, account_id, key, event_type, alert, level):
        endpoint = DEFAULT_ENDPOINT.format(account_id=account_id)

        values = {
            'eventType': event_type,
            'level': level,
            'project_name': alert.project.name,
            'platform': alert.project.platform,
            'event_id': alert.event_id
        }

        tags = dict(alert.get_tags(False))
        values.update(tags)

        headers = {'content-type': 'application/json',
                   'X-Insert-Key': key}
        result = requests.post(endpoint, data=json.dumps([values]),
                               headers=headers)
        try:
            result.raise_for_status()
        except:
            logger = logging.getLogger('sentry.plugins.insights')
            logger.error('Event was not sent to insights',
                         exc_info=True, extra={'data': {'payload': values}})
