from odoo import fields, models

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    consumo_interno = fields.Boolean(
        string='Consumo interno',
        help='Si está marcado, este producto se puede transferir al Salón como consumo interno.',
        default=False,
    )
