def migrate(cr, version):
    """pos.order.attended_by_id pasa de res.users a hr.employee.

    Cada usuario se sustituye por su empleado (el de la misma compañía si hay
    varios). Si no tiene empleado queda vacío, por lo que se relaja el NOT NULL
    antes de que se actualice el esquema.
    """
    cr.execute("ALTER TABLE pos_order ALTER COLUMN attended_by_id DROP NOT NULL")
    cr.execute("""
        UPDATE pos_order po
           SET attended_by_id = (
                SELECT e.id
                  FROM hr_employee e
                 WHERE e.user_id = po.attended_by_id
              ORDER BY (e.company_id = po.company_id) DESC, e.id
                 LIMIT 1)
         WHERE po.attended_by_id IS NOT NULL
    """)
