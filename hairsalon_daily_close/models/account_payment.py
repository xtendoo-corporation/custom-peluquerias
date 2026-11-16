# Copyright 2026 Xtendoo - Xtendoo Corporation
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    pos_session_id = fields.Many2one(
        comodel_name="pos.session",
        string="POS session",
        copy=False,
        readonly=True,
        index="btree_not_null",
        help="Point of sale session open when the payment was registered. "
        "The payment is counted in that session's daily close.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        payments = super().create(vals_list)
        for payment in payments.filtered(
            lambda pay: pay.payment_type == "inbound"
            and pay.partner_type == "customer"
            and not pay.pos_session_id
        ):
            session = self.env["pos.session"]._get_daily_close_session(payment.company_id)
            if session:
                payment.sudo().pos_session_id = session
        return payments
