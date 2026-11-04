from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_employee_contact = fields.Boolean(
        string="Is Employee Contact",
        compute="_compute_is_employee_contact",
        search="_search_is_employee_contact",
        help="The contact is the work contact of an active employee of the company.",
    )

    def _get_employee_contact_domain(self):
        return [
            ("work_contact_id", "!=", False),
            ("company_id", "in", self.env.companies.ids),
        ]

    @api.depends_context("allowed_company_ids")
    def _compute_is_employee_contact(self):
        employees = (
            self.env["hr.employee"]
            .sudo()
            .search(
                self._get_employee_contact_domain()
                + [("work_contact_id", "in", self.ids)]
            )
        )
        employee_contacts = employees.work_contact_id
        for partner in self:
            partner.is_employee_contact = partner in employee_contacts

    def _search_is_employee_contact(self, operator, value):
        if operator not in ("in", "not in"):
            return NotImplemented
        employee_query = (
            self.env["hr.employee"].sudo()._search(self._get_employee_contact_domain())
        )
        return [("id", operator, employee_query.select("work_contact_id"))]
