from odoo import api, fields, models

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    brand_id = fields.Many2one(
        'hairsalon.brand', 
        string='Brand'
    )
    brand_line_id = fields.Many2one(
        'hairsalon.brand.line', 
        string='Brand Line',
        domain="[('brand_id', '=', brand_id)]"
    )
