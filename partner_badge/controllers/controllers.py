# -*- coding: utf-8 -*-
# from odoo import http


# class PartnerBadge(http.Controller):
#     @http.route('/partner_badge/partner_badge/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/partner_badge/partner_badge/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('partner_badge.listing', {
#             'root': '/partner_badge/partner_badge',
#             'objects': http.request.env['partner_badge.partner_badge'].search([]),
#         })

#     @http.route('/partner_badge/partner_badge/objects/<model("partner_badge.partner_badge"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('partner_badge.object', {
#             'object': obj
#         })
