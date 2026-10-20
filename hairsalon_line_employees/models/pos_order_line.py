from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PosOrderLineEmployee(models.Model):
    _inherit = "pos.order.line"

    employee_ids = fields.Many2many(
        "hr.employee",
        string="Empleado/s",
        relation="pos_order_line_hr_employee_rel",
        column1="pos_order_line_id",
        column2="hr_employee_id",
    )

    @api.constrains("employee_ids")
    def _check_employee_ids_required(self):
        for line in self:
            if not line.employee_ids:
                raise ValidationError(
                    _(
                        "Debe indicar al menos un empleado en la línea del producto %s.",
                        line.product_id.display_name or line.name or "",
                    )
                )

    @api.model
    def _load_pos_data_fields(self, config):
        """Ensure `employee_ids` is included when POS frontend requests pos.order.line data."""
        fields = super()._load_pos_data_fields(config) or []
        if "employee_ids" not in fields:
            fields = fields + ["employee_ids"]
        return fields
