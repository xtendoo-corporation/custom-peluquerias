# Copyright 2026 Xtendoo - Xtendoo Corporation
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models, tools


class HairsalonDailyClosePayment(models.Model):
    """Real collections (POS and Sales), one record per collection line.

    POS collections come from pos.payment. Sales collections come from the
    partial reconciliations between customer payments and invoices linked to
    a sale order, so each payment is counted only once.
    """

    _name = "hairsalon.daily.close.payment"
    _description = "Daily close - Payments"
    _auto = False
    _order = "date desc, id desc"

    date = fields.Date(readonly=True)
    origin = fields.Selection(
        selection=[("pos", "Point of sale"), ("sale", "Sales")],
        readonly=True,
    )
    company_id = fields.Many2one("res.company", readonly=True)
    currency_id = fields.Many2one("res.currency", readonly=True)
    payment_method = fields.Char(string="Payment method", readonly=True)
    is_cash = fields.Boolean(string="Cash", readonly=True)
    amount = fields.Monetary(currency_field="currency_id", readonly=True)
    pos_order_id = fields.Many2one("pos.order", readonly=True)
    sale_order_id = fields.Many2one("sale.order", readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(
            f"""
            CREATE OR REPLACE VIEW {self._table} AS (
                SELECT
                    pp.id * 2 AS id,
                    (pp.payment_date AT TIME ZONE 'UTC'
                        AT TIME ZONE COALESCE(rp.tz, 'UTC'))::date AS date,
                    'pos'::varchar AS origin,
                    po.company_id AS company_id,
                    co.currency_id AS currency_id,
                    COALESCE(pm.name->>'es_ES', pm.name->>'en_US')
                        AS payment_method,
                    COALESCE(pm.is_cash_count, FALSE) AS is_cash,
                    CASE
                        WHEN pp.is_change THEN -pp.amount
                        ELSE pp.amount
                    END AS amount,
                    po.id AS pos_order_id,
                    NULL::integer AS sale_order_id
                FROM pos_payment pp
                JOIN pos_order po ON po.id = pp.pos_order_id
                JOIN pos_payment_method pm ON pm.id = pp.payment_method_id
                JOIN res_company co ON co.id = po.company_id
                JOIN res_partner rp ON rp.id = co.partner_id
                WHERE po.state IN ('paid', 'done')

                UNION ALL

                SELECT
                    apr.id * 2 + 1 AS id,
                    ap.date AS date,
                    'sale'::varchar AS origin,
                    ap.company_id AS company_id,
                    co.currency_id AS currency_id,
                    COALESCE(aj.name->>'es_ES', aj.name->>'en_US')
                        AS payment_method,
                    (aj.type = 'cash') AS is_cash,
                    apr.amount AS amount,
                    NULL::integer AS pos_order_id,
                    vf.sale_order_id AS sale_order_id
                FROM account_partial_reconcile apr
                JOIN account_move_line il
                    ON il.id IN (apr.debit_move_id, apr.credit_move_id)
                JOIN account_move_line pl
                    ON pl.id IN (apr.debit_move_id, apr.credit_move_id)
                    AND pl.id <> il.id
                JOIN account_account ail ON ail.id = il.account_id
                JOIN account_account pal ON pal.id = pl.account_id
                JOIN account_move inv ON inv.id = il.move_id
                JOIN account_move pm_move ON pm_move.id = pl.move_id
                JOIN account_payment ap ON ap.move_id = pm_move.id
                JOIN account_journal aj ON aj.id = ap.journal_id
                JOIN res_company co ON co.id = ap.company_id
                LEFT JOIN (
                    SELECT aml.move_id, MIN(sol.order_id) AS sale_order_id
                    FROM account_move_line aml
                    JOIN sale_order_line_invoice_rel rel
                        ON rel.invoice_line_id = aml.id
                    JOIN sale_order_line sol ON sol.id = rel.order_line_id
                    GROUP BY aml.move_id
                ) vf ON vf.move_id = inv.id
                WHERE ap.payment_type = 'inbound'
                    AND ap.state IN ('in_process', 'paid')
                    AND inv.move_type IN ('out_invoice', 'out_refund')
                    AND ail.account_type = 'asset_receivable'
                    AND pal.account_type = 'asset_receivable'
                    AND NOT EXISTS (
                        SELECT 1 FROM pos_payment pp2
                        WHERE pp2.account_move_id = pm_move.id
                    )
            )
        """
        )
