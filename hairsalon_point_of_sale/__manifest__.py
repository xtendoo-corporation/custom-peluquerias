{
    'name': 'Hairsalon Point of Sale',
    'version': '19.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'Personalización del ticket de venta para peluquerías',
    'description': """
        Mueve la fecha y hora del ticket debajo de Factura Simplificada.
        Hereda de pos_conventional_receipt y xtendoo_pos_receipt.
    """,
    'author': 'Xtendoo',
    'website': 'https://xtendoo.es',
    'depends': [
        'pos_conventional_receipt',
        'pos_conventional_receipt_custom',
        'xtendoo_pos_receipt',
    ],
    'data': [
        'views/report_pos_order.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'hairsalon_point_of_sale/static/src/js/receipt_order_hair.js',
            'hairsalon_point_of_sale/static/src/xml/receipt_templates.xml',
        ],
    },
    'installable': True,
    'license': 'AGPL-3',
}
