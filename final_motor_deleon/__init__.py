from . import models

from odoo import api, SUPERUSER_ID


# In response of the error during uninstall: KeyError: 'loan.application'
# In __init__.py
def uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Proper model cleanup
    Model = env['ir.model'].search([('model', '=', 'loan.application')])
    if Model:
        # First remove fields to prevent ORM errors
        Field = env['ir.model.fields'].search([
            ('model_id', '=', Model.id)
        ])
        Field.unlink()
        
        # Then remove the model itself
        Model.unlink()
    
    # Clean up sale.order fields
    SaleFields = env['ir.model.fields'].search([
        ('model', '=', 'sale.order'),
        ('name', 'in', ['spreadsheet_template_id', 'spreadsheet_id'])
    ])
    SaleFields.unlink()