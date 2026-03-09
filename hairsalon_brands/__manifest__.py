{
    'name': 'Hairsalon Brands',
    'version': '19.0.1.0.0',
    'category': 'Sales',
    'summary': 'Manage brands and brand lines for products',
    'description': """
        This module allows you to create brands and associate them with products.
        It also allows you to create brand lines for each brand and associate them with products.
    """,
    'author': 'Xtendoo',
    'depends': ['product', 'sale', 'point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/hairsalon_brand_views.xml',
        'views/product_template_views.xml',
        'wizard/hairsalon_brand_migrate_wizard_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
