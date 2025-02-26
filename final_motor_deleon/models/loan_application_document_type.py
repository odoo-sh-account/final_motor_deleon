from odoo import api, fields, models

class LoanApplicationDocumentType(models.Model):
    _name = 'loan.application.document.type'
    _description = 'Loan Application Document Type'
    _order = 'name asc'

    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(string='Active', default=True)
    document_number = fields.Integer(string='Required Document Number', default=1)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Document type name already exists!"),
    ]
