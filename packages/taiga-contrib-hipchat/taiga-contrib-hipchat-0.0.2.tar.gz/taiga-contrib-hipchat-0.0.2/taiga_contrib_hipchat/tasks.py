# Copyright (C) 2013 Andrey Antukh <niwi@niwi.be>
# Copyright (C) 2014 Jesús Espino <jespinog@gmail.com>
# Copyright (C) 2014 David Barragán <bameda@dbarragan.com>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import requests
import logging

from django.conf import settings
from django.template import loader, Context


from rest_framework.renderers import UnicodeJSONRenderer

from taiga.base.utils.db import get_typename_for_model_instance
from taiga.celery import app


logger = logging.getLogger(__name__)


def _get_type(obj):
    content_type = get_typename_for_model_instance(obj)
    return content_type.split(".")[1]


def _send_request(url, data):
    data["notify"] = True
    serialized_data = UnicodeJSONRenderer().render(data)
    headers = {
        'Content-type': 'application/json',
    }
    if settings.CELERY_ENABLED:
        requests.post(url, data=serialized_data, headers=headers)
        return
    try:
        requests.post(url, data=serialized_data, headers=headers)
    except Exception:
        logger.error("Error sending request to HipChat")


def _desc_or_content_to_attachment(template_field, field_name, values):
    context = Context({"field_name": field_name, "values": values})
    change_field_text = template_field.render(context)

    return change_field_text.strip()


def _field_to_attachment(template_field, field_name, values):
    context = Context({"field_name": field_name, "values": values})
    change_field_text = template_field.render(context)

    return change_field_text.strip()


@app.task
def change_hipchathook(url, obj, change):
    obj_type = _get_type(obj)

    template_change = loader.get_template('taiga_contrib_hipchat/change.jinja')
    context = Context({"obj": obj, "obj_type": obj_type, "change": change})

    change_text = template_change.render(context)
    data = {"message": change_text.strip()}
    data["color"] = "yellow"

    # Get description and content
    if change.diff:
        template_field = loader.get_template('taiga_contrib_hipchat/field-diff.jinja')
        included_fields = ["description", "content"]

        for field_name, values in change.diff.items():
            if field_name in included_fields:
                attachment = _desc_or_content_to_attachment(template_field, field_name, values)

                data["message"] += attachment

    if change.values_diff:
        template_field = loader.get_template('taiga_contrib_hipchat/field-diff.jinja')
        excluded_fields = ["description_diff", "description_html", "content_diff",
                           "content_html", "backlog_order", "kanban_order",
                           "taskboard_order", "us_order", "finish_date",
                           "is_closed"]

        for field_name, values in change.values_diff.items():
            if field_name in excluded_fields:
                continue

            attachment = _field_to_attachment(template_field, field_name, values)

            if attachment:
                data["message"] += attachment

    _send_request(url, data)


@app.task
def create_hipchathook(url, obj):
    obj_type = _get_type(obj)

    template = loader.get_template('taiga_contrib_hipchat/create.jinja')
    context = Context({"obj": obj, "obj_type": obj_type})

    data = {
        "message": template.render(context),
        "color": "green",
    }
    _send_request(url, data)


@app.task
def delete_hipchathook(url, obj):
    obj_type = _get_type(obj)

    template = loader.get_template('taiga_contrib_hipchat/delete.jinja')
    context = Context({"obj": obj, "obj_type": obj_type})

    data = {
        "message": template.render(context),
        "color": "red",
    }

    _send_request(url, data)


@app.task
def test_hipchathook(url):
    data = {
        "message": "<b>Test</b><br/>Test <a href='http://hipchat.com'>HipChat</a> message",
        "color": "purple",
    }

    _send_request(url, data)
