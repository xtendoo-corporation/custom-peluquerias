from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    employee_ids = fields.Many2many(
        "hr.employee",
        string="Empleado/s",
        relation="sale_order_line_hr_employee_rel",
        column1="sale_order_line_id",
        column2="hr_employee_id",
    )

