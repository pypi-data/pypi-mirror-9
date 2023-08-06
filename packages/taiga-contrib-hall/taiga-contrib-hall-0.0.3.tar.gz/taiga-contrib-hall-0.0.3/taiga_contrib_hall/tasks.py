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

from django.conf import settings
from django.template import loader, Context


from rest_framework.renderers import UnicodeJSONRenderer

from taiga.base.utils.db import get_typename_for_model_instance
from taiga.base.utils import json
from taiga.celery import app


def _get_type(obj):
    content_type = get_typename_for_model_instance(obj)
    return content_type.split(".")[1]


def _send_request(url, data):
    data["title"] = getattr(settings, "HALLHOOKS_USERNAME", "Taiga")
    data["picture"] = getattr(settings, "HALLHOOKS_ICON", "https://tree.taiga.io/images/favicon.png")

    requests.post(url, data=data)


def _markdown_field_to_message(template_field, field_name, values):
    context = Context({"field_name": field_name, "values": values })
    change_field_text = template_field.render(context)

    return change_field_text.strip()


def _field_to_message(template_field, field_name, values):
    context = Context({"field_name": field_name, "values": values })
    change_field_text = template_field.render(context)

    return change_field_text.strip()


@app.task
def change_hallhook(url, obj, change):
    obj_type = _get_type(obj)

    template_change = loader.get_template('taiga_contrib_hall/change.jinja')
    context = Context({ "obj": obj, "obj_type": obj_type, "change": change })

    change_text = template_change.render(context)
    data = {
        "message": change_text.strip(),
    }

    # Get markdown fields
    if change.diff:
        template_field = loader.get_template('taiga_contrib_hall/field-diff.jinja')
        included_fields = ["description", "content", "blocked_note"]

        for field_name, values in change.diff.items():
            if field_name in included_fields:
                message = _markdown_field_to_message(template_field, field_name, values)

                if message:
                    data['message'] += "\n" + message

    # Get rest of fields
    if change.values_diff:
        template_field = loader.get_template('taiga_contrib_hall/field-diff.jinja')
        excluded_fields = ["description_diff", "description_html", "content_diff",
                           "content_html", "blocked_note_diff", "blocked_note_html",
                           "backlog_order", "kanban_order", "taskboard_order", "us_order",
                           "finish_date", "is_closed"]

        for field_name, values in change.values_diff.items():
            if field_name in excluded_fields:
                continue

            message = _field_to_message(template_field, field_name, values)

            if message:
                data['message'] += "\n" + message

    _send_request(url, data)


@app.task
def create_hallhook(url, obj):
    obj_type = _get_type(obj)

    template = loader.get_template('taiga_contrib_hall/create.jinja')
    context = Context({ "obj": obj, "obj_type": obj_type })

    data = {
        "message": template.render(context).strip(),
    }

    _send_request(url, data)


@app.task
def delete_hallhook(url, obj):
    obj_type = _get_type(obj)

    template = loader.get_template('taiga_contrib_hall/delete.jinja')
    context = Context({ "obj": obj, "obj_type": obj_type })

    data = {
        "message": template.render(context).strip(),
    }

    _send_request(url, data)


@app.task
def test_hallhook(url):
    data = {
        "message": "Test hall message",
    }

    _send_request(url, data)
