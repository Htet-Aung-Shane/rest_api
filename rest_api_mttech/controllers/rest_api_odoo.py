# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Sruthi Pavithran (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
import json
import logging
from datetime import datetime

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class RestApi(http.Controller):
    """This is a controller which is used to generate responses based on the
    api requests"""

    def auth_api_key(self, api_key):
        """This function is used to authenticate the api-key when sending a
        request"""
        user_id = request.env["res.users"].sudo().search([("api_key", "=", api_key)])
        if api_key is not None and user_id:
            response = True
        elif not user_id:
            response = "<html><body><h2>Invalid <i>API Key</i> " "!</h2></body></html>"
        else:
            response = (
                "<html><body><h2>No <i>API Key</i> Provided " "!</h2></body></html>"
            )
        return response

    def generate_response(self, method, model, rec_id, fields,values):
        """This function is used to generate the response based on the type
        of request and the parameters given"""

        option = (
            request.env["connection.api"]
            .sudo()
            .search([("model_id", "=", model)], limit=1)
        )
        model_name = option.model_id.model
        if method != "DELETE":
            if fields:
                data = fields
                print("Result Fieldsssssssssssss", data)
            else:
                data = []
        else:
            data = []
        if not data and method != "DELETE":
            return (
                "<html><body><h2>No fields selected for the model" "</h2></body></html>"
            )
        if not option:
            return (
                "<html><body><h2>No Record Created for the model" "</h2></body></html>"
            )
        try:
            if method == "GET":
                filter_fields = []
                if fields:
                    filter_fields = json.loads(fields)
                
                if not option.is_get:
                    return "<html><body><h2>Method Not Allowed" "</h2></body></html>"
                else:
                    datas = []
                    if rec_id != 0:
                        partner_records = (
                            request.env[str(model_name)]
                            .sudo()
                            .search_read(
                                domain=[("id", "=", rec_id)], fields=filter_fields
                            )
                        )
                        # Manually convert datetime fields to string format
                        for record in partner_records:
                            for key, value in record.items():
                                if isinstance(value, datetime):
                                    record[key] = value.isoformat()
                        data = json.dumps({"records": partner_records})
                        datas.append(data)
                        return request.make_response(data=datas)
                    else:
                        if partner_records:
                            partner_records = (
                                request.env[str(model_name)]
                                .sudo()
                                .search_read(domain=[], fields=filter_fields)
                            )

                            # Manually convert datetime fields to string format
                            for record in partner_records:
                                for key, value in record.items():
                                    if isinstance(value, datetime):
                                        record[key] = value.isoformat()

                            data = json.dumps({"records": partner_records})
                            datas.append(data)
                            return request.make_response(data=datas)
                        else:
                            return 'Record does not exist'
        except:
            return "<html><body><h2>Invalid JSON Data" "</h2></body></html>"
        if method == "POST":
            datas = []
            if not option.is_post:
                return "<html><body><h2>Method Not Allowed" "</h2></body></html>"
            else:
                try:
                    # attr_values = json.load(values)
                    create_fields = json.loads(fields)
                    create_values = json.loads(values)
                    data_dict = dict(zip(create_fields, create_values))
                    new_resource = request.env[str(model_name)].sudo().create(data_dict)
                    partner_records = request.env[str(model_name)].sudo().search_read(
                        domain=[("id", "=", new_resource.id)], fields=create_fields
                    )
                    for record in partner_records:
                        for key, value in record.items():
                            if isinstance(value, datetime):
                                record[key] = value.isoformat()
                    
                    data = json.dumps({"New Record": partner_records})
                    datas.append(data)
                    return request.make_response(data=datas)
                except:
                    return "<html><body><h2>Invalid JSON Data" "</h2></body></html>"
        if method == "PUT":
            if not option.is_put:
                return "<html><body><h2>Method Not Allowed" "</h2></body></html>"
            else:
                if rec_id == 0:
                    return "<html><body><h2>No ID Provided" "</h2></body></html>"
                else:
                    resource = request.env[str(model_name)].sudo().browse(int(rec_id))
                    if not resource.exists():
                        return (
                            "<html><body><h2>Resource not found" "</h2></body></html>"
                        )
                    else:
                        try:
                            datas = []
                            create_fields = json.loads(fields)
                            create_values = json.loads(values)
                            data_dict = dict(zip(create_fields, create_values))
                            resource.sudo().write(data_dict)
                            partner_records = request.env[str(model_name)].sudo().search_read(
                                domain=[("id", "=", resource.id)], fields=create_fields
                            )
                            new_data = json.dumps(
                                {
                                    "Updated resource": partner_records,
                                }
                            )
                            datas.append(new_data)
                            return request.make_response(data=datas)

                        except:
                            return (
                                "<html><body><h2>Invalid JSON Data "
                                "!</h2></body></html>"
                            )
        if method == "DELETE":
            if not option.is_delete:
                return "<html><body><h2>Method Not Allowed" "</h2></body></html>"
            else:
                if rec_id == 0:
                    return "<html><body><h2>No ID Provided" "</h2></body></html>"
                else:
                    resource = request.env[str(model_name)].sudo().browse(int(rec_id))
                    if not resource.exists():
                        return (
                            "<html><body><h2>Resource not found" "</h2></body></html>"
                        )
                    else:
                        records = request.env[str(model_name)].sudo().search_read(
                            domain=[("id", "=", resource.id)],
                            fields=["id", "name"],
                        )
                        if records:
                            remove = json.dumps(
                                {
                                    "Resource deleted": records,
                                }
                            )
                            resource.unlink()
                            return request.make_response(data=remove)
                        else:
                            return "Record Does Not Exist!"

    @http.route(
        ["/send_request"],
        type="http",
        auth="none",
        methods=["GET", "POST", "PUT", "DELETE"],
        csrf=False,
    )
    def fetch_data(self, **kw):
        """This controller will be called when sending a request to the
        specified url, and it will authenticate the api-key and then will
        generate the result"""
        http_method = request.httprequest.method
        api_key = request.httprequest.headers.get("token")
        model = kw.get("model")
        user = (
            request.env["res.users"].sudo().search([("api_key", "=", api_key)], limit=1)
        )
        if user:
            model_id = request.env["ir.model"].sudo().search([("model", "=", model)])
            if not model_id:
                return (
                    "<html><body><h3>Invalid model, check spelling or maybe "
                    "the related "
                    "module is not installed"
                    "</h3></body></html>"
                )
            if not kw.get("id"):
                rec_id = 0
            else:
                rec_id = int(kw.get("id"))
            fields = kw.get("fields", [])
            values = kw.get("values", [])
            result = self.generate_response(http_method, model_id.id, rec_id, fields, values)
            return result
        else:
            return "Token Key Not Valid"

    @http.route(
        ["/odoo_connect"], type="http", auth="none", csrf=False, methods=["GET"]
    )
    def odoo_connect(self, **kw):
        """This is the controller which initializes the api transaction by
        generating the api-key for specific user and database"""

        username = request.httprequest.headers.get("login")
        password = request.httprequest.headers.get("password")
        db = request.httprequest.headers.get("db")

        try:
            request.session.update(http.get_default_session(), db=db)
            credential = {"login": username, "password": password, "type": "password"}
            auth = request.session.authenticate(request.db, credential)
            user = request.env["res.users"].browse(auth)
            api_key = request.env.user.generate_api(username)
            data = json.dumps({"Status": "auth successful", "api-key": api_key})
            headers = [("Content-Type", "application/json")]
            return request.make_response(data, headers=headers)
        except:
            return "<html><body><h2>wrong login credentials" "</h2></body></html>"
