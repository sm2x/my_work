# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Meeting Minutes for Construction and Contracating Projects',
    'currency': 'EUR',
    'price': 10.0,
    'version': '1.1',

    'depends': [
        'print_meeting_minutes',
        'odoo_job_costing_management',
    ],
    'license': 'Other proprietary',
    'category': 'Projects',
    'summary': 'Project Meeting Minutes for Construction and Contracating Projects and Jobs',
    'description': """
  Project Meeting Minutes
  
 This module allow print project meeting minutes.
Print Meeting Minutes
Print Meeting Minutes. Print Report of Meeting.
This module allow you to add minutes of meetings and print pdf report.
Print Report of Meeting
Print Report of 
Print  of Meeting
 Report of Meeting
print meeting
meeting minutes
meeting minute
report meeting
calender meeting
calendar meeting
report calendar
Meetings (Week)
Click to schedule a new meeting.
meeting Attendees
Attendees
The calendar is shared between employees and fully integrated with other applications such as the employee holidays or the business opportunities.    
Print meetings
Print calendar
Calendar meetings
Print customer meetings
customer meetings

job cost sheet
Odoo Job Costing And Job Cost Sheet (Contracting)
Odoo job cost sheet
job cost sheet odoo
contracting odoo
odoo construction
job costing (Contracting)
odoo job costing (Contracting)
odoo job costing Contracting
job order odoo
work order odoo
job Contracting
job costing
job cost Contracting
odoo Contracting
Contracting odoo job
Jobs
Jobs/Configuration
Jobs/Configuration/Job Types
Jobs/Configuration/Stages
Jobs/Job Costs
Jobs/Job Costs/Job Cost Sheets
Jobs/Job Orders
Jobs/Job Orders/Job Notes
Jobs/Job Orders/Job Orders
Jobs/Job Orders/Project Issues
BOQ
Job Costing
Notes
Project Report
Task Report
Jobs/Materials / BOQ 
Jobs/Materials / BOQ /Material Requisitions/ BOQ
Jobs/Materials / BOQ /Materials
Jobs/Projects
Jobs/Projects/Project Budgets
Jobs/Projects/Project Notes
Jobs/Projects/Projects
Jobs/Sub Contractors 
Jobs/Sub Contractors /Sub Contractors
material requision odoo
Contracting
job Contracting
job sheet
job cost Contracting
job cost plan
costing
cost Contracting
subcontracting
Email: contact@probuse.com for more details.
This module provide Construction Management Related Activity.
Construction
Construction Projects
Budgets
Notes
Materials
Material Request For Job Orders
Add Materials
Job Orders
Create Job Orders
Job Order Related Notes
Issues Related Project
Vendors
Vendors / Contractors

Construction Management
Construction Activity
Construction Jobs
Job Order Construction
Job Orders Issues
Job Order Notes
Construction Notes
Job Order Reports
Construction Reports
Job Order Note
Construction app
Construction 

Construction Management

This module provide feature to manage Construction Management activity.
Menus:
Construction
Construction/Configuration
Construction/Configuration /Stages
Construction/Construction
Construction/Construction/Budgets
Construction/Construction/Notes
Construction/Construction/Projects
Construction/Job Orders
Construction/Job Orders /Issues
Construction/Job Orders /Job Orders
Construction/Job Orders /Notes
Construction/Materials / BOQ
Construction/Materials /Material Requisitions / BOQ
Construction/Materials /Materials
Construction/Vendors
Construction/Vendors /Contractors
Defined Reports
Notes
Project Report
Task Report
Construction Project - Project Manager
real estate property
propery management
bill of material
Material Planning On Job Order

Bill of Quantity On Job Order
Bill of Quantity construction
job costing
job cost sheet
cost sheet
project cost sheet
project planning
project sheet cost
job costing plan
Construction cost sheet
Construction job cost sheet
Construction jobs
Construction job sheet
Construction material
Construction labour
Construction overheads
Construction sheet plan
costing
workshop
job workshop
workshop
jobs
cost centers
Construction purchase order
Construction activities
Basic Job Costing
Job Costing Example
job order costing
job order
job orders
Tracking Labor
Tracking Material
Tracking Overhead
overhead
material plan
job overhead
job labor
Job Cost Sheet
Example For Larger Job
Job costing is a method of costing applied in industries where production is measured in terms of completed jobs. Industries where job costing is generally applied are Printing Press. Automobile Garage, Repair workshops, Ship Building, Foundry and other similar manufacturing units which manufacture to customers� specific requirements.

Job costing is a method of costing whereby cost is compiled for a job or work order. The production is against customer�s orders and not for stock. The cost is not related to the unit of production but is a cost for the job, e. g printing of 5000 ledger sheets, repairs of 50 equipment�s, instead of printing one sheet or repair of one equipment.

The elements of cost comprising Prime Cost viz. direct materials, direct labour and direct expenses are charged directly to the jobs concerned, the overhead charged to a job is an apportioned portion of the departmental overhead.
Advantages of Job Order Costing

Features of Job Costing
Enabling Job Costing
Creating Cost Centres for Job Costing
project job cost
project job costing
project job contracting
project job contract
job contract
jobs contract
construction
Construction app
Construction odoo
odoo Construction

    """,
    'images': ['static/description/image.jpg'],
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'live_test_url': 'https://youtu.be/Vd4VM-QkMp4',

    'data': [
        'views/calendar_event_view.xml',
        'views/jobcost_view.xml',
        'views/project_view.xml',
        'views/task_view.xml',
        'report/jobcost_meeting_report.xml',
    ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
