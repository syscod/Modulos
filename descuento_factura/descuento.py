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
    
    def apply_discount(self, cr, uid, ids, args, context = {}):
        res = {}
        form = self.browse(cr, uid, ids[0], context=context)
        for invoice in self.browse(cr, uid, ids, context=context):
            res[invoice.id] = {}
            for line in invoice.invoice_line:
                line.write({'discount': form.invoice_discount})
        return {}
    
    _columns = {
        'invoice_discount':fields.float('Descuento (%)',digits=(4,2), readonly=True, states={'draft': [('readonly', False)]}),
    }
    
    _defaults={
               'invoice_discount': 0.0,               
    }
    
invoice()
