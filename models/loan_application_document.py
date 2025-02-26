from odoo import api, fields, models

class LoanApplicationDocument(models.Model):
    _name = 'loan.application.document'
    _description = 'Loan Application Document'

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Document name already exists!"),
    ]

    name = fields.Char(string='Name', required=True)
    application_id = fields.Many2one('loan.application', string='Loan Application', required=True, ondelete='cascade')
    attachment = fields.Binary(string='File')
    type_id = fields.Many2one('loan.application.document.type', string='Document Type', required=True)
    state = fields.Selection([
        ('new', 'New'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='Status', default='new', required=True)

    def action_approve(self):
        self.ensure_one()
        self.write({'state': 'approved'})
    
    def action_reject(self):
        self.ensure_one()
        self.write({'state': 'rejected'})