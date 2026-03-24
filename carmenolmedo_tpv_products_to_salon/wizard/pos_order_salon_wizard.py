from odoo import fields, models, api, _

class PosOrderSalonWizard(models.TransientModel):
    _name = 'pos.order.salon.wizard'
    _description = 'Wizard Transferir a Salón'

    pos_order_id = fields.Many2one('pos.order', string='Pedido', required=True, ondelete='cascade')
    line_ids = fields.One2many('pos.order.salon.wizard.line', 'wizard_id', string='Líneas')

    def action_accept(self):
        self.ensure_one()
        # Find Salon location
        salon_location = self.env.ref('carmenolmedo_tpv_products_to_salon.location_salon', raise_if_not_found=False)
        if not salon_location:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Error'),
                    'message': _('La ubicación "Salón" no existe.'),
                    'type': 'danger',
                    'sticky': False,
                }
            }
            
        # Get source location from the company's internal warehouse.
        # usually company's main warehouse stock location
        company = self.env.company
        warehouse = self.env['stock.warehouse'].search([('company_id', '=', company.id)], limit=1)
        source_location = warehouse.lot_stock_id
        if not source_location:
            source_location = self.env['stock.location'].search([('usage', '=', 'internal'), ('company_id', '=', company.id)], limit=1)

        lines_to_move = self.line_ids.filtered(lambda l: l.qty > 0)
        if not lines_to_move:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Aviso'),
                    'message': _('No se han seleccionado productos o cantidades para transferir.'),
                    'type': 'warning',
                    'sticky': False,
                }
            }

        picking_type = self.env['stock.picking.type'].search([
            ('code', '=', 'internal'),
            ('warehouse_id', '=', warehouse.id)
        ], limit=1)

        picking_vals = {
            'location_id': source_location.id,
            'location_dest_id': salon_location.id,
            'picking_type_id': picking_type.id,
            'origin': self.pos_order_id.name,
            'move_ids': [(0, 0, {
                'product_id': line.product_id.id,
                'product_uom_qty': line.qty,
                'product_uom': line.product_id.uom_id.id,
                'location_id': source_location.id,
                'location_dest_id': salon_location.id,
            }) for line in lines_to_move]
        }

        picking = self.env['stock.picking'].create(picking_vals)
        picking.action_confirm()
        picking.button_validate()

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Éxito'),
                'message': _('Movimiento de almacén creado y validado correctamente: %s') % picking.name,
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'}
            }
        }


class PosOrderSalonWizardLine(models.TransientModel):
    _name = 'pos.order.salon.wizard.line'
    _description = 'Líneas del Wizard Transferir a Salón'

    wizard_id = fields.Many2one('pos.order.salon.wizard', string='Wizard', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Producto', required=True, domain="[('consumo_interno', '=', True)]")
    qty = fields.Float(string='Cantidad', default=1.0)
