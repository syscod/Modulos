
import time
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp.tools import float_compare

class venta_credito(osv.osv):    
    _name = 'venta.credito'
              
    def get_saldo(self, cr, uid, ids, context=None):
        saldo = valor = val = va = ent = entrada= 0.0
        values={}
        #import pdb
        #pdb.set_trace()
        if context.get("entrada"):             
            ent=context.get("entrada")
        if context.get("valor"):
            va=context.get("valor")
          
        if context is None:
            return True
        for form in self.browse(cr, uid, ids, context=context):
            entrada=form.entrada
            valor=form.valor              
            if form.cobros_ids:
                for line in form.cobros_ids:
                    val += line.abono
        if va != valor and va!=0.0:
            valor=va
        if ent != entrada and ent!=0.0:
            entrada=ent    
        saldo = valor -val- entrada
        if saldo < 0:
            saldo=-999999999;
        values = {'saldo':saldo}
        return {'value':values}
    
    def get_saldo1(self, cr, uid, ids, valor, entrada, context):
        saldo = val = 0.0
        for form in self.browse(cr, uid, ids, context=context):
            if form.cobros_ids:
                for line in form.cobros_ids:
                    val += line.abono
            saldo = valor - val - entrada
            values = {'saldo':saldo}
        return {'value':values}
   
    def on_change_cliente(self, cr, uid, ids,cliente_id,context=None):
        #import pdb
        #pdb.set_trace()
        values = {
                  'es_venta':False,
                  'direccion':None,
                  'telefono':None
                  }
        if context is None:
            context = {}
        if context.get("es_venta"):
            values['es_venta'] = True
        cliente = self.pool.get('res.partner').browse(cr,uid,cliente_id,context)
        values['direccion'] = cliente.street 
        values['telefono'] = cliente.phone
        return {'value':values}
    
    def on_change_garante(self, cr, uid, ids,cliente_id,context=None):
        cliente = self.pool.get('res.partner').browse(cr,uid,cliente_id,context)
        values = {'direccion2':cliente.street, 'telefono2':cliente.phone}
        return {'value':values} 
    
    def _check_paid(self, cr, uid, ids, prop, unknow_none, context):
        form = self.browse(cr, uid, ids[0])
        return True
    
    def _get_saldo(self, cr, uid, ids, prop, unknow_none, context):
        res = {}
        val = saldo = 0.0
        for form in self.browse(cr, uid, ids, context=context):
            if form.cobros_ids:
                for line in form.cobros_ids:
                    val += line.abono
            saldo = form.valor - val - form.entrada
            res[form.id] = saldo
        return res
    
    def _get_name(self, cr, uid, ids, prop, unknow_none, context):
        res = {}
        val = ""
        for form in self.browse(cr, uid, ids, context=context):
            if form.numero and form.cliente_id.name:
                val= form.numero + " " + form.cliente_id.name + " " + form.fecha_venta
            elif form.numero and not form.cliente_id.name:
                val = form.numero + " " + form.fecha_venta
            elif not form.numero and form.cliente_id.name:
                val = form.cliente_id.name + " " + form.fecha_venta
            res[form.id] = val
        return res
    
    _columns = {
                'name':fields.char('Nombre', size=512, help="Nombre de la venta realizada."),
                'numero':fields.char('Numero', size=512, help="Identificador de la venta realizada."),
                'cliente_id':fields.many2one('res.partner', 'Cliente', required = True, help="Cliente al que se le da el credito"),  
                'direccion':fields.char('Direccion', size=512, help="Direccion del cliente."),
                'telefono':fields.char('Telefono', size=512, help="Telefono del Cliente."),
                'garante_id':fields.many2one('res.partner', 'Garante', help="Garante del credito de la venta."),
                'direccion2':fields.char('Direccion', size=512, help="Direccion del garante."),
                'telefono2':fields.char('Telefono', size=512, help="Telefono del garante."),
                'entrada':fields.float('Entrada', help="Valor que se dio de entrada."),
                'fecha_venta':fields.date('Date', readonly=True, select=True, help="Dia en que se realiza la venta"),
                'producto_id':fields.many2one('product.product', 'Articulo', help="Articulo que se incluye en la venta."),
                'valor':fields.float('Valor', help="Valor del Articulo vendido."),
                'saldo':fields.function(_get_saldo, string='Saldo', type='float', help="Valor pendiente a pagar"),
                #'saldo':fields.float('Saldo', help="Valor que queda de saldo."),
                'cobros_ids':fields.one2many('venta.cobro','venta_credito_id','Lineas de Cobros'),
                'es_venta':fields.boolean('Es venta'),
                }
    
    _defaults = {
        'fecha_venta': lambda *a: time.strftime('%Y-%m-%d'),
    }
