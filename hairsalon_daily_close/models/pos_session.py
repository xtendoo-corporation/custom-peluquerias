# Copyright 2026 Xtendoo - Xtendoo Corporation
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, models


class PosSession(models.Model):
    _inherit = "pos.session"

    @api.model
    def _get_daily_close_session(self, company=None):
        """Sesión de TPV abierta a la que se imputan ventas y cobros de Ventas.

        Prefiere la sesión abierta del usuario actual y, si no tiene, la última
        sesión abierta de la compañía. Devuelve un recordset vacío si no hay.
        """
        company = company or self.env.company
        sessions = self.sudo().search(
            [("state", "=", "opened"), ("company_id", "=", company.id)],
            order="start_at desc, id desc",
        )
        own = sessions.filtered(lambda session: session.user_id == self.env.user)
        return (own or sessions)[:1]
