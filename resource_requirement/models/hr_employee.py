# -*- coding: utf-8 -*-

from odoo import api, fields, models
from dateutil.relativedelta import relativedelta
from datetime import datetime
from random import randint


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def _get_default_color(self):
        return randint(1, 11)

    color = fields.Integer('Color', default=_get_default_color)
    short_name = fields.Char(string='Short Name')
    is_driver = fields.Boolean(string='Driver')

    def name_get(self):
        result = []
        for rec in self:
            result.append(
                (rec.id, "%s" % (
                    rec.short_name or rec.name)))
        return result

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False,
                access_rights_uid=None):
        context = self._context.copy()
        if context.get('is_warehouse_manpower'):
            today = datetime.now()
            emp_list = []
            start_date = today + relativedelta(
                hours=00, minutes=00, seconds=00)
            end_date = today + relativedelta(
                hours=23, minutes=59, seconds=59)
            bookings_obj = self.env['employee.booking'].search([
                ('state', 'in', ('new', 'assigned')),
                ('start_date', '<=', end_date),
                ('end_date', '>=', start_date),
            ])
            for emp in bookings_obj:
                emp_list.append(emp.employee_id.id)
            args.append((('id', 'not in', emp_list)))
            return super(HrEmployee, self)._search(
                args, offset=offset, limit=limit, order=order, count=count,
                access_rights_uid=access_rights_uid)
        assigne_employees_list = []
        employees_in_project = []
        employee_with_skill = []
        if context.get('is_job_requirement'):
            if context.get('default_start_date') and context.get(
                    'default_end_date'):
                start_date = datetime.strptime(
                    context.get('default_start_date'), '%Y-%m-%d %H:%M:%S')
                end_date = datetime.strptime(
                    context.get('default_end_date'), '%Y-%m-%d %H:%M:%S')
                start_date = start_date + relativedelta(
                    hours=00, minutes=00, seconds=00)
                end_date = end_date + relativedelta(
                    hours=23, minutes=59, seconds=59)
                bookings_obj = self.env['employee.booking'].search([
                    ('state', 'in', ('new', 'assigned')),
                    ('start_date', '<=', end_date),
                    ('end_date', '>=', start_date),
                ])
                assigne_employees_list = bookings_obj.employee_id.ids
            if context.get('default_project_id'):
                project_obj = self.env['project.project'].browse(
                    context.get('default_project_id'))
                employees_in_project = project_obj.employee_ids.ids
            if context.get('default_skill_ids'):
                skill_ids = context.get('default_skill_ids')[0][2]
                hr_skill_obj = self.env['hr.employee.skill'].search([
                    ('skill_id', 'in', skill_ids)
                ])
                if skill_ids:
                    employee_with_skill = hr_skill_obj.employee_id.ids
                    all_employee = list(set(employees_in_project) & set(
                        employee_with_skill))
                    all_employee = list(set(all_employee) ^ set(
                        assigne_employees_list))
                    args.append((('id', 'in', all_employee)))
                else:
                    all_employee = list(set(employees_in_project))
                    all_employee = list(set(all_employee) ^ set(
                        assigne_employees_list))
                    args.append((('id', 'in', all_employee)))
        return super(HrEmployee, self)._search(
            args, offset=offset, limit=limit, order=order, count=count,
            access_rights_uid=access_rights_uid)

class EmployeeSkill(models.Model):
    _inherit = 'hr.employee.skill'

    expiry_date = fields.Datetime('Expiry Date')
