
from osv import osv, fields

class academy_course_category(osv.osv):
    """Courses Categories"""
    _name = 'academy.course.category'
    _columns = {
        'name': fields.char('Category',size=16, help='Name of the category'),
        'parent_id': fields.many2one('academy.course.category','Parent Category', help='Name of the parent category'),
    }
academy_course_category()

class academy_classroom(osv.osv):
    """Academy Classrooms"""
    _name = 'academy.classroom'
    _columns = {
        'name': fields.char('Classroom',size=35, help='Name of the classroom'),
        #'address_id': fields.many2one('res.partner.address','Address', help='Address of the classroom'),
        'capacity': fields.integer('Capacity', help='Capacity of the classroom'),
        'state': fields.selection([('usable','Usable'),('in works','In Works')],'State', help='State of the classroom'),
        'active': fields.boolean('Active'),
    }
academy_classroom()

class academy_course(osv.osv):
    """Courses taught by academy"""
    _name = 'academy.course'
    _columns = {
        'name': fields.char('Course',size=32, help='Name of the course'),
        'category_id': fields.many2one('academy.course.category','Category', help='Category of the course'),
        'classroom_id': fields.many2one('academy.classroom','Classroom', help='Class in which the course is taught'),
        'dificulty': fields.selection([('low','Low'),('medium','Medium'),('high','High')],'Dificulty', help='Dificulty of the course'),
        'hours': fields.float('Studies Hours', help='Hours of the course'),
        'max_student':fields.integer('Max Estudiantes'),
        #'state': fields.selection([('draft','Draft'),('testing','Testing'),('stable','Stable')],'State'),
        'state': fields.selection([
    ('new','New'),
    ('assigned','Assigned'),
    ('negotiation','Negotiation'),
    ('won','Won'),
    ('lost','Lost')], 'Stage', readonly=True),
        'description': fields.text('Description', help='Description of the course'),
    }

    def academy_new(self, cr, uid, ids):
        self.write(cr, uid, ids, {'state': 'new'})
        return True
    def academy_assigned(self, cr, uid, ids):
        self.write(cr, uid, ids, {'state': 'assigned'})
        return True
    def academy_negotiation(self, cr, uid, ids):
        self.write(cr, uid, ids, {'state': 'negotiation'})
        return True
    def academy_won(self, cr, uid, ids):
        self.write(cr, uid, ids, {'state': 'won'})
        return True
    def academy_lost(self, cr, uid, ids):
        self.write(cr, uid, ids, {'state': 'lost'})
        return True
    def valida_cantidad_classroom(self,cr,uid,ids,classroom,context={}):
        #import pdb
        #pdb.set_trace()
        
        obj_calssroom=self.pool.get("academy.classroom")
        obj_table_class=obj_calssroom.browse(cr, uid, classroom, context=context)
        result={}
        result['max_student'] = obj_table_class.capacity
        return {'value' : result}
        
academy_course()

