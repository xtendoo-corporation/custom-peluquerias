from collections import defaultdict
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    employees_summary = fields.Char(
        string="Resumen de Empleados",
        compute="_compute_employees_summary",
        store=True,
    )

    @api.depends("order_line.employee_ids", "order_line.price_subtotal")
    def _compute_employees_summary(self):
        for order in self:
            if not order.order_line:
                order.employees_summary = ""
                continue

            accum = defaultdict(float)
            currency = order.currency_id or order.company_id.currency_id

            for line in order.order_line:
                line_total = float(line.price_subtotal or 0.0)
                n = len(line.employee_ids or [])
                if n:
                    per = line_total / n
                    for emp in line.employee_ids:
                        accum[emp.id] += per
                else:
                    accum[0] += line_total

            parts = []
            if accum.get(0.0):
                formatted_unassigned = f"{currency.symbol}{accum[0.0]:.2f}" if currency else f"{accum[0.0]:.2f}"
                parts.append(f"Sin asignar: {formatted_unassigned}")

            employees = self.env["hr.employee"].browse([k for k in accum.keys() if k])
            for emp in employees:
                amt = accum.get(emp.id, 0.0)
                formatted = f"{currency.symbol}{amt:.2f}" if currency else f"{amt:.2f}"
                parts.append(f"{emp.name}: {formatted}")

            order.employees_summary = "; ".join(parts)

