from odoo import models, fields, api
from odoo.exceptions import UserError

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

    @api.onchange('is_financed')
    def _onchange_is_financed(self):
        """
        Validate that exactly one Motorcycle product exists in sale order lines 
        when is_financed is set to True.
        """
        if self.is_financed:
            # Find the Motorcycles product category
            motorcycle_category = self.env['product.category'].search([('name', '=', 'Motorcycles')], limit=1)
            
            # Filter order lines with products in the Motorcycles category
            motorcycle_lines = self.order_line.filtered(lambda line: line.product_id.categ_id == motorcycle_category)
            
            if len(motorcycle_lines) != 1:
                return {
                    'warning': {
                        'title': 'Financing Validation Error',
                        'message': 'To apply financing, the sale order must have exactly one Motorcycle product.'
                    },
                    'value': {'is_financed': False}
                }

    def action_create_loan_application(self):
        """
        Create a new loan application directly from the sales order
        when no existing loan application is found.
        """
        self.ensure_one()
        
        # Ensure the sales order is financed
        if not self.is_financed:
            return False
        
        # Find the Motorcycles product category
        motorcycle_category = self.env['product.category'].search([('name', '=', 'Motorcycles')], limit=1)
        
        # Validate that the order contains exactly one motorcycle
        motorcycle_lines = self.order_line.filtered(lambda line: line.product_id.categ_id == motorcycle_category)
        if len(motorcycle_lines) != 1:
            raise UserError(_('Loan applications are only allowed for sale orders with exactly one motorcycle.'))
        
        # Get the motorcycle line
        motorcycle_line = motorcycle_lines[0]
        
        # Create loan application with sales order details
        loan_app = self.env['loan.application'].create({
            'partner_id': self.partner_id.id,
            'sale_order_id': self.id,
            'loan_amount': motorcycle_line.price_subtotal,
            'down_payment': 0,  # Default down payment
            'loan_term': 24,    # Default loan term
            'interest_rate': 6.0,  # Default interest rate
            'state': 'draft',
            'date_application': fields.Date.today(),
        })
        
        # Link the loan application to the sale order
        self.loan_application_id = loan_app
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Loan Application',
            'res_model': 'loan.application',
            'view_mode': 'form',
            'res_id': loan_app.id,
            'target': 'current',
        }

    # Signature tracking fields
    signed_by = fields.Char(string='Signed By', help='Name of the person who signed the document')
    signed_on = fields.Datetime(string='Signed On', help='Date and time of signature')
    signed_document = fields.Binary(string='Signed Document', help='Uploaded signed document')

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