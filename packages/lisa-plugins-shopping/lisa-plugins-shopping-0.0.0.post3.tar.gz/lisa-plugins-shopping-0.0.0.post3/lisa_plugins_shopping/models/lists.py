# -*- coding: utf-8 -*-

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from lisa_api import db


# Define models
class ListItem(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    item = db.Column(db.String(80), unique=True)
    checked = db.Column(db.Boolean())

    def __repr__(self):
        return '<ListItem %r>' % self.id
