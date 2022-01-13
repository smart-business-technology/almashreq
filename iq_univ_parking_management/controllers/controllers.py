# -*- coding: utf-8 -*-
# from odoo import http


# class IqUnivParkingManagement(http.Controller):
#     @http.route('/iq_univ_parking_management/iq_univ_parking_management/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/iq_univ_parking_management/iq_univ_parking_management/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('iq_univ_parking_management.listing', {
#             'root': '/iq_univ_parking_management/iq_univ_parking_management',
#             'objects': http.request.env['iq_univ_parking_management.iq_univ_parking_management'].search([]),
#         })

#     @http.route('/iq_univ_parking_management/iq_univ_parking_management/objects/<model("iq_univ_parking_management.iq_univ_parking_management"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('iq_univ_parking_management.object', {
#             'object': obj
#         })
