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

from openerp.osv import fields, osv

class academy_course(osv.osv):
    _name = 'academy.course'
    _inherit = 'academy.course' 
    _columns = {
                'student_ids': fields.many2many('res.partner', 'course_address_rel', 'course_id', 'res_partner_address_id', 'Students', help='Students enrolled in the course'),
                'remaining_seats': fields.integer('Remaining seats', help='Remaining seats of the course'), 
                'complete': fields.boolean('Complete', help='Complete course. No more one can be enroled.'),
                }
    
academy_course()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: