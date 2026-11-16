# Copyright 2026 Xtendoo - Xtendoo Corporation
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class ReportPointOfSaleSaledetails(models.AbstractModel):
    _inherit = "report.point_of_sale.report_saledetails"

    @api.model
    def _get_report_values(self, docids, data=None):
        values = super()._get_report_values(docids, data=data)
        date_from, date_to = self._get_daily_close_period(values)
        sessions = self.env["pos.session"].browse(values.get("session_ids") or [])
        values["daily_close"] = self.env["hairsalon.daily.close"].get_summary(
            date_from, date_to, self.env.company, sessions=sessions
        )
        return values

    @api.model
    def _get_daily_close_period(self, values):
        """Intervalo del cierre: el del informe o el de las sesiones indicadas."""
        if values.get("date_start"):
            date_from = fields.Date.to_date(values["date_start"])
            date_to = fields.Date.to_date(
                values.get("date_stop") or values["date_start"]
            )
            return date_from, max(date_from, date_to)
        sessions = self.env["pos.session"].browse(values.get("session_ids") or [])
        if sessions:
            dates = [
                fields.Date.context_today(sessions[0], session.start_at)
                for session in sessions
            ]
            return min(dates), max(dates)
        today = fields.Date.context_today(self)
        return today, today
