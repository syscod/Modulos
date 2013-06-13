<<<<<<< HEAD
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
=======
# -*- encoding: utf-8 -*-
############################################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2010 Zikzakmedia S.L. (<http://www.zikzakmedia.com>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
>>>>>>> 45445c0e2e4c781eeb3d7bb37ed12be62767a666
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
<<<<<<< HEAD
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv

class academy_wizard(osv.osv_memory):
    
    _name = 'academy.wizard'
    _columns = {
                'classroom_info_updates': fields.integer('Info Updates', readonly=True),
                'classroom_origen': fields.integer('Origen', required=True),
                'classroom_update': fields.integer('Update', required=True),
                'state':fields.selection([ ('first','First'), ('done','Done'), ],'State'),
                }
    
    _defaults = {
                 'state': lambda *a: 'first', 
                 }
    
    def update_classrooms(self, cr, uid, ids, data, context=None):
        form = self.browse(cr, uid, ids[0])
        classroom_origen = form.classroom_origen
        classroom_update = form.classroom_update
        classroom_obj = self.pool.get('academy.classroom')
        classroom_ids = classroom_obj.search(cr, uid, [('capacity','=',classroom_origen)])
        values = { 'capacity': classroom_update, }
        classroom_obj.write(cr, uid, classroom_ids, values)
        values = { 'state':'done', 'classroom_info_updates':len(classroom_ids), }
        self.write(cr, uid, ids, values)
        return True
    
academy_wizard()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
=======
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
############################################################################################

from osv import fields,osv
from tools.translate import _

class academy_wizard(osv.osv_memory):
    _name = 'academy.wizard'

    _columns = {
        'classroom_info_updates': fields.integer('Info Updates', readonly=True),
        'classroom_origen': fields.integer('Origen', required=True),
        'classroom_update': fields.integer('Update', required=True),
        'state':fields.selection([
            ('first','First'),
            ('done','Done'),
        ],'State'),
    }

    _defaults = {
        'state': lambda *a: 'first',
    }

    def update_classrooms(self, cr, uid, ids, data, context={}):
        form = self.browse(cr, uid, ids[0])
        classroom_origen = form.classroom_origen
        classroom_update = form.classroom_update

        classroom_obj = self.pool.get('academy.classroom')
        classroom_ids = classroom_obj.search(cr, uid, [('capacity','=',classroom_origen)])

        values = {
            'capacity':classroom_update,
        }
        classroom_obj.write(cr, uid, classroom_ids, values)

        values = {
            'state':'done',
            'classroom_info_updates':len(classroom_ids),
        }
        self.write(cr, uid, ids, values)

        return True

academy_wizard()
>>>>>>> 45445c0e2e4c781eeb3d7bb37ed12be62767a666
