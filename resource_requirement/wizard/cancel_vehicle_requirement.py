# -*- coding: utf-8 -*-

from odoo import fields, models


class CancelVehicleRequirementWizard(models.TransientModel):
    _name = 'cancel.vehicle.requirement.wizard'
    _description = 'Cancel Vehicle Requirement Wizard'

    reason = fields.Text(string='Reason', required=True)

    def cancel_vehicle_requirement_reason(self):
        self.ensure_one()
        context = self._context.copy()
        resource_id = context.get('resource_id')
        if resource_id:
            resource_obj = self.env['resource.requirement'].browse(
                resource_id)
        if context.get('active_id'):
            vehicle_requirement_obj = self.env[
                'vehicle.requirement'].browse(context.get('active_id'))
            vehicle_requirement_obj.notes = self.reason
            vehicle_requirement_obj.write({'state': 'canceled'})
            for vehicle_booking in vehicle_requirement_obj.vehicle_booking_ids:
                vehicle_booking.write({'state': 'canceled'})
        if resource_obj:
            if all(job_requirement.state == 'canceled' for job_requirement
                    in resource_obj.job_requirement_ids):
                resource_obj.write({'state': 'canceled'})