venta_credito()


class venta_cobro(osv.osv):
    _name = 'venta.cobro'
    _columns = {
                'venta_credito_id':fields.many2one('venta.credito', 'Venta', required=1, ondelete='cascade'),
                'abono': fields.float('Abono', help="Valor que se abona a la deuda."),
                'interes': fields.float('Interes', help="Registro de interes."),
                'total': fields.float('Total', help="Total."),
                'saldo': fields.float('Saldo', help="Saldo pendiente."),
                'fecha_cobro':fields.date('Date', readonly=True, select=True, help="Dia en que se realiza el pago"),
                }
    
    _defaults = {
        'fecha_cobro': lambda *a: time.strftime('%Y-%m-%d'),
    }
venta_cobro()


class cobro_wizard(osv.osv_memory):
    _name = 'cobro.wizard'
    _columns = {
                'venta_credito_id':fields.many2one('venta.credito', 'Venta', required=1, ondelete='cascade'),
                'abono': fields.float('Abono', help="Valor que se dio de entrada."),
                'interes': fields.float('Interes', help="Valor que se dio de entrada."),
                'fecha_cobro':fields.date('Date', readonly=True, select=True, help="Dia en que se realiza la venta"),
                }
    
    _defaults = {
        'fecha_cobro': lambda *a: time.strftime('%Y-%m-%d'),
    }
    
    def do_cobro(self, cr, uid, ids, context=None):
        cobro_pool =  self.pool.get('venta.cobro')
        if context is None: context = {}
        for form in self.browse(cr, uid, ids, context=context):
            cobro_pool.create(cr, uid, {
                                    'venta_credito_id': form.venta_credito_id.id,
                                    'abono': form.abono,
                                    'interes': form.interes,
                                    'fecha_cobro': form.fecha_cobro,
                        })
        return True
    
cobro_wizard()


class venta_credito_wizard(osv.osv_memory):
    
    _name = 'venta.credito.wizard'
    
    def _get_saldo(self, cr, uid, ids, prop, unknow_none, context):
        res = {}
        saldo = 0.0
        for form in self.browse(cr,uid,ids):
            res[form.id] = form.valor - form.entrada
        return res
    
    def _get_name(self, cr, uid, ids, prop, unknow_none, context):
        res = {}
        val = ""
        for form in self.browse(cr, uid, ids, context=context):
            if form.numero and form.cliente_id.name:
                val= form.numero + " " + form.cliente_id.name + " " + form.fecha_venta
            elif form.numero and not form.cliente_id.name:
                val = form.numero + " " + form.fecha_venta
            elif not form.numero and form.cliente_id.name:
                val = form.cliente_id.name + " " + form.fecha_venta
            res[form.id] = val
        return res
    
    _columns = {
                'name':fields.function(_get_name, string='Nombre', type='char', help="Nombre del credito"),
                'numero':fields.char('Numero', size=512, help="Identificador de la venta realizada."),
                'cliente_id':fields.many2one('res.partner', 'Cliente', required = True, help="Cliente al que se le da el credito"),
                'garante_id':fields.many2one('res.partner', 'Garante', help="Garante del credito de la venta."),
                'entrada':fields.float('Entrada', help="Valor que se dio de entrada."),
                'fecha_venta':fields.date('Date', readonly=True, select=True, help="Dia en que se realiza la venta"),
                'producto_id':fields.many2one('product.product', 'Articulo', help="Articulo que se incluye en la venta."),
                'valor':fields.float('Valor', help="Valor del Articulo vendido."),
                'saldo':fields.function(_get_saldo, string='Saldo', type='float'),
                }
    
    _defaults = {
        'fecha_venta': lambda *a: time.strftime('%Y-%m-%d'),
    }  
    
    def do_venta(self, cr, uid, ids, context=None):
        venta_pool =  self.pool.get('venta.credito')
        for form in self.browse(cr, uid, ids, context=context):
            venta_pool.create(cr, uid, {
                                        'name':form.name,
                                        'cliente_id':form.cliente_id.id,
                                        'garante_id':form.garante_id.id,
                                        'entrada':form.entrada,
                                        'fecha_venta':form.fecha_venta,
                                        'producto_id':form.producto_id.id,
                                        'valor':form.valor,
                                        'saldo':form.saldo,
                                        'numero':form.numero,
                                        'es_venta':1, #especifica que se trata de una venta
                                        })
        return True
    
