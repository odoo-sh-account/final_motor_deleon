from odoo import models, fields, api, _

class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    # One2many field to link loan applications
    application_ids = fields.One2many(
        'loan.application', 
        'partner_id', 
        string='Loan Applications'
    )
    
    # Computed field to count loan applications
    application_count = fields.Integer(
        string='Loan Applications',
        compute='_compute_application_count',
        store=False
    )
    
    @api.depends('application_ids')
    def _compute_application_count(self):
        """Compute the number of loan applications for each partner"""
        for partner in self:
            partner.application_count = len(partner.application_ids)
    
    def action_view_applications(self):
        """Open a filtered view of loan applications for this customer"""
        self.ensure_one()
        
        # Get all loan applications for this partner
        applications = self.application_ids
        
        # Define the action
        action = {
            'type': 'ir.actions.act_window',
            'name': _('Loan Applications'),
            'res_model': 'loan.application',
            'view_mode': 'list,form',
            'domain': [('id', 'in', applications.ids)],
            'context': {'default_partner_id': self.id},
        }
        
        # If there's only one application, open it directly in form view
        if len(applications) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': applications.id,
            })
            
        return action
