# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
  "name"                 :  "Odoo Parking Management",
  "summary"              :  """Odoo Parking Management""",
  "category"             :  "ODOO",
  "version"              :  "1.0.0",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo.html",
  "description"          :  """This module helps to manage parking system.""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=parking_management",
  "depends"              :  ['account'],
  "data"                 :  [
                             'security/parking_security.xml',
                             'security/ir.model.access.csv',
                             'wizard/msg_wizard_view.xml',
                             'wizard/creat_slot_view.xml',
                             'views/vehicle_view.xml',
                             'report/receipt_template.xml',
                             'report/parking_receipt.xml',
                             'views/dashboard_view.xml',
                            ],
  "demo"                 :  ['data/demo.xml'],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  99,
  "currency"             :  "USD",
  #"pre_init_hook"        :  "pre_init_check",
}
