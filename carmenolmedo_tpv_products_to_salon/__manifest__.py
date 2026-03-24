{
    'name': 'Carmen Olmedo - TPV Productos a Salón',
    'version': '19.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'Permite transferir productos de consumo interno a un almacén virtual Salón desde un pedido TPV.',
    'description': """
        Añade un campo 'Consumo interno' a los productos.
        Permite desde un pedido del TPV transferir estos productos a una ubicación virtual de Salón,
        creando el movimiento de stock automáticamente.
    """,
    'author': 'Xtendoo',
    'website': 'https://www.xtendoo.es',
    'license': 'AGPL-3',
    'depends': [
        'point_of_sale',
        'stock',
        'pos_conventional',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/stock_location_data.xml',
        'views/product_template_views.xml',
        'views/pos_order_views.xml',
        'wizard/pos_order_salon_wizard_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
