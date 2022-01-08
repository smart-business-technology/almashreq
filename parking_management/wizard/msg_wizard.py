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

class MessageWizard(models.TransientModel):
    _name = "message.wizard"
    _description = "Message wizard"

    message = fields.Char()

    def show_message(self, message, name='Message/Summary'):
        wizard_id = self.create({'message': message})
        return {
            'name': name,
            'view_mode': 'form',
            'view_id': False,
            'res_model': 'message.wizard',
            'res_id': wizard_id.id,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
        }
