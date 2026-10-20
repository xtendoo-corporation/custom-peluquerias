{
    "name": "Carmen Olmedo - Extend POS Conventional",
    "version": "19.0.1.0.0",
    "category": "Sales/Point of Sale",
    "summary": "Botón Cerrar caja junto a Nuevo en el listado de pedidos POS convencional",
    "author": "Xtendoo",
    "website": "https://xtendoo.es",
    "license": "LGPL-3",
    "depends": ["pos_conventional_core"],
    "assets": {
        "web.assets_backend": [
            "carmenolmedo_extend_pos_conventional/static/src/js/pos_order_list_controller.js",
            "carmenolmedo_extend_pos_conventional/static/src/xml/pos_order_list_view.xml",
        ],
    },
    "installable": True,
    "application": False,
}
