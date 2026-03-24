from odoo import models

class PosOrder(models.Model):
    _inherit = 'pos.order'

    def action_open_salon_wizard(self):
        self.ensure_one()
        
        return {
            'name': 'Transferir a Salón',
            'type': 'ir.actions.act_window',
            'res_model': 'pos.order.salon.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_pos_order_id': self.id,
            }
        }
