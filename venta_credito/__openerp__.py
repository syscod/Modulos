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
    "name" : "Manejo de Ventas a Credito",
    "version" : "1.0",
    "description" : "Manejo de Ventas a Credito, cobros, clientes",
    "author" : "Syscon",
    'website': 'http://www.syscod.comyr.com/',
    "depends" : ['base','product',],
    "category" : "Generic Modules",
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : ["venta_credito_view.xml"],
    "installable": True,
    "license" : "GPL-3 or any later version",
}
