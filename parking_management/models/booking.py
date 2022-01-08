# -*- coding: utf-8 -*-
##########################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2016-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# License URL :<https://store.webkul.com/license.html/>
##########################################################################

import math
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class ParkingBooking(models.Model):
    _name = "parking.booking"
    _inherit = ['mail.thread']
    _description = "Parking"
    _order = "create_date desc"

    @api.onchange('check_out')
    def onchange_checkout(self):
        for obj in self:
            if obj.check_out:
                obj.duration = obj.get_duration()
                obj.total_amount = obj.get_price()
            else:
                obj.duration = 0
                obj.total_amount = 0.0

    def get_checkout(self):
        self.ensure_one()
        view_id = self.env.ref('parking_management.booking_form_wizard')
        return {
            'name': "Release",
            'view_mode': 'form',
            'view_id': view_id.id,
            'res_model': 'parking.booking',
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def get_duration(self):
        if self.check_in and self.check_out:
            if self.check_out < self.check_in:
                raise UserError(_("Check-Out time can't be less than Check-In time."))
            diff = self.check_out - self.check_in
            days, seconds = diff.days, diff.seconds
            if self.pricing.duration_type == 'daily':
                return days
            elif self.pricing.duration_type == 'monthly':
                return (self.check_out.year - self.check_in.year) * 12 + (self.check_out.month - self.check_in.month)
            else:
                return math.ceil( days * 24 + seconds / 3600)

    def release_parking(self):
        if self.state == 'allotted':
            self.state = 'released'
            self.slot_id.sudo().write({'status':'available'})
        self.advance_amount += self.balance
        return self.env['message.wizard'].show_message("<h4>Payment done for Booking ID: "+self.name+"</h4>")

    @api.onchange('pricing')
    def onchange_pricing(self):
        self.ensure_one()
        self.get_duration_unit()
        if self.check_out:
            self.onchange_checkout()
        floor_ids = self.get_floor()
        zone_ids = self.get_zones()
        self.floor_id = floor_ids[0] if floor_ids else False
        self.zone_id = zone_ids[0] if zone_ids else False
        slot_ids = self.get_slots()
        self.slot_id = slot_ids[0] if slot_ids else False
        self.pricelist_id = self.pricing.pricelist_id
        return {"domain":{'floor_id':[('id', 'in', floor_ids)],'zone_id':[('id', 'in', zone_ids)], 'slot_id':[('id', 'in', slot_ids)]}}

    def get_pricing(self):
        available_slots = []
        if self.vehicle_type:
            config_ids = self.env['parking.pricing'].search([('vehicle_type','=', self.vehicle_type.id)])
            for obj in config_ids:
                if obj.available_slots > 0:
                    available_slots.append(obj.id)
        return available_slots

    def get_floor(self):
        if self.company_id:
            return self.pricing.floor_ids.filtered(lambda obj : obj.company_id == self.company_id and obj.active == True).ids if self.pricing else []
        else:
            return self.pricing.floor_ids.ids if self.pricing else []

    def get_zones(self):
        if self.company_id:
            return self.pricing.zones.filtered(lambda obj : obj.company_id == self.company_id and obj.active == True).ids if self.pricing else []
        else:
            return self.pricing.zones.ids if self.pricing else []

    def get_slots(self):
        slots = []
        if self.zone_id:
            for obj in self.zone_id.slots:
                if self.company_id:
                    if obj.status == 'available' and obj.company_id == self.company_id:
                        slots.append(obj.id)
                else:
                    if obj.status == 'available':
                        slots.append(obj.id)
        return slots

    def get_price(self):
        if self.pricing:
            fixed_hours = self.pricing.fixed_duration
            additional_hours = self.pricing.additional_duration
            if self.duration <= self.pricing.fixed_duration:
                return self.pricing.fixed_price
            else:
                extra_hours = self.duration - self.pricing.fixed_duration
                if additional_hours > 0:
                    return self.pricing.fixed_price + (math.ceil(extra_hours / additional_hours)  * self.pricing.additional_price)
        else:
            return 0.0

    @api.depends('total_amount','advance_amount')
    def get_balance(self):
        for obj in self:
            obj.balance = obj.total_amount - obj.advance_amount

    @api.onchange('advance_amount')
    def onchange_advance_amount(self):
        self.ensure_one()
        if self.advance_amount <0 :
            raise UserError(_("Amount paid can't be negative."))
        if self.advance_amount and not self.check_out:
            raise UserError(_("Please enter Check-Out time first."))
        if self.advance_amount > self.total_amount:
            raise UserError(_("Advance payment can't be greater than Total amount to be paid."))

    def get_duration_unit(self):
        for obj in self:
            if obj.pricing:
                if obj.pricing.duration_type == 'hourly':
                    obj.duration_unit = 'Hour' if obj.duration <=1 else "Hours"
                elif obj.pricing.duration_type == 'daily':
                    obj.duration_unit = 'Day' if obj.duration <=1 else "Days"
                else:
                    obj.duration_unit = 'Month' if obj.duration <=1 else "Months"
            else:
                obj.duration_unit = ''

    @api.onchange('vehicle_type','pricelist_id','company_id')
    def get_pricing_domain(self):
        self.ensure_one()
        self.pricing = False
        domain = [('vehicle_type','=', self.vehicle_type.id)]
        if self.pricelist_id:
            domain += [('pricelist_id', '=', self.pricelist_id.id)]
        if self.company_id:
            domain += [('company_id', '=', self.company_id.id)]
        pricing_ids =  self.env['parking.pricing'].search(domain)
        if pricing_ids:
            self.pricing = pricing_ids[0]
        return {'domain': {'pricing': domain}}

    @api.onchange('customer')
    def onchange_customer(self):
        if self.customer:
            self.customer_name = self.customer.name

    name = fields.Char(string="Booking No.", default=lambda self: _('New'))
    active = fields.Boolean(default=True, groups='parking_management.parking_manager')
    vehicle_type = fields.Many2one('vehicle.type', track_visibility='onchange', ondelete='restrict', required=True, readonly=True, states={'new': [('readonly', False)]})
    state = fields.Selection([('new','New'),('allotted','Allotted'),('released','Released'),('invoiced','Invoiced')], string="Stages", default="new", required=True, track_visibility='onchange')
    check_in = fields.Datetime('Check In', default=lambda self: fields.Datetime.now(), track_visibility='onchange', required='1')
    check_out = fields.Datetime('Check Out', track_visibility='onchange')
    customer = fields.Many2one('res.partner', track_visibility='onchange', ondelete='restrict')
    customer_name = fields.Char("Customer Name", required=True,track_visibility='onchange', states={'new': [('readonly', False)]}, readonly=True)
    vehicle_no = fields.Char('Vehicle No.', track_visibility='onchange', required=True, readonly=True, states={'new': [('readonly', False)]})
    floor_id = fields.Many2one('parking.floor', ondelete='restrict', domain=lambda self: [('id', 'in', self.get_floor())], readonly=True, states={'new': [('readonly', False)]})
    zone_id = fields.Many2one('parking.zone', ondelete='restrict', domain="[('floor_id','=', floor_id)]", readonly=True, states={'new': [('readonly', False)]})
    slot_id = fields.Many2one('parking.slots', ondelete='restrict', domain="[('zone_id','=', zone_id),('status','=','available')]", readonly=True, states={'new': [('readonly', False)]})
    duration = fields.Integer('Duration', compute="onchange_checkout",track_visibility='onchange')
    duration_unit = fields.Char(compute='get_duration_unit', required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id,readonly=True, states={'new': [('readonly', False)]},track_visibility="True")
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist', help="Pricelist for current pricing.")
    currency_id = fields.Many2one("res.currency", related="pricelist_id.currency_id", string="Currency")
    advance_amount = fields.Monetary('Amount Paid', help="Advance amount paid by user", currency_field='currency_id',track_visibility='onchange')
    total_amount = fields.Monetary('Total Amount', help="Total amount to be paid", currency_field='currency_id',compute="onchange_checkout", track_visibility='onchange')
    balance = fields.Monetary('Balance', compute="get_balance", track_visibility='onchange', currency_field='currency_id', help="Balance= Total Amount - Amount Paid")
    pricing = fields.Many2one('parking.pricing', required=True, string="Pricing", ondelete='restrict', track_visibility='onchange', domain="[('vehicle_type','=', vehicle_type)]", readonly=True, states={'new': [('readonly', False)]})
    invoice_id = fields.Many2one('account.move',ondelete='restrict')
    description = fields.Text("Description", track_visibility="True")

    def book_now(self):
        if self.zone_id and self.zone_id.if_slots:
            if self.slot_id:
                if self.slot_id.status == 'not_available':
                    raise UserError(_("This slot is already allotted."))
                else:
                    self.slot_id.sudo().write({'status':'not_available'})
            else:
                raise UserError(_("No slot is available."))
        self.state = 'allotted'
        return True

    @api.model
    def create(self, vals):
        if self._context.get('new_booking'):
            vals['state'] = 'allotted'
        res = super(ParkingBooking, self).create(vals)
        res.name = "PK"+str(res.id).zfill(4)
        if 'floor_id' not in vals or 'pricelist_id' not in vals or res.pricing.pricelist_id != res.pricelist_id:
            res.onchange_pricing()
        return res

    def write(self, vals):
        if vals.get('advance_amount') and vals.get('advance_amount') < 0:
            raise UserError(_("Amount paid can't be negative."))
        return super(ParkingBooking, self).write(vals)

    def create_new_booking(self):
        self.ensure_one()
        view_id = self.env.ref('parking_management.booking_form_view')
        return {
            'name': "Booking",
            'view_mode': 'form',
            'view_id': view_id.id,
            'res_model': 'parking.booking',
            'res_id': self.id,
            'type': 'ir.actions.act_window',
        }

    def create_parking_invoice(self):
        partner = self.customer
        invoice = self.env['account.move'].create({
            'type': 'out_invoice',
            'partner_id': partner.id,
            'invoice_date': fields.Date.today(),
            'currency_id': self.currency_id.id,
            'invoice_line_ids': [(0, 0, {
                'name': self.name,
                'price_unit': self.total_amount,
                'quantity': 1.0,
            })],
        })

        if self.state == 'released':
            self.invoice_id = invoice.id
            self.state = 'invoiced'
            self.open_invoice()

    def open_invoice(self):
        action_vals = {
            'name': _('Invoices'),
            'domain': [('id', 'in', [self.invoice_id.id])],
            'view_type': 'form',
            'res_model': 'account.move',
            'view_id': self.env.ref('account.view_move_form').id,
            'type': 'ir.actions.act_window',
        }
        action_vals.update({'res_id': self.invoice_id.id, 'view_mode': 'form'})
        return action_vals

    def get_customer(self):
        self.ensure_one()
        if self.customer:
            return self.create_parking_invoice()
        else:
            view_id = self.env.ref('parking_management.booking_customer_wizard')
            return {
                'name': "Customer",
                'view_mode': 'form',
                'view_id': view_id.id,
                'res_model': 'parking.booking',
                'res_id': self.id,
                'type': 'ir.actions.act_window',
                'target': 'new',
            }

    def print_receipt(self):
        return self.env.ref('parking_management.parking_receipt').report_action(self)

    def unlink(self):
        for obj in self:
            if obj.state not in ('new'):
                raise UserError(_("Cannot delete booking(s) which are not in 'New' state."))
        return super(ParkingBooking, self).unlink()
