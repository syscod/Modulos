# -*- encoding: utf-8 -*-
##############################################################################
#
#    
##############################################################################

from osv import osv,fields
from tools import config

class invoice(osv.osv):
    '''
    Inherits account.invoice to add global discount feature.
    
    '''
    _inherit = 'account.invoice'
    
    def _get_total(self, cr, uid, ids, prop, unknow_none, context):
        record_id=ids[0]
        res={record_id: 0.0}
        for invoice in self.browse(cr, uid, ids, context=context):
            val = 0.0
            for line in invoice.invoice_line:
                val += line.price_unit * line.quantity
        res[record_id] = val
        return res
    
    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context):
        res = self.name_get(cr, uid, ids, context)
        return dict(res)

    def _get_total_discount(self, cr, uid, ids, prop, unknow_none, context):
        record_id=ids[0]
        res={record_id: 0.0}
        for invoice in self.browse(cr, uid, ids, context=context):
            val = 0.0
            for line in invoice.invoice_line:
                val += line.price_unit * line.quantity
            val = val - invoice.amount_untaxed
        res[record_id] = val
        return res

    _columns = {
        #'invoice_discount':fields.float('Descuento (%)',digits=(4,2), readonly=True, states={'draft': [('readonly', False)]}),
        'invoice_total': fields.function(_get_total, method=True, type="float", string='Total Bruto', readonly='True'),
        'invoice_discount': fields.function(_get_total_discount, method=True, type="float", string='Total Descuento', readonly='True'),
    }
    
invoice()
