# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import *


class VehicleRequirement(models.Model):
    _name = 'vehicle.requirement'
    _description = 'Vehicle Requirement'
    _rec_name = 'vehicle_type_id'

    resource_id = fields.Many2one(
        'resource.requirement', string='Resource Requirement')
    vehicle_type_id = fields.Many2one('vehicle.type', string='Vehicle Type')
    vehicle_ids = fields.Many2many('fleet.vehicle', string='Vehicle')
    number_of_vehicle = fields.Integer(string='Number of Vehicle')
    start_date = fields.Datetime('Start Date')
    end_date = fields.Datetime('End Date')
    notes = fields.Text('Notes/Remark')
    vehicle_booking_ids = fields.One2many(
        'vehicle.booking', 'vehicle_requirement_id',
        string='Vehicle Booking', store=True, copy=False)
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

    @api.model
    def create(self, vals):
        res = super(VehicleRequirement, self).create(vals)
        if res.vehicle_ids:
            res.vehicle_booking_ids = False
            for vehicle in res.vehicle_ids:
                if res.start_date and res.end_date:
                    sdate = res.start_date.date()
                    edate = res.end_date.date()
                    delta = edate - sdate
                    for i in range(delta.days + 1):
                        date_of_day = sdate + timedelta(days=i)
                        res.vehicle_booking_ids = [(0, 0, {
                            'vehicle_requirement_id': res.id,
                            'vehicle_id': vehicle.id,
                            'start_date': date_of_day,
                            'end_date': res.end_date,
                            'state': res.state,
                        })]
        return res

    def write(self, vals):
        res = super(VehicleRequirement, self).write(vals)
        if 'vehicle_ids' in vals:
            self.vehicle_booking_ids.unlink()
            for vehicle in self.vehicle_ids:
                sdate = self.start_date
                edate = self.end_date
                delta = edate - sdate
                for i in range(delta.days + 1):
                    date_of_day = sdate + timedelta(days=i)
                    self.vehicle_booking_ids = [(0, 0, {
                        'vehicle_requirement_id': self.id,
                        'vehicle_id': vehicle.id,
                        'start_date': date_of_day,
                        'end_date': self.end_date,
                        'state': self.state,
                    })]
        return res

    def unlink(self):
        vehicle_obj = self.env['vehicle.booking'].search(
            [('vehicle_requirement_id', 'in', self.ids)])
        if vehicle_obj:
            for rec in vehicle_obj:
                rec.unlink()
        return super(VehicleRequirement, self).unlink()

    def action_pending_vehicle(self):
        self.write({'state': 'pending'})
        for vehicle_booking in self.vehicle_booking_ids:
            vehicle_booking.write({'state': 'pending'})
        if all(job_requirement.state == 'pending' for job_requirement
                in self.resource_id.job_requirement_ids) and all(
                vehicle_requirement.state == 'pending' for vehicle_requirement
                in self.resource_id.vehicle_requirement_ids):
            self.resource_id.write({'state': 'pending'})

    def action_assign_vehicle(self):
        self.write({'state': 'assigned'})
        for vehicle_booking in self.vehicle_booking_ids:
            vehicle_booking.write({'state': 'assigned'})
        if all(job_requirement.state == 'assigned' for job_requirement
                in self.resource_id.job_requirement_ids) and all(
                vehicle_requirement.state == 'assigned' for vehicle_requirement
                in self.resource_id.vehicle_requirement_ids):
            self.resource_id.write({'state': 'assigned'})

    def action_postpone_vehicle(self):
        context = dict(self.env.context or {})
        context.update({
            'resource_id': self.resource_id.id
        })
        return {
            'name': 'Postpone Vehicle Requirement',
            'target': 'new',
            'context': context,
            'type': 'ir.actions.act_window',
            'res_model': 'postpone.vehicle.requirement.wizard',
            'search_view_id': self.env.ref(
                'resource_requirement.postpone_vehicle_requirement_wizard_view_form').id,
            'views': [(False, 'form')],
        }

    def action_update_vehicle(self):
        context = dict(self.env.context or {})
        context.update({
            'resource_id': self.resource_id.id
        })
        return {
            'name': 'Update Vehicle Requirement Reason',
            'target': 'new',
            'context': context,
            'type': 'ir.actions.act_window',
            'res_model': 'update.vehicle.requirement.wizard',
            'search_view_id': self.env.ref(
                'resource_requirement.update_vehicle_requirement_wizard_view_form').id,
            'views': [(False, 'form')],
        }

    def action_released_vehicle(self):
        today = datetime.now()
        self.write({'state': 'completed'})
        for vehicle_booking in self.vehicle_booking_ids:
            if vehicle_booking.state != 'completed':
                vehicle_booking.write({
                    'state': 'completed',
                    'end_date': today,
                })
        if all(job_requirement.state == 'completed' for job_requirement
                in self.resource_id.job_requirement_ids) and all(
                vehicle_requirement.state == 'completed' for vehicle_requirement
                in self.resource_id.vehicle_requirement_ids):
            self.resource_id.write({'state': 'completed'})

    def action_cancel_vehicle(self):
        context = dict(self.env.context or {})
        context.update({
            'resource_id': self.resource_id.id
        })
        return {
            'name': 'Cancel Vehicle Requirement Reason',
            'target': 'new',
            'context': context,
            'type': 'ir.actions.act_window',
            'res_model': 'cancel.vehicle.requirement.wizard',
            'search_view_id': self.env.ref(
                'resource_requirement.cancel_vehicle_requirement_wizard_view_form').id,
            'views': [(False, 'form')],
        }

    def _compute_is_team_operator(self):
        self.is_team_operator = False
        group_team_operator = self.env['res.users'].has_group(
            'resource_requirement.team_operator')
        if group_team_operator:
            self.is_team_operator = True
