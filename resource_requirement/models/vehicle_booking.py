# -*- coding: utf-8 -*-

from odoo import fields, models
from datetime import datetime


class VehicleBooking(models.Model):
    _name = 'vehicle.booking'
    _description = 'Vehicle Booking'
    _rec_name = 'vehicle_requirement_id'

    vehicle_requirement_id = fields.Many2one(
        'vehicle.requirement', string='Vehicle Requirement')
    resource_id = fields.Many2one(
        'resource.requirement', related='vehicle_requirement_id.resource_id')
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle')
    start_date = fields.Datetime('Start Date')
    end_date = fields.Datetime('End Date')
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

    def action_assign_vehicle_booking(self):
        self.write({'state': 'assigned'})
        if all(booking.state == 'assigned' for booking in
                self.vehicle_requirement_id.vehicle_booking_ids):
            self.vehicle_requirement_id.write({'state': 'assigned'})
        if all(job_requirement.state == 'assigned' for job_requirement in
                self.vehicle_requirement_id.resource_id.vehicle_booking_ids) and all(
                vehicle_requirement.state == 'assigned' for vehicle_requirement
                in self.vehicle_requirement_id.resource_id.vehicle_requirement_ids):
            self.resource_id.write({'state': 'assigned'})

    def action_released_vehicle_booking(self):
        self.write({'state': 'completed'})
        today = datetime.now()
        self.end_date = today
        if all(booking.state == 'completed' for booking in
                self.vehicle_requirement_id.vehicle_booking_ids):
            self.vehicle_requirement_id.write({'state': 'completed'})
        if all(job_requirement.state == 'completed' for job_requirement in
                self.vehicle_requirement_id.resource_id.vehicle_booking_ids) and all(
                vehicle_requirement.state == 'completed' for vehicle_requirement
                in self.vehicle_requirement_id.resource_id.vehicle_requirement_ids):
            self.resource_id.write({'state': 'completed'})

    def _compute_is_team_operator(self):
        self.is_team_operator = False
        group_team_operator = self.env['res.users'].has_group(
            'resource_requirement.team_operator')
        if group_team_operator:
            self.is_team_operator = True
