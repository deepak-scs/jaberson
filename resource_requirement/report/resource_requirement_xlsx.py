# -*- coding: utf-8 -*-

from odoo import models

class ResourceRequirementXlsx(models.AbstractModel):
    _name = 'report.resource_requirement_xlsx'
    _description = 'Resource Requirement Report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        header_format = workbook.add_format({
            'align': 'center', 'font_size': 13, 'bold': True, 'border': 1})
        header_line_format = workbook.add_format(
            {'align': 'center', 'border': 1, 'font_size': 10,
                'text_wrap': True})
        worksheet = workbook.add_worksheet()
        worksheet.write('A1', 'Date and Location', header_format)
        worksheet.write('B1', 'Customer and Poc', header_format)
        worksheet.write('C1', 'Job Reference', header_format)
        worksheet.write('D1', 'Site', header_format)
        worksheet.write('E1', 'Assign vehicel number', header_format)
        worksheet.write('F1', 'Assign Employee', header_format)
        worksheet.write('G1', 'Notes and Cargo Description', header_format)
        worksheet.write('H1', 'Reporting Time', header_format)

        row = 1
        worksheet.set_column('A:A', 20)
        worksheet.set_column('B:B', 20)
        worksheet.set_column('C:C', 20)
        worksheet.set_column('D:D', 20)
        worksheet.set_column('E:E', 20)
        worksheet.set_column('F:F', 20)
        worksheet.set_column('G:G', 40)
        worksheet.set_column('H:H', 20)
        for rec in partners:
            duty_timing = '{0:02.0f}:{1:02.0f}'.format(
                *divmod(rec.duty_timing * 60, 60))
            date_location = (
                str(rec.start_date.date()) + '\n' + str(
                    rec.location_collection or ''))
            customer_poc = (
                str(rec.partner_id.name) + '\n' + str(rec.poc or ''))
            assigned_emp = ''
            assigned_vehicel = ''
            for emp in rec.assigned_emp_ids:
                assigned_emp += str(emp.name + ', ')
            for veh in rec.assigned_vehicle_ids:
                assigned_vehicel += str(veh.license_plate + ', ')
            notes_cargo_des = (str(rec.remarks or '') + '\n' + (
                str(rec.cargo_description or '')))
            worksheet.write(row, 0, date_location, header_line_format)
            worksheet.write(row, 1, customer_poc, header_line_format)
            worksheet.write(row, 2, rec.quote_ref or '', header_line_format)
            worksheet.write(
                row, 3, rec.project_id.short_name or rec.project_id.name,
                header_line_format)
            worksheet.write(row, 4, assigned_vehicel, header_line_format)
            worksheet.write(row, 5, assigned_emp, header_line_format)
            worksheet.write(row, 6, notes_cargo_des, header_line_format)
            worksheet.write(row, 7, duty_timing, header_line_format)
            row += 1
