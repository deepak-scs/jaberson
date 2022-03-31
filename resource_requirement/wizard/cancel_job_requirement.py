# -*- coding: utf-8 -*-

from odoo import fields, models


class CancelJobRequirementWizard(models.TransientModel):
    _name = 'cancel.job.requirement.wizard'
    _description = 'Cancel Job Requirement Wizard'

    reason = fields.Text(string='Reason', required=True)

    def cancel_job_requirement_reason(self):
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
            job_requirement_obj.write({'state': 'canceled'})
            for employee_booking in job_requirement_obj.employee_booking_ids:
                employee_booking.write({'state': 'canceled'})
        if resource_obj:
            if all(vehicle_requirement.state == 'canceled' for vehicle_requirement
                    in resource_obj.vehicle_requirement_ids):
                resource_obj.write({'state': 'canceled'})
