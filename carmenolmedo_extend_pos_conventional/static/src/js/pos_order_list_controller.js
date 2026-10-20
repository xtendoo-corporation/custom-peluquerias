/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PosOrderListController } from "@pos_conventional_core/js/pos_order_list_controller";

patch(PosOrderListController.prototype, {
    get actionMenuItems() {
        const items = super.actionMenuItems;
        // "Cerrar caja" pasa a ser un botón junto a "Nuevo"; se quita del menú de acciones.
        items.action = (items.action || []).filter((item) => item.key !== "close_session");
        return items;
    },
});
