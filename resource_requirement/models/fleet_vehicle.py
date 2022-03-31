# -*- coding: utf-8 -*-
from odoo import api, fields, models
from dateutil.relativedelta import relativedelta
from datetime import datetime


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    type_of_vehicle_id = fields.Many2one(
        'vehicle.type', string='Type of Vehicle')

    def name_get(self):
        result = []
        for rec in self:
            result.append(
                (rec.id, "%s" % (
                    rec.license_plate or rec.model_id.name)))
        return result

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False,
                access_rights_uid=None):
        context = self._context.copy()
        if context.get('is_vehicle_requirement'):
            today = datetime.now()
            vehicle_list = []
            start_date = today + relativedelta(
                hours=00, minutes=00, seconds=00)
            end_date = today + relativedelta(
                hours=23, minutes=59, seconds=59)
            bookings_vehicle_obj = self.env['vehicle.booking'].search([
                ('state', 'in', ('new', 'assigned')),
                ('start_date', '<=', end_date),
                ('end_date', '>=', start_date),
            ])
            for vehicle in bookings_vehicle_obj:
                vehicle_list.append(vehicle.vehicle_id.id)
            args.append((('id', 'not in', vehicle_list)))
            return super(FleetVehicle, self)._search(
                args, offset=offset, limit=limit, order=order, count=count,
                access_rights_uid=access_rights_uid)
        if context.get('is_vehicle_requirement_line'):
            if context.get('default_start_date') and context.get(
                    'default_end_date'):
                vehicle_list = []
                start_date = datetime.strptime(
                    context.get('default_start_date'), '%Y-%m-%d %H:%M:%S')
                end_date = datetime.strptime(
                    context.get('default_end_date'), '%Y-%m-%d %H:%M:%S')
                start_date = start_date + relativedelta(
                    hours=00, minutes=00, seconds=00)
                end_date = end_date + relativedelta(
                    hours=23, minutes=59, seconds=59)
                bookings_vehicle_obj = self.env['vehicle.booking'].search([
                    ('state', 'in', ('new', 'assigned')),
                    ('start_date', '<=', end_date),
                    ('end_date', '>=', start_date),
                ])
                for vehicle in bookings_vehicle_obj:
                    vehicle_list.append(vehicle.vehicle_id.id)
                args.append((('id', 'not in', vehicle_list)))
        return super(FleetVehicle, self)._search(
            args, offset=offset, limit=limit, order=order, count=count,
            access_rights_uid=access_rights_uid)
