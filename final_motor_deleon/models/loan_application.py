from odoo import models, fields
from odoo.exceptions import UserError
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class LoanApplication(models.Model):
    _name = 'loan.application'
    _description = 'Loan Application'
    _order = 'date_application desc' 
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Application Number',
        store=True,
        compute='_compute_name',
        required=True
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency', 
        string='Currency',
        default=lambda self: self.env.company.currency_id.id
    )

    @api.depends('partner_id', 'sale_order_id')
    def _compute_name(self):
        for record in self:
            partner_name = record.partner_id.name or ''
            
            # Get the name of the first product from the sales order
            if record.sale_order_id and record.sale_order_id.order_line:
                product_name = record.sale_order_id.order_line[0].name or ''
            else:
                product_name = ''
            
            record.name = f"{partner_name} - {product_name}"

    date_application = fields.Date(string='Application Date', default=fields.Date.today, readonly=True, copy=False)
    date_approval = fields.Date(string='Approval Date', readonly=True, copy=False)
    date_rejection = fields.Date(string='Rejection Date', readonly=True, copy=False)
    date_signed = fields.Datetime(string='Signed On', readonly=True, copy=False)
    down_payment = fields.Monetary(string='Down Payment', required=True, currency_field='currency_id')
    interest_rate = fields.Float(string='Interest Rate (%)', required=True, digits=(5, 2))
    loan_amount = fields.Monetary(string='Loan Amount', required=True, currency_field='currency_id')
    loan_term = fields.Integer(string='Loan Term (Months)', required=True, default=36)
    rejection_reason = fields.Text(string='Rejection Reason', copy=False)
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('sent', 'Sent'),
            ('review', 'Credit Check'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('signed', 'Signed'),
            ('cancel', 'Canceled')
        ],
        default='draft',
        string='Status',
        copy=False,
        tracking=True
    )

    sale_order_id = fields.Many2one('sale.order', string='Sales Order', tracking=True)
    partner_id = fields.Many2one('res.partner', string='Customer', required=True, tracking=True)

    @api.onchange('sale_order_id')
    def _onchange_sale_order_id(self):
        if self.sale_order_id:
            # Find the Motorcycles product category
            motorcycle_category = self.env['product.category'].search([('name', '=', 'Motorcycles')], limit=1)
            
            # Find motorcycle lines
            motorcycle_lines = self.sale_order_id.order_line.filtered(
                lambda line: line.product_id.categ_id == motorcycle_category
            )
            
            if motorcycle_lines:
                motorcycle_line = motorcycle_lines[0]
                
                # Set default values
                self.partner_id = self.sale_order_id.partner_id
                self.loan_amount = motorcycle_line.price_subtotal
                self.down_payment = 0
                self.loan_term = 24
                self.interest_rate = 6.0
                
                # Set product template if available
                if motorcycle_line.product_id and motorcycle_line.product_id.product_tmpl_id:
                    self.product_template_id = motorcycle_line.product_id.product_tmpl_id
                
    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        
        # If created from a sales order context
        sale_order_id = self.env.context.get('default_sale_order_id')
        if sale_order_id:
            sale_order = self.env['sale.order'].browse(sale_order_id)
            
            # Find the Motorcycles product category
            motorcycle_category = self.env['product.category'].search([('name', '=', 'Motorcycles')], limit=1)
            
            # Find motorcycle lines
            motorcycle_lines = sale_order.order_line.filtered(
                lambda line: line.product_id.categ_id == motorcycle_category
            )
            
            if motorcycle_lines and len(motorcycle_lines) > 0:
                motorcycle_line = motorcycle_lines[0]
                
                # Set default values
                defaults.update({
                    'partner_id': sale_order.partner_id.id,
                    'sale_order_id': sale_order.id,
                    'loan_amount': motorcycle_line.price_subtotal,
                    'down_payment': 0,
                    'loan_term': 24,
                    'interest_rate': 6.0,
                    'state': 'draft',
                    'date_application': fields.Date.today(),
                })
                
                # Set product template if available
                if motorcycle_line.product_id and motorcycle_line.product_id.product_tmpl_id:
                    defaults['product_template_id'] = motorcycle_line.product_id.product_tmpl_id.id
                    
        return defaults

    _sql_constraints = [
        ('positive_amount_check',
         'CHECK(loan_amount >= 0 AND down_payment >= 0)',
         'Loan amount and down payment must be positive values.'),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        # Detect if this is being created from a sales order context
        for vals in vals_list:
            if not vals.get('sale_order_id'):
                sale_order_context = self.env.context.get('active_model') == 'sale.order'
                if sale_order_context:
                    active_id = self.env.context.get('active_id')
                    if active_id:
                        sale_order = self.env['sale.order'].browse(active_id)
                        
                        # Find the Motorcycles product category
                        motorcycle_category = self.env['product.category'].search([('name', '=', 'Motorcycles')], limit=1)
                        
                        # Find motorcycle lines
                        motorcycle_lines = sale_order.order_line.filtered(lambda line: line.product_id.categ_id == motorcycle_category)
                        
                        if motorcycle_lines:
                            motorcycle_line = motorcycle_lines[0]
                            
                            # Prepopulate fields
                            vals.update({
                                'partner_id': sale_order.partner_id.id,
                                'sale_order_id': sale_order.id,
                                'loan_amount': motorcycle_line.price_subtotal,
                                'down_payment': 0,
                                'loan_term': 24,
                                'interest_rate': 6.0,
                                'state': 'draft',
                                'date_application': fields.Date.today(),
                            })

        # Call the original create method
        applications = super().create(vals_list)

        # Create documents for each application (existing logic)
        document_types = self.env['loan.application.document.type'].search([('active', '=', True)])
        
        for app in applications:
            documents = []
            for doc_type in document_types:
                documents.append({
                    'name': f"{doc_type.name} Document",
                    'application_id': app.id,
                    'document_type_id': doc_type.id,
                    'state': 'draft'
                })
            self.env['loan.application.document'].create(documents)
        
        return applications

    @api.constrains('down_payment', 'sale_order_id')
    def _check_down_payment_limit(self):
        for application in self:
            if application.sale_order_id:
                order_total = application.sale_order_id.amount_total
                if application.down_payment > order_total:
                    raise ValidationError(
                        _("Down payment (₡%(down_payment)s) exceeds sales order total of ₡%(order_total)s") % {
                            'down_payment': application.down_payment,
                            'order_total': order_total
                        }
                    )

    def action_send_for_approval(self):
        self.ensure_one()
        
        # Document validation
        if not self.document_ids:
            raise UserError("Cannot send application - no documents attached")
        
        if any(doc.state != 'approved' for doc in self.document_ids):
            raise UserError("Cannot send application - some documents are not approved")
        
        # Update state and date
        self.write({
            'state': 'sent',
            'date_approval': fields.Datetime.now()
        })

        return {
        'type': 'ir.actions.client',
        'tag': 'display_notification',
        'params': {
            'title': 'Success',
            'message': 'Application successfully sent for approval!',
            'type': 'success',
            'sticky': False,
        }
    }

    def action_approve(self):
        self.ensure_one()
        self.write({'state':'approved'})
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': 'Application approved!',
                'type': 'success',
                'sticky': False,
            }
        }

    def action_reject(self):
        self.ensure_one()
        self.write({'state':'rejected'})
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': 'Application rejected!',
                'type': 'success',
                'sticky': False,
            }
        }


    notes = fields.Html(string='Notes', copy=False)
    
    # New relational fields
    document_ids = fields.One2many('loan.application.document', 'application_id', string='Documents')
    tag_ids = fields.Many2many('loan.application.tag', string='Tags')
    user_id = fields.Many2one('res.users', string='Salesperson')
    product_template_id = fields.Many2one('product.template', string='Product')
