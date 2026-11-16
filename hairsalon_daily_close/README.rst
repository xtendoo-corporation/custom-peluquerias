Hairsalon Daily Close
=====================

Cierre diario que concilia las ventas y los cobros de Punto de venta (TPV) y
de Ventas (``sale.order``), incluidos los adelantos.

Funcionalidad
=============

El bloque *Cierre diario* se añade al informe de cierre de sesión del Punto de
venta (*Punto de venta > Informes > Resumen de ventas*, y al cerrar la sesión).
Muestra:

* **Total vendido**: importe de los pedidos del día (TPV y Ventas).
* **Total cobrado hoy**: cobros registrados en el día (TPV y Ventas), incluidos
  adelantos y cobros de ventas de días anteriores.
* **Pendiente de cobro**: importe vendido hoy menos todo lo cobrado de esas
  ventas.
* **Efectivo esperado en caja**: cobros en efectivo del día (los cambios de
  TPV se restan).

El detalle por venta y por cobro está disponible en las vistas SQL
``hairsalon.daily.close.sale`` y ``hairsalon.daily.close.payment``. El cálculo
del resumen está en ``hairsalon.daily.close.get_summary``.

Orígenes de los datos
=====================

* TPV: ``pos.payment`` de pedidos en estado pagado o hecho. No depende de que
  la sesión esté cerrada.
* Ventas: pagos de cliente publicados y conciliados con facturas ligadas a un
  pedido de venta (``sale_order_line_invoice_rel``). Cada pago se cuenta una
  sola vez y se excluyen los pagos que ya son cobros de TPV.

Limitaciones
============

* Los importes se expresan en la moneda de la compañía.
* Los pagos de clientes que no están conciliados con facturas de venta no se
  incluyen en el cierre.
* La fecha de los cobros de TPV se calcula con la zona horaria del partner de
  la compañía.

Instalación y pruebas
=====================

Instalar el módulo ``hairsalon_daily_close`` en la base de datos. Para
ejecutar los tests::

    odoo -d <db> -u hairsalon_daily_close --test-enable \
        --test-tags /hairsalon_daily_close --stop-after-init

Licencia
========

LGPL-3.0 o posterior.
