# -*- coding: utf-8 -*-

from odoo import fields, models


class CancelRequirementWizard(models.TransientModel):
    _name = 'cancel.requirement.wizard'
    _description = 'Cancel Requirement Wizard'

    reason = fields.Text(string='Reason', required=True)

    def cancel_requirement_reason(self):
        self.ensure_one()
        context = self._context.copy()
        if context.get('active_id'):
            requirement_obj = self.env[
                'resource.requirement'].browse(context.get('active_id'))
            requirement_obj.remarks = self.reason
            requirement_obj.write({'state': 'canceled'})
            for job_requirement in requirement_obj.job_requirement_ids:
                job_requirement.write({
                    'state': 'canceled',
                    'notes': self.reason,
                })
            for employee_booking in requirement_obj.employee_booking_ids:
                employee_booking.write({'state': 'canceled'})
            for vehicle_booking in requirement_obj.vehicle_booking_ids:
                vehicle_booking.write({'state': 'canceled'})
            for vehicle_requirement in requirement_obj.vehicle_requirement_ids:
                vehicle_requirement.write({
                    'state': 'canceled',
                    'notes': self.reason,
                })
