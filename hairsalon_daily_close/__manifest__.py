# Copyright 2026 Xtendoo - Xtendoo Corporation
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "Hairsalon Daily Close",
    "version": "19.0.1.0.1",
    "category": "Point of Sale",
    "summary": "Daily close reconciling POS and Sales sales and collections",
    "author": "Xtendoo",
    "website": "https://xtendoo.es",
    "license": "LGPL-3",
    "depends": [
        "account",
        "point_of_sale",
        "sale",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/ir_rule.xml",
        "views/pos_session_sales_details_views.xml",
        "views/sale_order_views.xml",
    ],
    "installable": True,
    "application": False,
}
