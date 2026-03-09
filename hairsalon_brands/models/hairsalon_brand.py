from odoo import api, fields, models

class HairsalonBrand(models.Model):
    _name = 'hairsalon.brand'
    _description = 'Hairsalon Brand'

    name = fields.Char(string='Brand Name', required=True, translate=True)
    line_ids = fields.One2many(
        'hairsalon.brand.line', 
        'brand_id', 
        string='Brand Lines'
    )
