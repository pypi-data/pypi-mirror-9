# Copyright (C) 2014 Andrey Antukh <niwi@niwi.be>
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

from django.conf import settings

from taiga.projects.history import services as history_service
from taiga.projects.history.choices import HistoryType

from . import tasks


def _get_project_slackhooks(project):
    slackhooks = []
    for slackhook in project.slackhooks.all():
        slackhooks.append({
            "id": slackhook.pk,
            "url": slackhook.url,
        })
    return slackhooks


def on_new_history_entry(sender, instance, created, **kwargs):
    if instance.is_hidden:
        return None

    model = history_service.get_model_from_key(instance.key)
    pk = history_service.get_pk_from_key(instance.key)
    obj = model.objects.get(pk=pk)

    slackhooks = _get_project_slackhooks(obj.project)

    if instance.type == HistoryType.create:
        task = tasks.create_slackhook
        extra_args = []
    elif instance.type == HistoryType.change:
        task = tasks.change_slackhook
        extra_args = [instance]
    elif instance.type == HistoryType.delete:
        task = tasks.delete_slackhook
        extra_args = []

    for slackhook in slackhooks:
        args = [slackhook["url"], obj] + extra_args

        if settings.CELERY_ENABLED:
            task.delay(*args)
        else:
            task(*args)
