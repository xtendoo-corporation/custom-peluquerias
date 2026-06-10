/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { OrderReceipt } from "@point_of_sale/app/screens/receipt_screen/receipt/order_receipt";
import { onMounted } from "@odoo/owl";

patch(OrderReceipt.prototype, {
    setup() {
        super.setup();
        onMounted(() => {
            console.log("Hairsalon Point of Sale: OrderReceipt mounted");
            const el = document.querySelector('.pos-receipt');
            if (el) {
                console.log("Hairsalon Point of Sale: Found .pos-receipt element");
            }
        });
    }
});

