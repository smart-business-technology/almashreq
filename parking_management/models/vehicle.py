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

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class VehicleType(models.Model):
    _name = "vehicle.type"
    _inherit = ['mail.thread']
    _description = "Vehicle Type"

    name = fields.Char(string="Name", required=True, track_visibility="True")
    sequence = fields.Integer(string='Sequence')
    active = fields.Boolean(default=True)
    create_uid = fields.Many2one('res.users', 'Created by', index=True, readonly=True,track_visibility="True")
    create_date = fields.Datetime('Created on', index=True, readonly=True,track_visibility="True")
    description = fields.Text("Description", track_visibility="True")

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Vehicle Type must be unique !'),
    ]

class ParkingPricing(models.Model):
    _name = "parking.pricing"
    _inherit = ['mail.thread']
    _description = "Parking Pricing"

    def get_name(self):
        for obj in self:
            if obj.floor_ids and obj.vehicle_type and obj.duration_type:
                obj.name = obj.floor_ids[0].name+'/'+obj.vehicle_type.name +' @ '+ str(obj.fixed_price) + '/' + str(obj.fixed_duration) +' '+ obj.duration_type

    def current_capacity(self):
        for record in self:
            count = 0
            for obj in record.zones:
                for sl in obj.slots:
                    if sl.status == 'available':
                        count += 1
            record.available_slots = count

    def check_price_negative(self, vals):
        if vals.get('fixed_price') and vals.get('fixed_price') <0 or vals.get('additional_price') and vals.get('additional_price') <0 or vals.get('fixed_duration') and vals.get('fixed_duration') <0 or vals.get('additional_duration') and vals.get('additional_duration')<0:
            raise UserError(_("Price Amount or Duration can't be negative."))

    @api.model
    def create(self, vals):
        res = super(ParkingPricing, self).create(vals)
        res.check_price_negative(vals)
        res.get_zones()
        return res

    def write(self, vals):
        self.check_price_negative(vals)
        return super(ParkingPricing, self).write(vals)

    @api.onchange('floor_ids')
    def get_zones(self):
        self.zones = False
        for obj in self.floor_ids:
            if obj.zones:
                self.zones += obj.zones

    def open_booking(self):
        action_vals = {
            'name': _('Bookings'),
            'domain': [('pricing', '=', self.id)],
            'view_mode': 'tree,form',
            'res_model': 'parking.booking',
            'view_id': False,
            'type': 'ir.actions.act_window',
        }
        return action_vals

    @api.onchange('duration_type')
    def get_duration_unit_type(self):
        for obj in self:
            if obj.duration_type == 'hourly':
                obj.duration_unit_type = 'Hour'
            elif obj.duration_type == 'daily':
                obj.duration_unit_type = 'Day'
            else:
                obj.duration_unit_type = 'Month'

    def _get_default_pricelist_id(self):
        return self.env['product.pricelist'].search([], limit=1)

    name = fields.Char(string="Name", compute="get_name",default=lambda self: _('New'),track_visibility="True")
    active = fields.Boolean(default=True, track_visibility="True", groups='parking_management.parking_manager')
    vehicle_type = fields.Many2one('vehicle.type',required=True, track_visibility="True")
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id, track_visibility="True", groups="base.group_multi_company")
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist', help="Pricelist for current pricing.", default=_get_default_pricelist_id)
    currency_id = fields.Many2one("res.currency", related="pricelist_id.currency_id", string="Currency")
    fixed_price = fields.Monetary('Standard Price', currency_field='currency_id', store=True,help="Fixed rate for initial duration.",track_visibility="True")
    fixed_duration = fields.Integer('Fixed duration', default=1, help="Initial duration for fixed rate.", track_visibility="True")
    duration_type = fields.Selection([('hourly','Hourly'),('daily','Daily'),('monthly','Monthly')], default="hourly", string="Duration type",required=True, track_visibility="True")
    duration_unit_type = fields.Char(compute="get_duration_unit_type", required=True,track_visibility="True", readonly=True)
    additional_price = fields.Monetary('Additional Price', currency_field='currency_id', store=True,help="Additional rate in case of extra duration.",track_visibility="True")
    additional_duration = fields.Integer('Additional duration', default=1, help="Extra duration on which additional price will be applied.",track_visibility="True")
    floor_ids = fields.Many2many('parking.floor', required=True)
    zones = fields.Many2many('parking.zone', domain="[('floor_id','in',floor_ids)]")
    available_slots = fields.Integer("Available Slots", compute="current_capacity")
    description = fields.Text("Description", track_visibility="True")

class ParkingFloor(models.Model):
    _name = "parking.floor"
    _inherit = ['mail.thread']
    _description = "Parking floor"

    def get_name(self):
        for obj in self:
                obj.name = "FL-"+str(obj.id).zfill(2)

    def action_view_slots(self):
        slots = self.mapped('slots')
        action = self.env.ref('parking_management.slot_action').read()[0]
        if len(slots) >= 1:
            action['domain'] = [('id', 'in', slots.ids)]
            action['context'] = {'group_by' : 'zone_id'}
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def get_bookings(self):
        for obj in self:
            obj.booked = 0
            obj.available = 0
            if obj.if_zones:
                for zone_id in obj.zones:
                    if zone_id.if_slots:
                        obj.booked += len(zone_id.slots.filtered(lambda obj: obj.status == 'not_available'))
                        obj.available += len(zone_id.slots.filtered(lambda obj: obj.status == 'available'))

    def get_slots(self):
        slots = []
        for zone in self.zones:
            if zone.if_slots:
                slots += zone.slots.ids
        self.slots = slots

    def get_floor_capacity(self):
        for obj in self:
            obj.floor_capacity = 0
            if obj.zones:
                obj.floor_capacity =  len(obj.zones)
                if not obj.if_zones:
                    obj.if_zones = True

    def write(self, vals):
