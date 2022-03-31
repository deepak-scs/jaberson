# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, models


class ResourceRequirementReportPDF(models.AbstractModel):
    _name = 'report.resource_requirement.report_resource_requirement_pdf'
    _description = 'Resource Requirement Report PDF'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['resource.requirement'].browse(docids)
        return {
            'doc_model': 'resource.requirement',
            'docs': docs,
        }
