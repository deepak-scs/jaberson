# -*- coding: utf-8 -*-
from odoo import fields, models


class Project(models.Model):
    _inherit = "project.project"

    employee_ids = fields.Many2many('hr.employee', string='Member')
    short_name = fields.Char(string='Short Name')

    def name_get(self):
        result = []
        for rec in self:
            result.append(
                (rec.id, "%s" % (
                    rec.short_name or rec.name)))
        return result


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_internal_staffs = fields.Boolean(string='Internal Staffs?')
