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

from lisa_api import db, api, core
from flask.ext.restplus import Resource, fields
from lisa_api.models.users.user import user_datastore
from lisa_api.lib.login import login_api
from lisa_plugins_shopping.models.lists import ListItem

ListItem_api = api.model('ListItem', {
    'id': fields.Integer(required=False, description='The id of the item'),
    'item': fields.String(required=True, description='Item name (must be unique)'),
    'checked': fields.Boolean(required=False, description='Check item')
})


ListItem_parser = api.parser()
ListItem_parser.add_argument('item', type=str, required=True,
                             help='Item name (must be unique)', location='form')
ListItem_parser.add_argument('checked', type=bool, required=False,
                             help='Check item', location='form')


@core.route('/shoppinglist/<string:item>')
@api.doc(params={'item': 'The item name'})
@api.response(404, 'Item not found')
@api.response(401, 'Unauthorized access')
class ListItemResource(Resource):
    """ Show a single role item and lets you modify or delete it """
    decorators = [login_api]

    @api.marshal_with(ListItem_api)
    def get(self, item):
        """
        This function return a single item object

        :param name: The name of the item
        :type name: str
        :returns: a item object or a 404 string + int if item not found
        :rtype: object or string + int
        """
        item = ListItem.query.filter_by(item=item).first()
        if item is None:
            api.abort(404, 'Item not found')
        return item

    @api.response(204, 'Item deleted')
    def delete(self, item):
        """
        This function delete the given item object

        :param name: The name of the item
        :type name: str
        :returns: a 204 string + int or a 404 string + int if item is not found
        :rtype: string + int
        """
        item = ListItem.query.filter_by(item=item).first()
        if item is None:
            api.abort(404, 'Item not found')
        db.session.delete(item)
        db.session.commit()
        return 'Item has been deleted', 204

    @api.doc('update_item', parser=ListItem_parser)
    @api.marshal_with(ListItem_api, description="Item updated")
    def put(self, item):
        """
        This function modify a item object

        :param name: The name of the item
        :type name: str
        :returns: a 200 string + int or a 404 string + int if item is not found
        :rtype: string + int
        """
        args = ListItem_parser.parse_args()
        item = ListItem.query.filter_by(item=item).first()
        if item is None:
            api.abort(404, 'Item not found')
        item.name = args['item']
        item.checked = args['checked']
        db.session.commit()
        return item


@core.route('/shoppinglist')
@api.response(404, 'Item not found')
@api.response(401, 'Unauthorized access')
class ListItemListResource(Resource):
    """ This class return all items and is also responsible to handle the
     creation of an item """
    decorators = [login_api]

    @api.marshal_list_with(ListItem_api, description="Item list")
    def get(self):
        """
        This function return all item objects

        :return: a list of role objects
        :rtype: list of role objects
        """
        return ListItem.query.all()

    @api.doc('create_item', parser=ListItem_parser)
    @api.marshal_with(ListItem_api, code=201, description="Item added")
    def post(self):
        """
        This function create a role object

        :returns: a 201 string + int
        :rtype: string + int
        """
        args = ListItem_parser.parse_args()
        role = user_datastore.find_or_create_role(name=args['name'],
                                                  description=args['description'])
        db.session.commit()
        return role, 201
