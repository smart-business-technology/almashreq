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

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError

class Slot(models.TransientModel):
    _name = "slot.slot"
    _description = "Create slot wizard"

    zone_id = fields.Many2one('parking.zone', required=True)
    capacity = fields.Integer('Zone Capacity', required=True)

    def create_slots(self):
        msg = ''
        if self.capacity <= 0:
            raise UserError(_("New zone capacity can't be less than or equal to zero."))
        slot_ids = self.env['parking.slots'].search_count([('zone_id','=',self.zone_id.id)])
        for seat in range(self.capacity):
            vals = {'name':self.zone_id.name+'/SL-'+str(slot_ids+seat+1), 'status':'available','zone_id':self.zone_id.id}
            res = self.env['parking.slots'].sudo().create(vals)
            msg += "Slot <b>%s</b> has been created.<br/>"%(res.name)
        self.zone_id.capacity += self.capacity
        msg += "Updated capacity for Zone <b>"+ self.zone_id.name + " </b> is: "+ str(self.zone_id.capacity)
        return self.env['message.wizard'].show_message(msg)
