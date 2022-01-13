# -*- coding: utf-8 -*-

from odoo import models, fields, api
import random


class iq_Inherit_PAYMENT(models.Model):
    _inherit = 'account.payment'
    
    
    iq_card_id = fields.Many2one('iq.partner.card',string="Partner Parking Card", readonly=False)
    
    iq_vech_no= fields.Char(string="Vehicle Number", readonly=True)
    iq_vech_details= fields.Char(string="Vehicle Details", readonly=True)
    iq_pricing= fields.Many2one('iq.park.pricing',string="Parking Pricing", readonly=True)
    iq_partner_balance = fields.Monetary(related='partner_id.credit' , string='Partner Balance',)
    iq_partner_barcode = fields.Char(related='partner_id.iq_barcode' , string='Partner Barcode')
    iq_partner_balance_before = fields.Monetary( string='Total Amount')
    
    
    @api.onchange('iq_card_id')
    def get_parking_details(self):
      #  self.iq_partner_balance_before = self.iq_partner_balance -( self.amount*-1)
      
            
        self.iq_vech_no = self.iq_card_id.iq_vech_no
        self.iq_vech_details = self.iq_card_id.iq_vech_details
        self.iq_pricing = self.iq_card_id.iq_pricing
        self.partner_id = self.iq_card_id.iq_partner
        


class iq_Inherit_partner(models.Model):
    _inherit = 'res.partner'
    
    iq_barcode = fields.Char(string='Partner Barcode')
    
    
    @api.model
    def create(self, vals):
        rec = super(iq_Inherit_partner,self).create(vals)
        code =(random.randrange(1111111111111,9999999999999))

        partner_barcode = self.env['barcode.nomenclature'].sanitize_ean("%s" % (code))
        rec.write({'iq_barcode':partner_barcode})
        return rec
    
    
    _sql_constraints = [
        ('name_uniq', 'unique (iq_barcode)', "Barcode already exists !"),
    ]

        
                
                

