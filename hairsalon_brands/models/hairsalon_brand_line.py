from odoo import api, fields, models

class HairsalonBrandLine(models.Model):
    _name = 'hairsalon.brand.line'
    _description = 'Hairsalon Brand Line'

    name = fields.Char(string='Line Name', required=True, translate=True)
    brand_id = fields.Many2one(
        'hairsalon.brand', 
        string='Brand', 
        required=True, 
        ondelete='cascade'
    )
