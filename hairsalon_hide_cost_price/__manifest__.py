{
    "name": "Hairsalon Hide Cost Price",
    "version": "19.0.1.0.0",
    "category": "Sales",
    "summary": "Hide product cost, margins and stock valuation from users "
    "without the 'Show Cost Price' group",
    "author": "Xtendoo",
    "website": "https://www.xtendoo.es",
    "license": "LGPL-3",
    "depends": [
        "product",
        "sale_management",
        "point_of_sale",
        "stock",
        "stock_account",
    ],
    "data": [
        "security/security.xml",
        "views/product_views.xml",
        "views/stock_account_views.xml",
        "views/point_of_sale_views.xml",
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
    "application": False,
    "auto_install": False,
}
