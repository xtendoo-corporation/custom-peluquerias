# Copyright 2026 Xtendoo - Xtendoo Corporation
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models, tools


class HairsalonDailyCloseSale(models.Model):
    """Sold orders (POS and Sales), one record per order."""

    _name = "hairsalon.daily.close.sale"
    _description = "Daily close - Sales"
    _auto = False
    _order = "date desc, id desc"

    date = fields.Date(readonly=True)
    origin = fields.Selection(
        selection=[("pos", "Point of sale"), ("sale", "Sales")],
        readonly=True,
    )
    pos_session_id = fields.Many2one("pos.session", readonly=True)
    company_id = fields.Many2one("res.company", readonly=True)
    currency_id = fields.Many2one("res.currency", readonly=True)
    reference = fields.Char(readonly=True)
    pos_order_id = fields.Many2one("pos.order", readonly=True)
    sale_order_id = fields.Many2one("sale.order", readonly=True)
    amount_sold = fields.Monetary(currency_field="currency_id", readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(
            f"""
            CREATE OR REPLACE VIEW {self._table} AS (
                SELECT
                    po.id * 2 AS id,
                    (po.date_order AT TIME ZONE 'UTC'
                        AT TIME ZONE COALESCE(rp.tz, 'UTC'))::date AS date,
                    'pos'::varchar AS origin,
                    po.session_id AS pos_session_id,
                    po.company_id AS company_id,
                    co.currency_id AS currency_id,
                    po.name AS reference,
                    po.id AS pos_order_id,
                    NULL::integer AS sale_order_id,
                    po.amount_total AS amount_sold
                FROM pos_order po
                JOIN res_company co ON co.id = po.company_id
                JOIN res_partner rp ON rp.id = co.partner_id
                WHERE po.state IN ('paid', 'done')

                UNION ALL

                SELECT
                    so.id * 2 + 1 AS id,
                    (so.date_order AT TIME ZONE 'UTC'
                        AT TIME ZONE COALESCE(rp.tz, 'UTC'))::date AS date,
                    'sale'::varchar AS origin,
                    so.pos_session_id AS pos_session_id,
                    so.company_id AS company_id,
                    co.currency_id AS currency_id,
                    so.name AS reference,
                    NULL::integer AS pos_order_id,
                    so.id AS sale_order_id,
                    so.amount_total AS amount_sold
                FROM sale_order so
                JOIN res_company co ON co.id = so.company_id
                JOIN res_partner rp ON rp.id = co.partner_id
                WHERE so.state IN ('sale', 'done')
            )
        """
        )
