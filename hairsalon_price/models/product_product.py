# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductProduct(models.Model):
    _inherit = 'product.product'

    list_price = fields.Float(
        'Sales Price',
        digits='Product Price',
        help="The price at which the product is sold to customers.",
    )

    def _set_product_lst_price(self):
        for product in self:
            if self.env.context.get('uom'):
                value = self.env['uom.uom'].browse(self.env.context['uom'])._compute_price(product.lst_price, product.uom_id)
            else:
                value = product.lst_price

            value -= product.price_extra
            product.write({'list_price': value})

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'list_price' not in vals and 'product_tmpl_id' in vals:
                template = self.env['product.template'].browse(vals['product_tmpl_id'])
                if template:
                    vals['list_price'] = template.list_price
        return super(ProductProduct, self).create(vals_list)

