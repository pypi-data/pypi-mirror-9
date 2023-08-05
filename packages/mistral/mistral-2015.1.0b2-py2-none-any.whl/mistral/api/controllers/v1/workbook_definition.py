# -*- coding: utf-8 -*-
#
# Copyright 2013 - Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import pecan

from mistral.db.v1 import api as db_api
from mistral.openstack.common import log as logging
from mistral.services import workbooks
from mistral.utils import rest_utils


LOG = logging.getLogger(__name__)


class WorkbookDefinitionController(pecan.rest.RestController):
    @rest_utils.wrap_pecan_controller_exception
    @pecan.expose()
    def get(self, workbook_name):
        """Return the workbook definition."""
        LOG.info("Fetch workbook definition [workbook_name=%s]" %
                 workbook_name)

        return db_api.workbook_get(workbook_name).definition

    @rest_utils.wrap_pecan_controller_exception
    @pecan.expose(content_type="text/plain")
    def put(self, workbook_name):
        """Update workbook definition."""
        text = pecan.request.text

        LOG.info("Update workbook definition [workbook_name=%s, text=%s]" %
                 (workbook_name, text))

        wb = workbooks.update_workbook_v1(workbook_name, {'definition': text})

        return wb.definition
