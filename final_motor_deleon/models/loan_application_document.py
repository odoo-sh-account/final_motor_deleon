from odoo import api, fields, models
from odoo.exceptions import UserError


class LoanApplicationDocument(models.Model):
    _name = 'loan.application.document'
    _description = 'Loan Application Document'
    _order = 'sequence asc'

    sequence = fields.Integer(string='Sequence', default=1)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Document name already exists!"),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            application = self.env['loan.application'].browse(vals.get('application_id'))
            if application.state != 'draft':
                raise UserError("Cannot add documents to approved applications")
        return super().create(vals_list)

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