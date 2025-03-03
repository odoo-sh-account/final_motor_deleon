from . import models

from odoo import api, SUPERUSER_ID


# In response of the error during uninstall: KeyError: 'loan.application'
def uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Clean up computed fields before model removal
    Model = env['ir.model'].search([('model', '=', 'loan.application')])
    if Model:
        Model.write({'state': 'manual'})  # Disable model tracking
        
    # Remove any leftover fields
    Field = env['ir.model.fields'].search([
        ('model', '=', 'sale.order'),
        ('name', 'in', ['spreadsheet_template_id', 'spreadsheet_id'])
    ])
    Field.unlink()