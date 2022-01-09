from odoo import models, fields, api,_, SUPERUSER_ID

class FPartnerCard(models.Model):
    _name = 'iq.partner.card'
    _description = 'Partners Card'
    _rec_name = 'iq_partner'
    
    def _get_company_currency(self):
        self.iq_currency_id = self.env.company.currency_id
    
    
    iq_partner= fields.Many2one('res.partner',string="Partner")
    iq_vech_no= fields.Char(string="Vehicle Number")
    iq_vech_details= fields.Char(string="Vehicle Details")
    iq_pricing= fields.Many2one('iq.park.pricing',string="Parking Pricing")
    iq_currency_id = fields.Many2one('res.currency', compute='_get_company_currency', readonly=True,
        string="Currency", help='Utility field to express amount currency')
    iq_partner_balance = fields.Monetary(related='iq_partner.credit' , string='Total Balance',currency_field='iq_currency_id')
    iq_partner_barcode = fields.Char(related='iq_partner.iq_barcode' , string='Partner Barcode')
    
    
    
    
    
    def iq_register_payment(self):
        
        print("1111111111111111")
        
        
        
        form_id = self.env.ref('iq_univ_parking_management.iq_pay_card_form').id
        ctx = {'default_iq_partner': self.iq_partner.id,'default_iq_card_id': self.id,}
        action = {
             'name':_('Payment'),
             'type': 'ir.actions.act_window',
             'view_mode': 'form',
             'res_model': 'iq.pay.card',
             'context' : ctx,
            'target':'new'
              
             }
           
        return action
        

        
        
    def open_payment(self):
        print("22222222222222222222")
        tree_id = self.env.ref('account.view_account_payment_tree').id
        form_id = self.env.ref('account.view_account_payment_form').id
        ctx = {'default_iq_card_id': self.id}
        action = {
             'name':_('Payment'),
             'type': 'ir.actions.act_window',
             'view_mode': 'tree,form',
             'res_model': 'account.payment',
              'domain':[('iq_card_id', '=', self.id)],
              'target':'current'
             
             }
          
        return action
    
    
