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

import json

from taiga.base import filters
from taiga.base import response
from taiga.base.api import ModelCrudViewSet, ModelListViewSet
from taiga.base.api.utils import get_object_or_404
from taiga.base.decorators import detail_route

from . import models
from . import serializers
from . import permissions
from . import tasks


class HallHookViewSet(ModelCrudViewSet):
    model = models.HallHook
    serializer_class = serializers.HallHookSerializer
    permission_classes = (permissions.HallHookPermission,)
    filter_backends = (filters.IsProjectAdminFilterBackend,)
    filter_fields = ("project",)

    @detail_route(methods=["POST"])
    def test(self, request, pk=None):
        hallhook = self.get_object()
        self.check_permissions(request, 'test', hallhook)

        tasks.test_hallhook(hallhook.url)

        return response.NoContent()
