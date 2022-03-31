# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime
from dateutil.relativedelta import relativedelta


class ResourceRequirement(models.Model):
    _name = 'resource.requirement'
    _inherit = 'mail.thread'
    _description = 'Resource Requirement'
    _rec_name = 'name'
    _order = "sequence, name, id"

    name = fields.Char(
        'Requirement Number', required=True, index=True, copy=False,
        default='New')
    user_id = fields.Many2one(
        'res.users', string='Entry By', default=lambda self: self.env.user,
        copy=False)
    sequence = fields.Integer(
        'Sequence', default=1, help="Used to order stages. Lower is better.")
    partner_id = fields.Many2one('res.partner', string='CUSTOMER')
    poc = fields.Text(string='PoC')
    # order_id = fields.Many2one('sale.order', string="Quotation No")
    project_id = fields.Many2one('project.project', string="PROJECT")
    description_scope_of_work = fields.Text('Description (Scope Of Work)')
    remarks = fields.Text('Notes Remarks')
    start_date = fields.Datetime('START DATE')
    end_date = fields.Datetime('END DATE')
    duty_timing = fields.Float('Report for Duty Timing')
    do_end_time = fields.Datetime('DO End Time')
    quote_ref = fields.Char('QUOTE REF')
    cargo_description = fields.Text('Cargo Description')
    location_collection = fields.Text(string='Collection Location')
    # arrival_time_collection = fields.Datetime(
    #     'Collection Arrival Time', copy=False)
    location_delivery_id = fields.Many2one(
        'res.partner', string='DESTINATION')
    arrival_time_delivery = fields.Float(
        'ARRIVAL TIME', copy=False)
    state = fields.Selection([
        ('new', 'New'),
        ('pending', 'Pending'),
        ('assigned', 'Assigned'),
        ('postpone', 'Postponed'),
        ('canceled', 'Cancelled'),
        ('completed', 'Completed'),
    ], string='State', store=True, default='new', tracking=True)
    job_requirement_ids = fields.One2many(
        'job.requirement', 'resource_id',
        string='Resource Requirement', store=True)
    employee_booking_ids = fields.One2many(
        'employee.booking', 'resource_id',
        string='Employee Booking', store=True)
    vehicle_booking_ids = fields.One2many(
        'vehicle.booking', 'resource_id',
        string='Vehicle Booking', store=True)
    is_team_operator = fields.Boolean(
        compute='_compute_is_team_operator', string='Team Operator')
    employee_ids = fields.Many2many(
        'hr.employee', string='Employees',
        compute='_compute_employee_ids')
    vehicle_ids = fields.Many2many(
        'fleet.vehicle', string='Vehicles',
        compute='_compute_vehicle_ids')
    assigned_emp_ids = fields.Many2many(
        'hr.employee', string='Assigned Employees', copy=False)
    assigned_vehicle_ids = fields.Many2many(
        'fleet.vehicle', compute='_compute_assigned_vehicle_ids',
        string='Assigned Vehicles', copy=False)
    book_emp_count = fields.Integer(
        compute="_compute_book_emp_count", string='Employees Count')
    vehicle_requirement_ids = fields.One2many(
        'vehicle.requirement', 'resource_id')
    remaining_resources = fields.Integer(
        'Remaining Manpower for the day',
        compute='_compute_remaining_resources')
    remaining_resources_ids = fields.Many2many(
        'hr.employee', 'Remaining Manpower for the day list',
        compute='_compute_remaining_resources_ids')
    remaining_vehicle = fields.Integer(
        'Remaining vehicle for the Day',
        compute='_compute_remaining_vehicle')
    remaining_vehicle_ids = fields.Many2many(
        'fleet.vehicle', 'Remaining vehicle for the day list',
        compute='_compute_remaining_vehicle_ids')
    total_staff = fields.Char(
        'Assign and requested for staff',
        compute='_compute_total_staff')
    driver_ids = fields.Many2many(
        'hr.employee', 'driver_emp_rel', 'driver_id', 'employee_id',
        string='Driver', copy=False)

    def _compute_total_staff(self):
        total_number_of_position = 0
        total_number_of_assign = 0
        for rec in self.job_requirement_ids:
            total_number_of_position += rec.number_of_position
            if rec.state == 'assigned':
                total_number_of_assign += len(rec.employee_ids.ids)
        self.total_staff = str(
            'Assign staff ' + str(total_number_of_assign) + ' Out of ' + str(
                total_number_of_position))

    @api.onchange('job_requirement_ids')
    def _onchange_job_requirement_ids(self):
        self.assigned_emp_ids = False
        self.assigned_emp_ids = self.job_requirement_ids.employee_ids.ids

    def _compute_assigned_vehicle_ids(self):
        for rec in self:
            rec.assigned_vehicle_ids = False
            rec.assigned_vehicle_ids = rec.vehicle_requirement_ids.vehicle_ids.ids

    def _compute_remaining_vehicle(self):
        for rec in self:
            start_date = rec.start_date + relativedelta(
                hours=00, minutes=00, seconds=00)
            end_date = rec.start_date + relativedelta(
                hours=23, minutes=59, seconds=59)
            vehicle_bookings_obj = rec.env['vehicle.booking'].search([
                ('state', 'in', ('new', 'assigned')),
                ('start_date', '<=', end_date),
                ('end_date', '>=', start_date),
            ])
            total_vehicle = rec.env['fleet.vehicle'].search_count([])
            rec.remaining_vehicle = total_vehicle - len(
                vehicle_bookings_obj.vehicle_id.ids)

    def _compute_remaining_vehicle_ids(self):
        for rec in self:
            rec.remaining_vehicle_ids = False
            start_date = rec.start_date + relativedelta(
                hours=00, minutes=00, seconds=00)
            end_date = rec.start_date + relativedelta(
                hours=23, minutes=59, seconds=59)
            vehicle_bookings_obj = rec.env['vehicle.booking'].search([
                ('state', 'in', ('new', 'assigned')),
                ('start_date', '<=', end_date),
                ('end_date', '>=', start_date),
            ])
            vehicle_obj = rec.env['fleet.vehicle'].search([
                ('id', 'not in', vehicle_bookings_obj.vehicle_id.ids)
            ])
            rec.remaining_vehicle_ids = vehicle_obj.ids

    def _compute_remaining_resources(self):
        for rec in self:
            start_date = rec.start_date + relativedelta(
                hours=00, minutes=00, seconds=00)
            end_date = rec.start_date + relativedelta(
                hours=23, minutes=59, seconds=59)
            emp_bookings_obj = rec.env['employee.booking'].search([
                ('state', 'in', ('new', 'assigned')),
                ('start_date', '<=', end_date),
                ('end_date', '>=', start_date),
            ])
            total_emp = rec.env['hr.employee'].search_count([])
            rec.remaining_resources = total_emp - len(
                emp_bookings_obj.employee_id.ids)

    def _compute_remaining_resources_ids(self):
        for rec in self:
            rec.remaining_resources_ids = False
            start_date = rec.start_date + relativedelta(
                hours=00, minutes=00, seconds=00)
            end_date = rec.start_date + relativedelta(
                hours=23, minutes=59, seconds=59)
            emp_bookings_obj = rec.env['employee.booking'].search([
                ('state', 'in', ('new', 'assigned')),
                ('start_date', '<=', end_date),
                ('end_date', '>=', start_date),
            ])
            employee_obj = rec.env['hr.employee'].search([
                ('id', 'not in', emp_bookings_obj.employee_id.ids),
            ])
            rec.remaining_resources_ids = employee_obj.ids

    def _compute_book_emp_count(self):
        total_book_emp_count = 0
        for rec in self.job_requirement_ids:
            total_book_emp_count += len(rec.employee_ids.ids)
        self.book_emp_count = total_book_emp_count

    def _compute_is_team_operator(self):
        for rec in self:
            rec.is_team_operator = False
            group_team_operator = rec.env['res.users'].has_group(
                'resource_requirement.team_operator')
            if group_team_operator:
                rec.is_team_operator = True

    # @api.onchange('project_id')
    # def _onchange_project_id(self):
    #     self.job_requirement_ids = False

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'resource.requirement') or 'New'
        return super(ResourceRequirement, self).create(vals)

    def write(self, vals):
        res = super(ResourceRequirement, self).write(vals)
        if 'state' in vals:
            for rec in self.job_requirement_ids:
                rec.state = self.state
        return res

    def action_pending(self):
        self.write({'state': 'pending'})
        for job_requirement in self.job_requirement_ids:
            job_requirement.write({'state': 'pending'})
        for employee_booking in self.employee_booking_ids:
            employee_booking.write({'state': 'pending'})
        for vehicle_booking in self.vehicle_booking_ids:
            vehicle_booking.write({'state': 'pending'})
        for vehicle_requirement in self.vehicle_requirement_ids:
            vehicle_requirement.write({'state': 'pending'})

    def action_assign(self):
        for job_requirement in self.job_requirement_ids:
            job_requirement.write({'state': 'assigned'})
        for employee_booking in self.employee_booking_ids:
            employee_booking.write({'state': 'assigned'})
        for vehicle_booking in self.vehicle_booking_ids:
            vehicle_booking.write({'state': 'assigned'})
        self.write({'state': 'assigned'})
        for vehicle_requirement in self.vehicle_requirement_ids:
            vehicle_requirement.write({'state': 'assigned'})

    def action_released(self):
        today = datetime.now()
        for job_requirement in self.job_requirement_ids:
            if job_requirement.state != 'completed':
                job_requirement.write({
                    'end_date': today,
                    'state': 'completed',
                })
        for employee_booking in self.employee_booking_ids:
            if employee_booking.state != 'completed':
                employee_booking.write({
                    'end_date': today,
                    'state': 'completed',
                })
        for vehicle_booking in self.vehicle_booking_ids:
            if vehicle_booking.state != 'completed':
                vehicle_booking.write({
                    'end_date': today,
                    'state': 'completed',
                })
        for vehicle_requirement in self.vehicle_requirement_ids:
            vehicle_requirement.write({'state': 'completed'})
        self.write({'state': 'completed'})

    def action_cancel(self):
        context = dict(self.env.context or {})
        return {
            'name': 'Cancel Resource Requirement Reason',
            'target': 'new',
            'context': context,
            'type': 'ir.actions.act_window',
            'res_model': 'cancel.requirement.wizard',
            'search_view_id': self.env.ref(
                'resource_requirement.cancel_requirement_wizard_view_form').id,
            'views': [(False, 'form')],
        }

    def action_postpone(self):
        context = dict(self.env.context or {})
        return {
            'name': 'Postpone Resource Requirement Reason',
            'target': 'new',
            'context': context,
            'type': 'ir.actions.act_window',
            'res_model': 'postpone.requirement.wizard',
            'search_view_id': self.env.ref(
                'resource_requirement.postpone_requirement_wizard_view_form'
            ).id,
            'views': [(False, 'form')],
        }

    def action_update(self):
        context = dict(self.env.context or {})
        return {
            'name': 'Update Resource Requirement Reason',
            'target': 'new',
            'context': context,
            'type': 'ir.actions.act_window',
            'res_model': 'update.requirement.wizard',
            'search_view_id': self.env.ref(
                'resource_requirement.update_requirement_wizard_view_form').id,
            'views': [(False, 'form')],
        }

    def _compute_employee_ids(self):
        for rec in self:
            rec.employee_ids = False
            start_date = rec.start_date + relativedelta(
                hours=00, minutes=00, seconds=00)
            end_date = rec.start_date + relativedelta(
                hours=23, minutes=59, seconds=59)
            bookings_obj = rec.env['employee.booking'].search([
                ('state', 'in', ('new', 'assigned')),
                ('start_date', '<=', end_date),
                ('end_date', '>=', start_date),
            ])
            project_obj = rec.env['project.project'].browse(rec.project_id.id)
            if rec.job_requirement_ids.skill_ids:
                employee_obj = rec.env['hr.employee'].search([
                    ('id', 'not in', bookings_obj.employee_id.ids),
                    ('job_id', 'in', rec.job_requirement_ids.job_id.ids),
                    ('id', 'in', project_obj.employee_ids.ids),
                    ('employee_skill_ids.skill_id', 'in',
                        rec.job_requirement_ids.skill_ids.ids),
                ])
                rec.employee_ids = employee_obj.ids
            else:
                employee_obj = rec.env['hr.employee'].search([
                    ('id', 'not in', bookings_obj.employee_id.ids),
                    ('id', 'in', project_obj.employee_ids.ids),
                    ('job_id', 'in', rec.job_requirement_ids.job_id.ids),
                ])
                rec.employee_ids = employee_obj.ids

    def _compute_vehicle_ids(self):
        for rec in self:
            rec.vehicle_ids = False
            start_date = rec.start_date + relativedelta(
                hours=00, minutes=00, seconds=00)
            end_date = rec.start_date + relativedelta(
                hours=23, minutes=59, seconds=59)
            vehicle_booking_obj = rec.env['vehicle.booking'].search([
                ('state', 'in', ('new', 'assigned')),
                ('start_date', '<=', end_date),
                ('end_date', '>=', start_date),
            ])
            if rec.vehicle_requirement_ids:
                vehicle_obj = rec.env['fleet.vehicle'].search([
                    ('type_of_vehicle_id', 'in',
                        rec.vehicle_requirement_ids.vehicle_type_id.ids),
                    ('id', 'not in', vehicle_booking_obj.vehicle_id.ids)
                ])
                rec.vehicle_ids = vehicle_obj.ids
        # else:
        #     vehicle_obj = self.env['fleet.vehicle'].search([
        #         ('id', 'not in', vehicle_booking_obj.vehicle_id.ids),
        #     ])
        #     self.vehicle_ids = vehicle_obj.ids

    def action_book_employee(self):
        self.ensure_one()
        return {
            'name': _("Employee Booking"),
            'type': 'ir.actions.act_window',
            'res_model': 'employee.booking',
            'view_type': 'tree',
            'view_mode': 'list,form',
            'domain': [('resource_id', '=', self.id)],
            'context': {'group_by': 'employee_id'},
        }

    def name_get(self):
        result = []
        for rec in self:
            result.append(
                (rec.id, "%s %s" % (
                    rec.name, rec.project_id.name or '')))
        return result