venta_credito_wizard()

class pago_wizard(osv.osv_memory):
    
    _name = 'pago.wizard'
    _columns = {
                'venta_credito_id':fields.many2one('venta.credito', 'Venta', required=1, ondelete='cascade'),
                'abono': fields.float('Abono', help="Valor que se dio de entrada."),
                'interes': fields.float('Interes', help="Valor que se dio de entrada."),
                'fecha_cobro':fields.date('Date', readonly=True, select=True, help="Dia en que se realiza la venta"),
                }
    
    _defaults = {
        'fecha_cobro': lambda *a: time.strftime('%Y-%m-%d'),
    }
    
    def do_pago(self, cr, uid, ids, context=None):
        cobro_pool =  self.pool.get('venta.cobro')
        if context is None: context = {}
        for form in self.browse(cr, uid, ids, context=context):
            cobro_pool.create(cr, uid, {
                                    'venta_credito_id': form.venta_credito_id.id,
                                    'abono': form.abono,
                                    'interes': form.interes,
                                    'fecha_cobro': form.fecha_cobro,
                        })
        return True
    
cobro_wizard()


class compra_credito_wizard(osv.osv_memory):
    
    _name = 'compra.credito.wizard'
    
    def _get_saldo(self, cr, uid, ids, prop, unknow_none, context):
        res = {}
        saldo = 0.0
        for form in self.browse(cr,uid,ids):
            res[form.id] = form.valor - form.entrada
        return res
    
    def _get_name(self, cr, uid, ids, prop, unknow_none, context):
        res = {}
        val = ""
        for form in self.browse(cr, uid, ids, context=context):
            if form.numero and form.cliente_id.name:
                val= form.numero + " " + form.cliente_id.name + " " + form.fecha_venta
            elif form.numero and not form.cliente_id.name:
                val = form.numero + " " + form.fecha_venta
            elif not form.numero and form.cliente_id.name:
                val = form.cliente_id.name + " " + form.fecha_venta
            res[form.id] = val
        return res
    
    _columns = {
                #'name':fields.char('Nombre', size=512, help="Nombre de la venta realizada."),
                'name':fields.function(_get_name, string='Nombre', type='char', help="Nombre del credito"),
                'numero':fields.char('Numero', size=512, help="Identificador de la venta realizada."),
                'cliente_id':fields.many2one('res.partner', 'Cliente', required = True, help="Cliente al que se le da el credito"),
                'garante_id':fields.many2one('res.partner', 'Garante', help="Garante del credito de la venta."),
                'entrada':fields.float('Entrada', help="Valor que se dio de entrada."),
                'fecha_venta':fields.date('Date', readonly=True, select=True, help="Dia en que se realiza la venta"),
                'producto_id':fields.many2one('product.product', 'Articulo', help="Articulo que se incluye en la venta."),
                'valor':fields.float('Valor', help="Valor del Articulo vendido."),
                'saldo':fields.function(_get_saldo, string='Saldo', type='float'),
                }
    
    _defaults = {
        'fecha_venta': lambda *a: time.strftime('%Y-%m-%d'),
    }  
    
    def do_compra(self, cr, uid, ids, context=None):
        venta_pool =  self.pool.get('venta.credito')
        for form in self.browse(cr, uid, ids, context=context):
            venta_pool.create(cr, uid, {
                                        'numero':form.numero,
                                        'name':form.name,
                                        'cliente_id':form.cliente_id.id,
                                        'garante_id':form.garante_id.id,
                                        'entrada':form.entrada,
                                        'fecha_venta':form.fecha_venta,
                                        'producto_id':form.producto_id.id,
                                        'valor':form.valor,
                                        'saldo':form.saldo,
                                        })
        import pdb
        pdb.set_trace()
        return True
    
compra_credito_wizard()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: