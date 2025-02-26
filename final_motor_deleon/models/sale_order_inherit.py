from odoo import models, fields, api

class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    def action_view_loan_application(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Loan Application',
            'res_model': 'loan.application',
            'view_mode': 'form',
            'res_id': self.loan_application_id.id,
            'target': 'current',
        }

    # Add a Many2one field to link to loan application
    loan_application_id = fields.Many2one(
        'loan.application', 
        string='Loan Application', 
        help='Linked loan application for this sale order'
    )

    # Add a Boolean field to indicate financing requirement
    is_financed = fields.Boolean(
        string='Requires Financing', 
        default=False, 
        help='Check if this sale order requires financing'
    )

    # Add a computed field to get all related loan applications
    loan_application_ids = fields.One2many(
        'loan.application', 
        'sale_order_id', 
        string='Loan Applications', 
        help='All loan applications related to this sale order'
    )

    # Compute method to automatically set is_financed
    @api.depends('loan_application_id')
    def _compute_is_financed(self):
        for order in self:
            order.is_financed = bool(order.loan_application_id)

    def action_create_loan_application(self):
        """
        Create a new loan application directly from the sales order
        when no existing loan application is found.
        """
        self.ensure_one()
        
        # Ensure the sales order is financed
        if not self.is_financed:
            return False
        
        # Get the first order line for product information
        first_line = self.order_line and self.order_line[0]
        
        # Create loan application
        loan_app = self.env['loan.application'].create({
            'partner_id': self.partner_id.id,
            'sale_order_id': self.id,
            'product_template_id': first_line.product_id.product_tmpl_id.id if first_line else False,
            'loan_amount': self.amount_total,
            'down_payment': 0,  # Default, can be adjusted
            'loan_term': 36,    # Default term, can be adjusted
            'interest_rate': 6.0,  # Default rate, can be adjusted
            'state': 'draft',
            'date_application': fields.Date.today(),
            'user_id': self.user_id.id,
        })
        
        # Update the sales order with the new loan application
        self.loan_application_id = loan_app
        
        # Open the newly created loan application
        return {
            'type': 'ir.actions.act_window',
            'name': 'Loan Application',
            'res_model': 'loan.application',
            'view_mode': 'form',
            'res_id': loan_app.id,
            'target': 'current',
        }

class LoanApplication(models.Model):
    _inherit = 'loan.application'

    def action_view_sale_order(self):
        """
        Navigate to the related sales order from a loan application.
        """
        self.ensure_one()
        if not self.sale_order_id:
            return False
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sales Order',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'res_id': self.sale_order_id.id,
            'target': 'current',
        }