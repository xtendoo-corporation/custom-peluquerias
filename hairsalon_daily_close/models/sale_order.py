# Copyright 2026 Xtendoo - Xtendoo Corporation
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    pos_session_id = fields.Many2one(
        comodel_name="pos.session",
        string="POS session",
        copy=False,
        readonly=True,
        index="btree_not_null",
        help="Point of sale session open when the order was confirmed. "
        "The order is counted in that session's daily close.",
    )

    def action_confirm(self):
        res = super().action_confirm()
        for order in self.filtered(
            lambda so: so.state in ("sale", "done") and not so.pos_session_id
        ):
            session = self.env["pos.session"]._get_daily_close_session(order.company_id)
            if session:
                order.sudo().pos_session_id = session
        return res
