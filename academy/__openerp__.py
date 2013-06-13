# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
'name': 'academy',
'version': '0.1',
'category': 'Generic Modules',
'description': """Academy module description""",
'author': 'zikzakmedia',
'website': 'http://www.zikzakmedia.com',
'depends': ['base'],
'init_xml': [],
'update_xml': [ 
            'academy_view.xml',
            'academy_wizard.xml',
            'wizard/wizard_academy.xml',
            'workflow/academy_workflow.xml'
            'academy_view.xml',
            'security/academy_security.xml',
            'security/ir.model.access.csv',
],
'demo_xml': [],
'installable': True,
}