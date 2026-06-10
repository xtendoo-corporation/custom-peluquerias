{
    'name': 'Hairsalon Price',
    'version': '19.0.1.0.0',
    'category': 'Sales',
    'summary': 'Restrict price changes on products with variants',
    'description': """
        When a product has multiple variants, the base price (list price)
        becomes read-only. Prices can only be modified at the variant level.
    """,
    'author': 'Xtendoo',
    'depends': ['product'],
    'data': [
        'views/product_template_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
