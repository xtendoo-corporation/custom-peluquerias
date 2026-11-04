from odoo import models
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _has_employee_partner(self):
        self.ensure_one()
        if not self.partner_id:
            return False
        return bool(
            self.env["hr.employee"]
            .sudo()
            .search_count(
                [
                    ("work_contact_id", "=", self.partner_id.id),
                    ("company_id", "=", self.company_id.id),
                ],
                limit=1,
            )
        )

    def _check_internal_transfer_partner(self):
        invalid_pickings = self.filtered(
            lambda picking: (
                picking.picking_type_code == "internal"
                and not picking._has_employee_partner()
            )
        )
        if invalid_pickings:
            raise ValidationError(
                self.env._(
                    "Internal transfers must have an employee of the company as "
                    "contact. Review: %(pickings)s",
                    pickings=", ".join(invalid_pickings.mapped("display_name")),
                )
            )

    def action_confirm(self):
        self._check_internal_transfer_partner()
        return super().action_confirm()

    def button_validate(self):
        self.filtered(
            lambda picking: picking.state != "done"
        )._check_internal_transfer_partner()
        return super().button_validate()
