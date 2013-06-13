from openerp.osv import fields, osv

class academy_report(osv.osv_memory):
    
    _name = 'academy.report'
    
    listaobjetos = []
    listaobjetosd = []
    
    def _get_cur_function_id(self, cr, uid, ids, nombre_campo, arg, context):
        form = self.browse(cr, uid, ids[0])
        classroom_origen = form.classroom_origen
        classroom_update = form.classroom_update
        classroom_obj = self.pool.get('academy.classroom')
        classroom_ids = classroom_obj.search(cr, uid, [('capacity','=',classroom_origen)])
        
        import pdb 
        pdb.set_trace()
        return classroom_obj.read(cr, uid, classroom_ids) # res es un vector de ids
    
    _columns = {
                'classroom_info_updates': fields.integer('Info Updates', readonly=True),
                'classroom_origen': fields.integer('Origen', required=True),
                'classroom_update': fields.integer('Update', required=True),
                'state':fields.selection([ ('first','First'), ('done','Done'), ],'State'),
                #'classroom_ids': fields.many2many('academy.classroom', 'report_classroom_rel', 'classroom_id', 'academy_classroom_id', 'Classroom'),
                
                #'aclassroom_ids' : fields.one2many('academy.classroom', 'academy_classroom_id', 'Classroom'),
                #'class_ids' : fields.function(_get_cur_function_id, type='list', obj='academy.classroom', method = True, string = 'academy_classroom_id'),             
                #'aclassroom_ids' : fields.function(_get_cur_function_id, type='one2many', obj='academy.classroom', method = True, string = 'academy_classroom_id'),
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
        values = { 'state':'done', 'classroom_info_updates':len(classroom_ids), 'classroom_origen': classroom_origen, 'classroom_update': classroom_update}
        self.write(cr, uid, ids, values)
        return True

    def print_classrooms(self, cr, uid, ids, data, context=None):
        form = self.browse(cr, uid, ids[0])
        #data1 = self.read(cr, uid, ids)[0]          ## borrar esto
        #objeto = self.pool.get('academy.classroom') ## borrar esto 
        #objeto_browse = objeto.browse(cr, uid, 1) ## borrar esto
        #objeto_read = objeto.read(cr, uid, 1) ## borrar esto
        
        classroom_origen = form.classroom_origen
        classroom_update = form.classroom_update
        classroom_obj = self.pool.get('academy.classroom')
        classroom_ids = classroom_obj.search(cr, uid, [('capacity','=',classroom_origen)])
        course_obj = self.pool.get('academy.course')
        course_ids = course_obj.search(cr,uid, [('name','=','Matematicas')])
        course_browse = course_obj.browse(cr, uid, 1)
        course_read = course_obj.read(cr, uid, 1)
		#hasta aqui busca segun la capacidad de origen
        valores = [1,2]
        values = { 'capacity': classroom_update, }
        #classroom_obj.write(cr, uid, classroom_ids, values)
        self.listaobjetos = classroom_obj.browse(cr, uid, classroom_ids) #devuelve lista objetos
        self.listaobjetosd = classroom_obj.read(cr, uid, classroom_ids) #devuelve lista diccionarios
        #self.listaobjetos.append(2)
        #self.listaobjetos.append(5)
		#escribe la capacidad nueva
        values = { 'state':'done', 'classroom_info_updates':len(classroom_ids), 'classroom_ids':classroom_ids  } # ,  'aclassroom_ids':objeto_read
        import pdb
        pdb.set_trace()
        self.write(cr, uid, ids, values)#####oiu09806
        
        ##datas = {'ids':classroom_ids, 'model': 'academy.classroom', 'form': listaobjetosd}
        datas = {'ids':ids, 'model': 'academy.report', 'form': data}
        pdb.set_trace()
        #return {
        #    'type': 'ir.actions.report.xml',
        #    'nodestroy': True,
        #    'report_name': 'academy.report.classroom',
        #    'datas': datas,
        #}
        
        return {
            'type': 'ir.actions.report.xml',
            'nodestroy': True,
            'report_name': 'academy.report',
            'datas': datas,
        }

    def check_report(self, cr, uid, ids, context=None):
        datas = {}
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        datas = {
             'ids': context.get('active_ids',[]),
             'model': 'account.analytic.account',
             'form': data
                 }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'account.analytic.account.balance',
            'datas': datas,
            }

    
academy_report()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: