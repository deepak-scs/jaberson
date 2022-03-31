# -*- coding: utf-8 -*-

from odoo import fields, models


class VehicleType(models.Model):
    _name = 'vehicle.type'
    _rec_name = 'name'
    _description = 'Vehicle Type'

    name = fields.Char(string='Vehicle Name')

    # @api.model
    # def _search(self, args, offset=0, limit=None, order=None, count=False,
    #             access_rights_uid=None):
    #     context = self._context.copy()
    #     if context.get('is_vehicle_requirement'):
    #         vehicle_bookings_obj = self.env['vehicle.requirement'].search([
    #             ('state', '=', 'assigned'),
    #         ])
    #         vehicle_list = []
    #         if vehicle_bookings_obj:
    #             for vehicle in vehicle_bookings_obj:
    #                 vehicle_list.append(vehicle.vehicle_id.id)
    #             args.append((('id', 'not in', vehicle_list)))
    #     return super(VehicleType, self)._search(
    #         args, offset=offset, limit=limit, order=order, count=count,
    #         access_rights_uid=access_rights_uid)
