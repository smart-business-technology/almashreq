# -*- coding: utf-8 -*-

from odoo import models, fields, api


class partner_badge(models.Model):
    _inherit = 'res.partner'


    barcode = fields.Char(string="Barcode", required=False, )

