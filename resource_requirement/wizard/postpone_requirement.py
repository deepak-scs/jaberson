# -*- coding: utf-8 -*-

from odoo import fields, models


class PostponeRequirementWizard(models.TransientModel):
    _name = 'postpone.requirement.wizard'
    _description = 'Postpone Requirement Wizard'

    reason = fields.Text(string='Reason', required=True)
    start_date = fields.Datetime('Start Date')
    end_date = fields.Datetime('End Date')

    def postpone_requirement_reason(self):
        self.ensure_one()
        context = self._context.copy()
        if context.get('active_id'):
            requirement_obj = self.env[
                'resource.requirement'].browse(context.get('active_id'))
            requirement_obj.remarks = self.reason
            requirement_obj.start_date = self.start_date
            requirement_obj.end_date = self.end_date
            requirement_obj.write({'state': 'new'})
            for job_requirement in requirement_obj.job_requirement_ids:
                job_requirement.write({
                    'state': 'new',
                    'notes': self.reason,
                    'start_date': self.start_date,
                    'end_date': self.end_date,
                })
            for employee_booking in requirement_obj.employee_booking_ids:
                employee_booking.write({
                    'state': 'new',
                    'start_date': self.start_date,
                    'end_date': self.end_date,
                })
            for vehicle_booking in requirement_obj.vehicle_booking_ids:
                vehicle_booking.write({
                    'state': 'new',
                    'start_date': self.start_date,
                    'end_date': self.end_date,
                })
            for vehicle_requirement in requirement_obj.vehicle_requirement_ids:
                vehicle_requirement.write({
                    'state': 'new',
                    'notes': self.reason,
                    'start_date': self.start_date,
                    'end_date': self.end_date,
                })
