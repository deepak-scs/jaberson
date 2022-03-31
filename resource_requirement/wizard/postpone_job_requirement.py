# -*- coding: utf-8 -*-

from odoo import fields, models


class PostponeJobRequirementWizard(models.TransientModel):
    _name = 'postpone.job.requirement.wizard'
    _description = 'Postpone Job Requirement Wizard'

    reason = fields.Text(string='Reason', required=True)
    start_date = fields.Datetime('Start Date')
    end_date = fields.Datetime('End Date')

    def postpone_job_requirement_reason(self):
        self.ensure_one()
        context = self._context.copy()
        resource_id = context.get('resource_id')
        if resource_id:
            resource_obj = self.env['resource.requirement'].browse(
                resource_id)
        if context.get('active_id'):
            job_requirement_obj = self.env[
                'job.requirement'].browse(context.get('active_id'))
            job_requirement_obj.notes = self.reason
            job_requirement_obj.start_date = self.start_date
            job_requirement_obj.end_date = self.end_date
            job_requirement_obj.write({'state': 'new'})
            for employee_booking in job_requirement_obj.employee_booking_ids:
                employee_booking.write({
                    'state': 'new',
                    'start_date': self.start_date,
                    'end_date': self.end_date,
                })
        if resource_obj:
            if all(vehicle_requirement.state == 'new' for vehicle_requirement
                    in resource_obj.vehicle_requirement_ids):
                resource_obj.write({'state': 'new'})
