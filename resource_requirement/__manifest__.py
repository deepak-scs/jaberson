# -*- coding: utf-8 -*-

{
    "name": "Resource Requirement",
    "version": "14.0.1.0.0",
    "depends": [
        "hr",
        "hr_skills",
        "project",
        "fleet",
        "sale_management",
        "contacts",
        "report_xlsx",
    ],
    "author": "Serpent Consulting Services Pvt. Ltd.",
    "website": "http://www.serpentcs.com",
    "maintainer": "Serpent Consulting Services Pvt. Ltd.",
    "category": "Human Resources/Employees",
    "description": """ """,
    "summary": """ """,
    'data': [
        'security/ir.model.access.csv',
        'security/resource_requirement_security.xml',
        'data/ir_sequence_data.xml',
        'views/templates.xml',
        'views/resource_requirement_views.xml',
        'views/job_requirement_views.xml',
        'views/vehicle_type_views.xml',
        'views/project_views.xml',
        'views/employee_booking_views.xml',
        'views/vehicle_requirement_views.xml',
        'views/in_warehouse_manpower_views.xml',
        'views/hr_skill_views.xml',
        'views/employee_skill_expiry_date_views.xml',
        'views/vehicle_booking_views.xml',
        'views/fleet_vehicle_views.xml',
        'report/resource_requirement_xlsx_views.xml',
        'report/report_resource_requirement_pdf.xml',
        'wizard/cancel_requirement_views.xml',
        'wizard/postpone_requirement_views.xml',
        'wizard/update_requirement_views.xml',
        'wizard/cancel_job_requirement_views.xml',
        'wizard/cancel_vehicle_requirement_views.xml',
        'wizard/update_vehicle_requirement_views.xml',
        'wizard/postpone_vehicle_requirement_views.xml',
        'wizard/postpone_job_requirement_views.xml',
        'wizard/update_jobs_requirement_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
