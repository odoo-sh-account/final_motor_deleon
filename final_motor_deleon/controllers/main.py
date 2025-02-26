from odoo import http, fields
from odoo.http import request


class LoanApplicationController(http.Controller):
    
    @http.route('/loan/new', type='http', auth='user', website=True)
    def create_loan_application(self, **kw):
        """Create a new loan application directly"""
        values = {
            'default_state': 'draft',
            'form_view_initial_mode': 'edit',
        }
        
        # Create a new loan application
        loan_app = request.env['loan.application'].create({
            'name': request.env['ir.sequence'].next_by_code('loan.application') or 'New',
            'state': 'draft',
            'date_application': fields.Date.today(),
        })
        
        # Redirect to the form view
        return request.redirect('/web#id=%s&model=loan.application&view_type=form' % loan_app.id)
