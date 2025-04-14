# -*- coding: utf-8 -*-

from odoo import models, fields


class Commission(models.Model):
    _name = 'commission.commission'
    _description = 'Commission'

    name = fields.Char(string='Name', required=True)
    amount = fields.Float(string='Amount')
    date = fields.Date(string='Date')