#         if vals.get('if_zones') and not vals.get('zones'):
#             raise UserError(_("Floor capacity should be greater than zero."))
        if vals.get('if_zones') == False:
            for obj in self:
                for zone_id in obj.zones:
                    zone_id.slots.unlink()
                    zone_id.capacity = 0
                obj.zones.unlink()
                obj.floor_capacity = 0
        return super(ParkingFloor, self).write(vals)

    @api.model
    def create(self, vals):
        floor_id = super(ParkingFloor, self).create(vals)
        if not floor_id.name:
            floor_id.get_name()
        if floor_id.if_zones and not floor_id.zones:
            raise UserError(_("Floor capacity should be greater than zero."))
        return floor_id

    name = fields.Char(string="Floor", track_visibility="True")
    color = fields.Integer("Color Index", default=0)
    active = fields.Boolean(default=True, track_visibility="True")
    zones = fields.One2many('parking.zone', 'floor_id')
    slots = fields.Many2many('parking.slots', compute="get_slots")
    config_id = fields.Many2one('parking.pricing')
    description = fields.Text("Description", track_visibility="True")
    if_zones = fields.Boolean("Floor with zones?", track_visibility="True")
    floor_capacity = fields.Integer("Floor capacity",compute="get_floor_capacity", track_visibility="True")
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id, track_visibility="True")
    booked = fields.Integer(compute="get_bookings")
    available = fields.Integer(compute="get_bookings")

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Floor name must be unique !'),
    ]

class ParkingZone(models.Model):
    _name = "parking.zone"
    _inherit = ['mail.thread']
    _description = "Parking zone"

    def get_name(self):
        return str(self.floor_id.name)+"/ZN-"+str(self.id).zfill(2)

    name = fields.Char(string="Zone",track_visibility="True")
    active = fields.Boolean(default=True, track_visibility="True")
    capacity = fields.Integer("Zone capacity",track_visibility="True")
    floor_id = fields.Many2one('parking.floor')
    slots = fields.One2many('parking.slots', 'zone_id')
    description = fields.Text("Description", track_visibility="True")
    if_slots = fields.Boolean("Zone with slots?", track_visibility="True", required=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id, track_visibility="True")

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Zone name must be unique !'),
    ]

    def action_view_slots(self):
        slots = self.mapped('slots')
        action = self.env.ref('parking_management.slot_action').read()[0]
        if len(slots) >= 1:
            action['domain'] = [('id', 'in', slots.ids)]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def write(self, vals):
        for obj in self:
            if vals.get('if_slots'):
                if vals.get('capacity'):
                    for seat in range(vals.get('capacity')):
                        slot_vals = {'name':obj.name+'/SL-'+str(seat+1), 'status':'available','zone_id':obj.id,'floor_id':obj.floor_id.id}
                        res = self.env['parking.slots'].sudo().create(slot_vals)
                else:
                    raise UserError(_("Zone capacity should be greater than zero."))
            elif vals.get('if_slots') == False:
                obj.slots.unlink()
                obj.capacity = 0
        return super(ParkingZone, self).write(vals)

    @api.model
    def create(self, vals):
        zone = super(ParkingZone, self).create(vals)
        if zone.capacity<0:
            raise UserError(_("Zone capacity cannot be negative."))
        if zone.if_slots and not zone.capacity:
            raise UserError(_("Zone capacity should be greater than zero."))
        if not zone.name:
            zone.name = zone.get_name()
        if zone.capacity >0 and zone.if_slots:
            for seat in range(zone.capacity):
                vals = {'name':zone.name+'/SL-'+str(seat+1), 'status':'available','zone_id':zone.id,'floor_id':zone.floor_id.id}
                res = self.env['parking.slots'].sudo().create(vals)
        return zone

class ParkingSlots(models.Model):
    _name = "parking.slots"
    _inherit = ['mail.thread']
    _description = "Parking slots"

    def block_slot(self):
        if self.status == 'not_available':
            raise UserError(_("This slot is already allotted and can't be blocked."))
        if not self.status == 'blocked':
            self.status = 'blocked'

    def unblock_slot(self):
        if self.status == 'blocked':
            self.status = 'available'
        else:
            raise UserError(_("This slot is not blocked yet."))

    name = fields.Char(string="Name", required=True)
    active = fields.Boolean(default=True)
    zone_id = fields.Many2one('parking.zone', required=True)
    floor_id = fields.Many2one('parking.floor', related="zone_id.floor_id")
    status = fields.Selection([('available','Available'),('not_available','Not Available'),('blocked','Blocked')], string="Status", default="available")
    description = fields.Text("Description", track_visibility="True")
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id,track_visibility="True")

    _sql_constraints = [
        ('name_zone_uniq', 'unique(name, zone_id)', 'Slot name must be unique !'),
    ]
