# No shebang line, this module is meant to be imported
#
# Copyright 2013 Oliver Palmer
# Copyright 2014 Ambient Entertainment GmbH & Co. KG
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Software
========

Objects and classes for working with the software models.
"""

from pyfarm.master.admin.baseview import SQLModelView
from pyfarm.master.application import SessionMixin
from pyfarm.models.software import Software


class SoftwareView(SessionMixin, SQLModelView):
    model = Software
    access_roles = ("admin.db.work.software", )
