from odoo import models, fields, api,_, SUPERUSER_ID

class FPartnerCardpaywizard(models.TransientModel):
    _name = 'iq.pay.card'
    _description = 'Payment Card'
    
    
    iq_journal= fields.Many2one('account.journal',string="Journal")
    iq_amount= fields.Float(string="Amount")
    iq_partner= fields.Many2one('res.partner',string="Partner", readonly=True)
    iq_card_id = fields.Many2one('iq.partner.card',string="Partner Parking Card", readonly=True)
    
    
    
    def generate_pay(self):
        print("11111111222222")
        vals = {
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'amount': self.iq_amount,
            'currency_id': self.env.company.currency_id.id,
            'journal_id': self.iq_journal.id,
            'company_id': self.env.company.id,
            'partner_id': self.iq_partner.id,
            'iq_card_id': self.iq_card_id.id,
            'iq_vech_no':self.iq_card_id.iq_vech_no,
            'iq_vech_details':self.iq_card_id.iq_vech_details,
            'iq_pricing':self.iq_card_id.iq_pricing.id,
        }
        payment = self.env['account.payment'].create(vals)
        payment.action_post()
    
    