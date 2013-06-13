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

import time
from lxml import etree

from openerp import netsvc
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp.tools import float_compare

class hr_voucher(osv.osv):
    _name = 'hr.voucher'
    _description = 'Payroll Voucher'
    _inherit = ['mail.thread']
    _order = "date desc, id desc"
#    _rec_name = 'number'
    _track = {
        'state': {
            'hr_voucher.mt_voucher_state_change': lambda self, cr, uid, obj, ctx=None: True,
        },
    }
    
    def _get_period(self, cr, uid, context=None):
        if context is None: context = {}
        if context.get('period_id', False):
            return context.get('period_id')
        periods = self.pool.get('account.period').find(cr, uid)
        return periods and periods[0] or False
    
    def _get_currency(self, cr, uid, context=None):
        if context is None: context = {}
        journal_pool = self.pool.get('account.journal')
        journal_id = context.get('journal_id', False)
        if journal_id:
            journal = journal_pool.browse(cr, uid, journal_id, context=context)
            if journal.currency:
                return journal.currency.id
        return False

    _columns = {
        'active': fields.boolean('Active', help="By default, reconciliation vouchers made on draft bank statements are set as inactive, which allow to hide the customer/supplier payment while the bank statement isn't confirmed."),
        'type':fields.selection([
            ('sale','Sale'),
            ('purchase','Purchase'),
            ('payment','Payment'),
            ('receipt','Receipt'),
        ],'Default Type', readonly=True, states={'draft':[('readonly',False)]}),
        'name':fields.char('Memo', size=256, readonly=True, states={'draft':[('readonly',False)]}),
        'date':fields.date('Date', readonly=True, select=True, states={'draft':[('readonly',False)]}, help="Effective date for accounting entries"),
        'journal_id':fields.many2one('account.journal', 'Journal', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'account_id':fields.many2one('account.account', 'Account', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'line_ids':fields.one2many('hr.voucher.line','voucher_id','Voucher Lines', readonly=True, states={'draft':[('readonly',False)]}),
        'line_cr_ids':fields.one2many('hr.voucher.line','voucher_id','Credits',
            domain=[('type','=','cr')], context={'default_type':'cr'}, readonly=True, states={'draft':[('readonly',False)]}),
        'line_dr_ids':fields.one2many('hr.voucher.line','voucher_id','Debits',
            domain=[('type','=','dr')], context={'default_type':'dr'}, readonly=True, states={'draft':[('readonly',False)]}),
        'period_id': fields.many2one('account.period', 'Period', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'narration':fields.text('Notes', readonly=True, states={'draft':[('readonly',False)]}),
        'currency_id':fields.many2one('res.currency', 'Currency', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'currency_id': fields.related('journal_id','currency', type='many2one', relation='res.currency', string='Currency', readonly=True),
        'company_id': fields.many2one('res.company', 'Company', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'state':fields.selection(
            [('draft','Draft'),
             ('cancel','Cancelled'),
             ('proforma','Pro-forma'),
             ('posted','Posted')
            ], 'Status', readonly=True, size=32, track_visibility='onchange',
            help=' * The \'Draft\' status is used when a user is encoding a new and unconfirmed Voucher. \
                        \n* The \'Pro-forma\' when voucher is in Pro-forma status,voucher does not have an voucher number. \
                        \n* The \'Posted\' status is used when user create voucher,a voucher number is generated and voucher entries are created in account \
                        \n* The \'Cancelled\' status is used when user cancel voucher.'),
        'amount': fields.float('Total', digits_compute=dp.get_precision('Account'), required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'tax_amount':fields.float('Tax Amount', digits_compute=dp.get_precision('Account'), readonly=True, states={'draft':[('readonly',False)]}),
        'reference': fields.char('Ref #', size=64, readonly=True, states={'draft':[('readonly',False)]}, help="Transaction reference number."),
        'number': fields.char('Number', size=32, readonly=True,),
        'move_id':fields.many2one('account.move', 'Account Entry'),
        'move_ids': fields.related('move_id','line_id', type='one2many', relation='account.move.line', string='Journal Items', readonly=True),
        'partner_id':fields.many2one('res.partner', 'Partner', change_default=1, readonly=True, states={'draft':[('readonly',False)]}),
        'audit': fields.related('move_id','to_check', type='boolean', help='Check this box if you are unsure of that journal entry and if you want to note it as \'to be reviewed\' by an accounting expert.', relation='account.move', string='To Review'),
     #   'paid': fields.function(_check_paid, string='Paid', type='boolean', help="The Voucher has been totally paid."),
        'pay_now':fields.selection([
            ('pay_now','Pay Directly'),
            ('pay_later','Pay Later or Group Funds'),
        ],'Payment', select=True, readonly=True, states={'draft':[('readonly',False)]}),
        'tax_id': fields.many2one('account.tax', 'Tax', readonly=True, states={'draft':[('readonly',False)]}, domain=[('price_include','=', False)], help="Only for tax excluded from price"),
        'pre_line':fields.boolean('Previous Payments ?', required=False),
        'date_due': fields.date('Due Date', readonly=True, select=True, states={'draft':[('readonly',False)]}),
        'payment_option':fields.selection([
                                           ('without_writeoff', 'Keep Open'),
                                           ('with_writeoff', 'Reconcile Payment Balance'),
                                           ], 'Payment Difference', required=True, readonly=True, states={'draft': [('readonly', False)]}, help="This field helps you to choose what you want to do with the eventual difference between the paid amount and the sum of allocated amounts. You can either choose to keep open this difference on the partner's account, or reconcile it with the payment(s)"),
        'writeoff_acc_id': fields.many2one('account.account', 'Counterpart Account', readonly=True, states={'draft': [('readonly', False)]}),
        'comment': fields.char('Counterpart Comment', size=64, required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'analytic_id': fields.many2one('account.analytic.account','Write-Off Analytic Account', readonly=True, states={'draft': [('readonly', False)]}),
       # 'writeoff_amount': fields.function(_get_writeoff_amount, string='Difference Amount', type='float', readonly=True, help="Computed as the difference between the amount stated in the voucher and the sum of allocation on the voucher lines."),
        'payment_rate_currency_id': fields.many2one('res.currency', 'Payment Rate Currency', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'payment_rate': fields.float('Exchange Rate', digits=(12,6), required=True, readonly=True, states={'draft': [('readonly', False)]},
            help='The specific rate that will be used, in this voucher, between the selected currency (in \'Payment Rate Currency\' field)  and the voucher currency.'),
      #  'paid_amount_in_company_currency': fields.function(_paid_amount_in_company_currency, string='Paid Amount in Company Currency', type='float', readonly=True),
        'is_multi_currency': fields.boolean('Multi Currency Voucher', help='Fields with internal purpose only that depicts if the voucher is a multi currency one or not'),
    }
    _defaults = {
        'active': True,
        'period_id': _get_period,
        'payment_rate_currency_id': _get_currency,
       # 'partner_id': _get_partner,
       # 'journal_id':_get_journal,
       # 'currency_id': _get_currency,
       # 'reference': _get_reference,
       # 'narration':_get_narration,
       # 'amount': _get_amount,
       # 'type':_get_type,
        'state': 'draft',
        'pay_now': 'pay_now',
        'name': lambda *a: "hola",
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'hr.voucher',context=c),
       # 'tax_id': _get_tax,
        'payment_option': 'without_writeoff',
        'comment': _('Write-Off'),
        'payment_rate': 1.0,
       #'payment_rate_currency_id': _get_payment_rate_currency,
    }
    
    
    def do_payment(self, cr, uid, ids, data, context=None):
        import pdb
        if context is None:
            context = {}
        move_pool = self.pool.get('account.move')
        move_line_pool = self.pool.get('account.move.line')
        journal_pool = self.pool.get('account.journal')
        period_pool = self.pool.get('account.period')
        timenow = time.strftime('%Y-%m-%d')
        for slip in self.browse(cr, uid, ids, context=context):
            journal_id = slip.journal_id.id
            pdb.set_trace()
            move_line_ids = []
            debit_sum = 0.0
            credit_sum = 0.0
            journal = journal_pool.browse(cr, uid, journal_id, context=context)
            if not slip.period_id:
                search_periods = period_pool.find(cr, uid, slip.date_to, context=context)
                period_id = search_periods[0]
            else:
                period_id = slip.period_id.id

            #default_partner_id = slip.employee_id.address_home_id.id
            name = _('Payslip of %s') % (slip.partner_id.name) #employee_id
            move = {
                'narration': name,
                'date': timenow,
                'ref': slip.number,
                'journal_id': slip.journal_id.id,
                'period_id': period_id,
            }
            for line in slip.line_ids:
                amt = slip.amount and -line.amount or line.amount
                # partner_id = line.salary_rule_id.register_id.partner_id and line.salary_rule_id.register_id.partner_id.id or default_partner_id
                partner_id = slip.partner_id.id
                #debit_account_id = line.salary_rule_id.account_debit.id
                #credit_account_id = line.salary_rule_id.account_credit.id
                debit_account_id = slip.journal_id.default_debit_account_id.id
                credit_account_id = slip.journal_id.default_credit_account_id.id
                pdb.set_trace()
                if debit_account_id:

                    debit_line = (0, 0, {
                    'name': line.name,
                    'date': timenow,
                    'partner_id': slip.partner_id.id,
                    'account_id': debit_account_id,
                    'journal_id': slip.journal_id.id,
                    'period_id': period_id,
                    'debit': amt > 0.0 and amt or 0.0,
                    'credit': amt < 0.0 and -amt or 0.0,
                    #'analytic_account_id': line.salary_rule_id.analytic_account_id and line.salary_rule_id.analytic_account_id.id or False,
                    #'tax_code_id': line.salary_rule_id.account_tax_id and line.salary_rule_id.account_tax_id.id or False,
                    #'tax_amount': line.salary_rule_id.account_tax_id and amt or 0.0,
                })
                    move_line_ids.append(debit_line)
                    debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']
                pdb.set_trace()
                if credit_account_id:

                    credit_line = (0, 0, {
                    'name': line.name,
                    'date': timenow,
                    'partner_id': slip.partner_id.id,
                    'account_id': credit_account_id,
                    'journal_id': slip.journal_id.id,
                    'period_id': period_id,
                    'debit': amt < 0.0 and -amt or 0.0,
                    'credit': amt > 0.0 and amt or 0.0,
                    #'analytic_account_id': line.salary_rule_id.analytic_account_id and line.salary_rule_id.analytic_account_id.id or False,
                    #'tax_code_id': line.salary_rule_id.account_tax_id and line.salary_rule_id.account_tax_id.id or False,
                    #'tax_amount': line.salary_rule_id.account_tax_id and amt or 0.0,
                })
                    move_line_ids.append(credit_line)
                    credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']

            if debit_sum > credit_sum:
                acc_id = slip.journal_id.default_credit_account_id.id
                if not acc_id:
                    raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has not properly configured the Credit Account!')%(slip.journal_id.name))
                adjust_credit = (0, 0, {
                    'name': _('Adjustment Entry'),
                    'date': timenow,
                    'partner_id': False,
                    'account_id': acc_id,
                    'journal_id': slip.journal_id.id,
                    'period_id': period_id,
                    'debit': 0.0,
                    'credit': debit_sum - credit_sum,
                })
                move_line_ids.append(adjust_credit)

            elif debit_sum < credit_sum:
                acc_id = slip.journal_id.default_debit_account_id.id
                if not acc_id:
                    raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has not properly configured the Debit Account!')%(slip.journal_id.name))
                adjust_debit = (0, 0, {
                    'name': _('Adjustment Entry'),
                    'date': timenow,
                    'partner_id': False,
                    'account_id': acc_id,
                    'journal_id': slip.journal_id.id,
                    'period_id': period_id,
                    'debit': credit_sum - debit_sum,
                    'credit': 0.0,
                })
                move_line_ids.append(adjust_debit)
            move.update({'line_id': move_line_ids})
            move_id = move_pool.create(cr, uid, move, context=context)
            self.write(cr, uid, [slip.id], {'move_id': move_id, 'period_id' : period_id}, context=context)
            if slip.journal_id.entry_posted: 
                move_pool.post(cr, uid, [move_id], context=context) #omitir estado borrador
        self.write(cr, uid, ids, {'state':'posted'})
        return False
    
    def cancel_payment(self, cr, uid, ids, data, context=None):
        reconcile_pool = self.pool.get('account.move.reconcile')
        move_pool = self.pool.get('account.move')

        for voucher in self.browse(cr, uid, ids, context=context):
            recs = []
            for line in voucher.move_ids:
                if line.reconcile_id:
                    recs += [line.reconcile_id.id]
                if line.reconcile_partial_id:
                    recs += [line.reconcile_partial_id.id]

            reconcile_pool.unlink(cr, uid, recs)

            if voucher.move_id:
                move_pool.button_cancel(cr, uid, [voucher.move_id.id])
                move_pool.unlink(cr, uid, [voucher.move_id.id])
        res = {
            'state':'cancel',
            'move_id':False,
        }
        self.write(cr, uid, ids, res)
        return True
    
    
    def action_cancel_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'draft'})
        return True
    
hr_voucher()
    

class hr_voucher_line(osv.osv):
    _name = 'hr.voucher.line'
    _description = 'HR Voucher Lines'
    _order = "move_line_id"

    _columns = {
        'voucher_id':fields.many2one('hr.voucher', 'Voucher', required=1, ondelete='cascade'),
        'name':fields.char('Description', size=256),
        'account_id':fields.many2one('account.account','Account', required=True),
        'partner_id':fields.related('voucher_id', 'partner_id', type='many2one', relation='res.partner', string='Partner'),
        'untax_amount':fields.float('Untax Amount'),
        'amount':fields.float('Amount', digits_compute=dp.get_precision('Account')),
        'reconcile': fields.boolean('Full Reconcile'),
        'type':fields.selection([('dr','Debit'),('cr','Credit')], 'Dr/Cr'),
        'account_analytic_id':  fields.many2one('account.analytic.account', 'Analytic Account'),
        'move_line_id': fields.many2one('account.move.line', 'Journal Item'),
        'date_original': fields.related('move_line_id','date', type='date', relation='account.move.line', string='Date', readonly=1),
        'date_due': fields.related('move_line_id','date_maturity', type='date', relation='account.move.line', string='Due Date', readonly=1),
       # 'amount_original': fields.function(_compute_balance, multi='dc', type='float', string='Original Amount', store=True, digits_compute=dp.get_precision('Account')),
      #  'amount_unreconciled': fields.function(_compute_balance, multi='dc', type='float', string='Open Balance', store=True, digits_compute=dp.get_precision('Account')),
        'company_id': fields.related('voucher_id','company_id', relation='res.company', type='many2one', string='Company', store=True, readonly=True),
     #   'currency_id': fields.function(_currency_id, string='Currency', type='many2one', relation='res.currency', readonly=True),
    }
    _defaults = {
        'name': '',
    }
    
hr_voucher_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
