from odoo import api, fields, models


class SaleDetailsWizard(models.TransientModel):
    _name = 'sale.details.wizard'
    _description = 'Sale Employee Details Report Wizard'

    date_start = fields.Date(
        string='Start Date',
        required=True,
        default=fields.Date.context_today,
    )
    date_stop = fields.Date(
        string='End Date',
        required=True,
        default=fields.Date.context_today,
    )
    sale_order_ids = fields.Many2many(
        'sale.order',
        string='Orders',
        help='Select specific sale orders to include in the report.',
    )

    def generate_report(self):
        data = {
            'date_start': self.date_start,
            'date_stop': self.date_stop,
            'sale_order_ids': self.sale_order_ids.ids,
        }
        return self.env.ref(
            'hairsalon_line_employees.sale_employee_details_report'
        ).report_action([], data=data)
