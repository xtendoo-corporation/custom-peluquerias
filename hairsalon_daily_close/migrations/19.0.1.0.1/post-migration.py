# Copyright 2026 Xtendoo - Xtendoo Corporation
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

_SESSION_AT = """
    SELECT ps.id
    FROM pos_session ps
    JOIN pos_config pc ON pc.id = ps.config_id
    WHERE pc.company_id = {table}.company_id
        AND ps.start_at <= {moment}
        AND (ps.stop_at IS NULL OR ps.stop_at >= {moment})
    ORDER BY ps.start_at DESC, ps.id DESC
    LIMIT 1
"""


def migrate(cr, version):
    """Imputa a su sesión los pedidos de venta y cobros ya existentes.

    Se usa la sesión de la compañía que estaba abierta en el momento de la
    confirmación del pedido (date_order) o del registro del cobro (create_date).
    """
    cr.execute(
        f"""
        UPDATE sale_order
        SET pos_session_id = ({_SESSION_AT.format(table="sale_order", moment="sale_order.date_order")})
        WHERE pos_session_id IS NULL AND state IN ('sale', 'done')
    """
    )
    cr.execute(
        f"""
        UPDATE account_payment
        SET pos_session_id = ({_SESSION_AT.format(table="account_payment", moment="account_payment.create_date")})
        WHERE pos_session_id IS NULL
            AND payment_type = 'inbound' AND partner_type = 'customer'
    """
    )
