from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    phone_2 = fields.Char(string="Teléfono 2")
    phone_3 = fields.Char(string="Teléfono 3")
