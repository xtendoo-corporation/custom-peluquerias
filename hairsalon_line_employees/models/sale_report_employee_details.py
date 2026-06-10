from odoo import api, models


class SaleReportEmployeeDetails(models.AbstractModel):
    _name = 'report.hairsalon_line_employees.sale_employee_details'
    _description = 'Sale Order Employee Details Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data:
            data = {}

        date_start = data.get('date_start')
        date_stop = data.get('date_stop')
        sale_order_ids = data.get('sale_order_ids', [])

        domain = [('state', 'in', ['sale', 'done'])]
        if date_start:
            domain.append(('date_order', '>=', date_start))
        if date_stop:
            domain.append(('date_order', '<=', date_stop + ' 23:59:59'))
        if sale_order_ids:
            domain.append(('id', 'in', sale_order_ids))

        orders = self.env['sale.order'].search(domain, order='date_order asc')

        employee_sales_data = {}
        for order in orders:
            for line in order.order_line:
                if line.display_type:
                    continue
                employees = line.employee_ids
                if not employees:
                    continue

                line_total = float(line.price_subtotal or 0.0)
                amount_per_employee = line_total / len(employees)
                product_name = (
                    line.product_id.display_name
                    if line.product_id else line.name or ''
                )
                date_str = (
                    order.date_order.strftime('%d/%m/%Y %H:%M')
                    if order.date_order else ''
                )

                for employee in employees:
                    if employee.id not in employee_sales_data:
                        employee_sales_data[employee.id] = {
                            'employee_name': employee.name,
                            'lines': [],
                            'total_amount': 0.0,
                        }
                    employee_sales_data[employee.id]['lines'].append({
                        'order_name': order.name or '',
                        'partner_name': order.partner_id.name or '',
                        'product_name': product_name,
                        'date': date_str,
                        'line_total': line_total,
                        'employee_amount': amount_per_employee,
                    })
                    employee_sales_data[employee.id]['total_amount'] += amount_per_employee

        employee_sales_grouped = list(employee_sales_data.values())
        employee_sales_grouped.sort(key=lambda x: x['employee_name'])

        sale_order_names = []
        if sale_order_ids:
            sale_order_names = [o.name for o in orders]

        currency = self.env.user.company_id.currency_id
        currency_data = {
            'symbol': currency.symbol or '',
            'position': currency.position or 'before',
            'precision': currency.decimal_places,
        }

        return {
            'doc_ids': docids,
            'doc_model': 'sale.order',
            'data': data,
            'docs': orders,
            'employee_sales_grouped': employee_sales_grouped,
            'sale_order_names': sale_order_names,
            'currency': currency_data,
        }
