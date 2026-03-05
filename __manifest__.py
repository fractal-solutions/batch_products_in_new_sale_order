{
    'name': 'Batch Products in New Sales Order',
    'version': '1.0',
    'summary': 'A test module for demonstration purposes',
    'description': 'This module is created to demonstrate the structure of an Odoo module.',
    'author': 'Fractal Solutions',
    'category': 'Experimental',
    'depends': ['base', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
}
