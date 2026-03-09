from odoo import _, fields, models

import logging

_logger = logging.getLogger(__name__)


class HairsalonBrandMigrateWizard(models.TransientModel):
    _name = 'hairsalon.brand.migrate.wizard'
    _description = 'Migrate Brand Fields from x_marca_id/x_linea_id to brand_id/brand_line_id'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
    ], default='draft', string='State')
    brand_count = fields.Integer(string='Brands Created', readonly=True)
    line_count = fields.Integer(string='Lines Created', readonly=True)
    product_count = fields.Integer(string='Products Updated', readonly=True)

    def action_migrate_brands(self):
        self.ensure_one()

        Brand = self.env['hairsalon.brand']
        BrandLine = self.env['hairsalon.brand.line']
        Product = self.env['product.template']
        XMarca = self.env['x_marca']
        XLinea = self.env['x_linea']

        # Step 1: Get ALL x_marca records
        x_marca_records = XMarca.search([])

        # Step 2: Create hairsalon.brand for each x_marca (if not already exists)
        marca_map = {}  # x_marca.id -> hairsalon.brand record
        brand_created = 0
        for x_marca in x_marca_records:
            existing = Brand.search([('name', '=', x_marca.x_name)], limit=1)
            if existing:
                marca_map[x_marca.id] = existing
            else:
                new_brand = Brand.create({'name': x_marca.x_name})
                marca_map[x_marca.id] = new_brand
                brand_created += 1

        # Step 3: Get ALL x_linea records
        x_linea_records = XLinea.search([])

        # Step 4: Create hairsalon.brand.line for each x_linea (if not already exists)
        linea_map = {}  # x_linea.id -> hairsalon.brand.line record
        line_created = 0
        for x_linea in x_linea_records:
            # Get the corresponding brand from the marca_map
            brand = False
            if x_linea.x_marca_cod and x_linea.x_marca_cod.id in marca_map:
                brand = marca_map[x_linea.x_marca_cod.id]

            if brand:
                existing = BrandLine.search([
                    ('name', '=', x_linea.x_name),
                    ('brand_id', '=', brand.id),
                ], limit=1)
                if existing:
                    linea_map[x_linea.id] = existing
                else:
                    new_line = BrandLine.create({
                        'name': x_linea.x_name,
                        'brand_id': brand.id,
                    })
                    linea_map[x_linea.id] = new_line
                    line_created += 1
            else:
                _logger.warning(
                    'Skipping x_linea %s (id=%s): no matching brand found.',
                    x_linea.x_name, x_linea.id,
                )

        # Step 5: Update all products with the new brand_id / brand_line_id
        product_updated = 0
        all_products = Product.search([
            '|',
            ('x_marca_id', '!=', False),
            ('x_linea_id', '!=', False),
        ])
        for product in all_products:
            vals = {}
            if product.x_marca_id and product.x_marca_id.id in marca_map:
                vals['brand_id'] = marca_map[product.x_marca_id.id].id
            if product.x_linea_id and product.x_linea_id.id in linea_map:
                vals['brand_line_id'] = linea_map[product.x_linea_id.id].id
            if vals:
                product.write(vals)
                product_updated += 1

        _logger.info(
            'Hairsalon Brand Migration: %d brands created, %d lines created, %d products updated.',
            brand_created, line_created, product_updated,
        )

        self.write({
            'brand_count': brand_created,
            'line_count': line_created,
            'product_count': product_updated,
            'state': 'done',
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
