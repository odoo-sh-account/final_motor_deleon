{
    'name': 'Moto-loan',
    'version': '18.0.0.0.1',
    'category': 'Kawiil/Custom Modules',
    'license': 'OPL-1',
    'summary': 'Streamlines the loan application process for dealerships. Alejandro',
    'description': 'A module to handle motorcycle loan applications, tracking, and management',
    'author': 'Odoo-sh-account',
    'website': 'https://github.com/odoo-sh-account/final_motor_deleon',
    'support': 'support@deleonlangure.com',
    'sequence': 10,
    'installable': True,
    'application': True,
    'auto_install': False,
    'depends': ['base', 'mail', 'sale', 'product', 'sale_management'],
    'data': [
        'security/financing_security.xml',
        'security/motorcycle_financing_groups.xml',
        'security/ir.model.access.csv',
        'security/rules.xml',
        'data/loan_sequence.xml',
        'views/loan_application_views.xml',
        'views/loan_application_tag_views.xml',
        'views/loan_application_document_type_views.xml',
        'views/loan_application_document_views.xml',
        'views/sale_order_views.xml',
        'views/res_partner_views.xml',
        'views/menu_views.xml',
        'data/loan_demo.xml',
    ],
}