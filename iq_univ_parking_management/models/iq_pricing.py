from odoo import models, fields, api

class FPricingCard(models.Model):
    _name = 'iq.park.pricing'
    _description = 'Parking Pricing'
    _rec_name = 'iq_pricing_name'
    
    iq_pricing_name= fields.Char(string="Name")
    iq_pricing_amount= fields.Float(string="Amount")
    
    
    