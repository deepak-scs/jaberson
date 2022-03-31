# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import datetime
from dateutil.relativedelta import relativedelta


class EmployeeBooking(models.Model):
    _name = 'employee.booking'
    _description = 'Employee Booking'
    _rec_name = 'job_requirement_id'

    job_requirement_id = fields.Many2one('job.requirement')
    job_id = fields.Many2one('hr.job', 'Job Position')
    resource_id = fields.Many2one(
        'resource.requirement', related='job_requirement_id.resource_id')
    project_id = fields.Many2one(
        'project.project', string="PROJECT")
    number_of_position = fields.Integer('Number of Position', copy=False)
    skill_ids = fields.Many2many(
        'hr.skill', string='Skill', store=True, copy=False)
    start_date = fields.Datetime('Start Date')
    end_date = fields.Datetime('End Date')
    employee_id = fields.Many2one('hr.employee', string='Assigned Manpower')
    remaining_employee_ids = fields.Many2many(
        'hr.employee', string='Remaining Manpower',
        compute='_compute_remaining_employee_ids', copy=False)
    is_team_operator = fields.Boolean(
        compute='_compute_is_team_operator', string='Team Operator')
    state = fields.Selection([
        ('new', 'New'),
        ('pending', 'Pending'),
        ('assigned', 'Assigned'),
        ('postpone', 'Postponed'),
        ('canceled', 'Cancelled'),
        ('completed', 'Completed'),
    ], string='State', store=True, default='new')

    def _compute_remaining_employee_ids(self):
        for rec in self:
            rec.remaining_employee_ids = False
            # today = datetime.now()
            # start_date = today + relativedelta(
            #     hours=00, minutes=00, seconds=00)
            # end_date = today + relativedelta(
            #     hours=23, minutes=59, seconds=59)
            bookings_obj = rec.env['employee.booking'].search([
                ('state', 'in', ('new', 'assigned')),
                ('start_date', '<=', rec.end_date),
                ('end_date', '>=', rec.start_date),
            ])
            project_obj = rec.env['project.project'].browse(rec.project_id.id)
            employee_obj = rec.env['hr.employee'].search([
                ('id', 'not in', bookings_obj.employee_id.ids),
                ('job_id', '=', rec.job_id.id),
                ('id', 'in', project_obj.employee_ids.ids),
            ])
            rec.remaining_employee_ids = employee_obj.ids

    def action_assign_booking(self):
        self.write({'state': 'assigned'})
        if all(booking.state == 'assigned' for booking in
                self.job_requirement_id.employee_booking_ids):
            self.job_requirement_id.write({'state': 'assigned'})
        if all(job_requirement.state == 'assigned' for job_requirement in
                self.job_requirement_id.resource_id.employee_booking_ids) and all(
                vehicle_requirement.state == 'assigned' for vehicle_requirement
                in self.job_requirement_id.resource_id.vehicle_requirement_ids):
            self.resource_id.write({'state': 'assigned'})

    def action_released_booking(self):
        self.write({'state': 'completed'})
        today = datetime.now()
        self.end_date = today
        if all(booking.state == 'completed' for booking in
                self.job_requirement_id.employee_booking_ids):
            self.job_requirement_id.write({'state': 'completed'})
        if all(job_requirement.state == 'completed' for job_requirement in
                self.job_requirement_id.resource_id.employee_booking_ids) and all(
                vehicle_requirement.state == 'completed' for vehicle_requirement
                in self.job_requirement_id.resource_id.vehicle_requirement_ids):
            self.resource_id.write({'state': 'completed'})

    # def action_cancel_booking(self):
    #     self.write({'state': 'canceled'})
    #     if all(booking.state == 'canceled' for booking in
    #             self.job_requirement_id.employee_booking_ids):
    #         self.job_requirement_id.write({'state': 'canceled'})
    #     if all(job_requirement.state == 'canceled' for job_requirement in
    #             self.job_requirement_id.resource_id.employee_booking_ids):
    #         self.resource_id.write({'state': 'canceled'})

    def _compute_is_team_operator(self):
        self.is_team_operator = False
        group_team_operator = self.env['res.users'].has_group(
            'resource_requirement.team_operator')
        if group_team_operator:
            self.is_team_operator = True
