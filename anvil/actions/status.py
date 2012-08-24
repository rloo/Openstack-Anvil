# vim: tabstop=4 shiftwidth=4 softtabstop=4

#    Copyright (C) 2012 Yahoo! Inc. All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from anvil import action
from anvil import colorizer
from anvil import log
from anvil import utils

from anvil.action import PhaseFunctors

LOG = log.getLogger(__name__)

from anvil.components import (STATUS_INSTALLED, STATUS_STARTED,
                              STATUS_STOPPED, STATUS_UNKNOWN)


class StatusAction(action.Action):
    def __init__(self, name, distro, root_dir, **kwargs):
        action.Action.__init__(self, name, distro, root_dir, **kwargs)
        self.show_amount = kwargs.get('show_amount')

    @property
    def lookup_name(self):
        return 'running'

    def _fetch_status(self, component):
        return component.status()

    def _quote_status(self, status):
        if status == STATUS_UNKNOWN:
            return colorizer.quote(status, quote_color='yellow')
        elif status == STATUS_STARTED or status == STATUS_INSTALLED:
            return colorizer.quote(status, quote_color='green')
        else:
            return colorizer.quote(status, quote_color='red')

    def _print_status(self, component, result):
        if not result:
            LOG.info("Status of %s is %s.", colorizer.quote(component.name), self._quote_status(STATUS_UNKNOWN))
            return

        def details_printer(entry, spacing, max_len):
            det = utils.truncate_text(entry.details, max_len=max_len, from_bottom=True)
            for line in det.splitlines():
                line = line.replace("\t", "\\t")
                line = line.replace("\r", "\\r")
                line = utils.truncate_text(line, max_len=120)
                LOG.info("%s>> %s", (" " * spacing), line)

        if len(result) == 1:
            s = result[0]
            if s.name and s.name != component.name:
                LOG.info("Status of %s (%s) is %s.", colorizer.quote(component.name), s.name, self._quote_status(s.status))
            else:
                LOG.info("Status of %s is %s.", colorizer.quote(component.name), self._quote_status(s.status))
            if self.show_amount > 0 and s.details:
                details_printer(s, 2, self.show_amount)
        else:
            LOG.info("Status of %s is:", colorizer.quote(component.name))
            for s in result:
                LOG.info("|-- %s is %s.", s.name, self._quote_status(s.status))
                if self.show_amount > 0 and s.details:
                    details_printer(s, 4, self.show_amount)

    def _run(self, persona, component_order, instances):
        self._run_phase(
            PhaseFunctors(
                start=None,
                run=self._fetch_status,
                end=self._print_status,
            ),
            component_order,
            instances,
            None,
            )
