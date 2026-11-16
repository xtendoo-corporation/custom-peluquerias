# Copyright 2026 Xtendoo - Xtendoo Corporation
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, models

ORIGIN_LABELS = {"pos": "Punto de venta", "sale": "Ventas"}


class HairsalonDailyClose(models.AbstractModel):
    """Cálculo del cierre diario que concilia cobros de TPV y de Ventas."""

    _name = "hairsalon.daily.close"
    _description = "Daily close"

    @api.model
    def get_summary(self, date_from, date_to, company):
        """Devuelve totales y desgloses del cierre de un intervalo y compañía.

        Los cobros se filtran por su fecha de pago, incluidos los de facturas
        sin pedido de venta.
        """
        domain = [
            ("date", ">=", date_from),
            ("date", "<=", date_to),
            ("company_id", "=", company.id),
        ]
        self.env.flush_all()
        sales = self.env["hairsalon.daily.close.sale"].sudo().search(domain)
        payments = self.env["hairsalon.daily.close.payment"].sudo().search(domain)
        # Cobros de las ventas del periodo, incluidos los hechos en otras fechas.
        sale_payments = (
            self.env["hairsalon.daily.close.payment"]
            .sudo()
            .search(
                [
                    ("company_id", "=", company.id),
                    "|",
                    ("pos_order_id", "in", sales.pos_order_id.ids),
                    ("sale_order_id", "in", sales.sale_order_id.ids),
                ]
            )
        )
        total_sold = sum(sales.mapped("amount_sold"))
        return {
            "date_from": date_from,
            "date_to": date_to,
            "currency": company.currency_id,
            "total_sold": total_sold,
            "total_collected": sum(payments.mapped("amount")),
            "pending_collection": total_sold - sum(sale_payments.mapped("amount")),
            "expected_cash": sum(payments.filtered("is_cash").mapped("amount")),
            "sales": self._group_sales(sales),
            "payments": self._group_payments(payments),
        }

    @api.model
    def _group_sales(self, sales):
        return [
            {
                "origin": label,
                "amount": sum(
                    sales.filtered(lambda sale, o=origin: sale.origin == o).mapped(
                        "amount_sold"
                    )
                ),
            }
            for origin, label in ORIGIN_LABELS.items()
        ]

    @api.model
    def _group_payments(self, payments):
        groups = {}
        for payment in payments:
            key = (payment.origin, payment.payment_method or "")
            groups[key] = groups.get(key, 0.0) + payment.amount
        return [
            {
                "origin": ORIGIN_LABELS.get(origin, origin),
                "method": method,
                "amount": amount,
            }
            for (origin, method), amount in sorted(groups.items())
        ]
