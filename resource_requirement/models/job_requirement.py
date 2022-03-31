# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import *


class JobRequirement(models.Model):
    _name = 'job.requirement'
    _inherit = 'mail.thread'
    _description = 'Job Requirement'
    _rec_name = 'name'

    name = fields.Char(
        string="Requirement Number", readonly=True, required=True,
        copy=False, default='New')
    resource_id = fields.Many2one(
        'resource.requirement', string='Resource Requirement')
    project_id = fields.Many2one(
        'project.project', string="PROJECT")
    job_id = fields.Many2one('hr.job', 'Job Position')
    start_date = fields.Datetime('Start Date', copy=False)
    end_date = fields.Datetime('End Date', copy=False)
    number_of_position = fields.Integer('Number of Position', copy=False)
    skill_ids = fields.Many2many(
        'hr.skill', string='Skill', store=True, copy=False)
    description_scope_of_work = fields.Text(
        'Description (Scope Of Work)',
        related='resource_id.description_scope_of_work')
    employee_ids = fields.Many2many(
        'hr.employee', string='Employee', copy=False)
    is_team_operator = fields.Boolean(
        compute='_compute_is_team_operator', string='Team Operator')
    state = fields.Selection([
        ('new', 'New'),
        ('pending', 'Pending'),
        ('assigned', 'Assigned'),
        ('postpone', 'Postponed'),
        ('canceled', 'Cancelled'),
        ('completed', 'Completed'),
    ], string='State', store=True, default='new', tracking=True)
    notes = fields.Text('Notes Remarks')
    employee_booking_ids = fields.One2many(
        'employee.booking', 'job_requirement_id',
        string='Employee Booking', store=True, copy=False)


    @api.model
    def create(self, vals):
        res = super(JobRequirement, self).create(vals)
        if vals.get('name', 'New') == 'New':
            res.name = self.env['ir.sequence'].next_by_code(
                'job.requirement') or 'New'
        if res.employee_ids:
            res.employee_booking_ids = False
            for employee in res.employee_ids:
                if res.start_date and res.end_date:
                    sdate = res.start_date.date()
                    edate = res.end_date.date()
                    delta = edate - sdate
                    for i in range(delta.days + 1):
                        date_of_day = sdate + timedelta(days=i)
                        res.employee_booking_ids = [(0, 0, {
                            'job_requirement_id': res.id,
                            'job_id': res.job_id.id,
                            'project_id': res.project_id.id,
                            'number_of_position': res.number_of_position,
                            'skill_ids': res.skill_ids.ids,
                            'employee_id': employee.id,
                            'start_date': date_of_day,
                            'end_date': res.end_date,
                            'state': res.state,
                        })]
        return res

    def write(self, vals):
        res = super(JobRequirement, self).write(vals)
        if 'employee_ids' in vals:
            self.employee_booking_ids.unlink()
            for employee in self.employee_ids:
                sdate = self.start_date
                edate = self.end_date
                delta = edate - sdate
                for i in range(delta.days + 1):
                    date_of_day = sdate + timedelta(days=i)
                    self.employee_booking_ids = [(0, 0, {
                        'job_requirement_id': self.id,
                        'job_id': self.job_id.id,
                        'project_id': self.project_id.id,
                        'number_of_position': self.number_of_position,
                        'skill_ids': self.skill_ids.ids,
                        'employee_id': employee.id,
                        'start_date': date_of_day,
                        'end_date': self.end_date,
                        'state': self.state,
                    })]
        return res

    def unlink(self):
        booking_obj = self.env['employee.booking'].search(
            [('job_requirement_id', 'in', self.ids)])
        if booking_obj:
            for rec in booking_obj:
                rec.unlink()
        return super(JobRequirement, self).unlink()

    def _compute_is_team_operator(self):
        self.is_team_operator = False
        group_team_operator = self.env['res.users'].has_group(
            'resource_requirement.team_operator')
        if group_team_operator:
            self.is_team_operator = True

    @api.onchange('project_id')
    def _onchange_project(self):
        self.employee_ids = False

    def action_assign_job(self):
        self.write({'state': 'assigned'})
        for employee_booking in self.employee_booking_ids:
            employee_booking.write({'state': 'assigned'})
        if all(job_requirement.state == 'assigned' for job_requirement in
                self.resource_id.employee_booking_ids) and all(
                vehicle_requirement.state == 'assigned' for vehicle_requirement
                in self.resource_id.vehicle_requirement_ids):
            self.resource_id.write({'state': 'assigned'})

    def action_pending_job(self):
        self.ensure_one()
        self.write({'state': 'pending'})
        for employee_booking in self.employee_booking_ids:
            employee_booking.write({'state': 'pending'})
        if all(job_requirement.state == 'pending' for job_requirement in
                self.resource_id.employee_booking_ids) and all(
                vehicle_requirement.state == 'pending' for vehicle_requirement
                in self.resource_id.vehicle_requirement_ids):
            self.resource_id.write({'state': 'pending'})

    def action_postpone_job(self):
        context = dict(self.env.context or {})
        context.update({
            'resource_id': self.resource_id.id
        })
        return {
            'name': 'Postpone Job Requirement',
            'target': 'new',
            'context': context,
            'type': 'ir.actions.act_window',
            'res_model': 'postpone.job.requirement.wizard',
            'search_view_id': self.env.ref(
                'resource_requirement.postpone_job_requirement_wizard_view_form').id,
            'views': [(False, 'form')],
        }

    def action_update_job(self):
        self.ensure_one()
        context = dict(self.env.context or {})
        context.update({
            'resource_id': self.resource_id.id
        })
        return {
            'name': 'Update Job Requirement Reason',
            'target': 'new',
            'context': context,
            'type': 'ir.actions.act_window',
            'res_model': 'update.job.requirement.wizard',
            'search_view_id': self.env.ref(
                'resource_requirement.update_jobs_requirement_wizard_view_form').id,
            'views': [(False, 'form')],
        }

    def action_released_job(self):
        today = datetime.now()
        self.write({'state': 'completed'})
        for employee_booking in self.employee_booking_ids:
            if employee_booking.state != 'completed':
                employee_booking.write({
                    'state': 'completed',
                    'end_date': today,
                })
        if all(job_requirement.state == 'completed' for job_requirement in
                self.resource_id.employee_booking_ids) and all(
                vehicle_requirement.state == 'completed' for vehicle_requirement
                in self.resource_id.vehicle_requirement_ids):
            self.resource_id.write({'state': 'completed'})

    def action_cancel_job(self):
        context = dict(self.env.context or {})
        context.update({
            'resource_id': self.resource_id.id
        })
        return {
            'name': 'Cancel Job Requirement Reason',
            'target': 'new',
            'context': context,
            'type': 'ir.actions.act_window',
            'res_model': 'cancel.job.requirement.wizard',
            'search_view_id': self.env.ref(
                'resource_requirement.cancel_job_requirement_wizard_view_form').id,
            'views': [(False, 'form')],
        }

    def name_get(self):
        result = []
        for rec in self:
            result.append(
                (rec.id, "%s %s" % (rec.name, rec.project_id.name or '')))
        return result
