# -*- coding: utf-8 -*-
# Copyright 2016 Serpent Consulting Services Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import datetime, timedelta, date
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.exceptions import UserError


class PartnerCreditLimit(models.TransientModel):
    _name = 'partner.credit.limit'

    so_id = fields.Many2one('sale.order')

    @api.model
    def default_get(self, fields):
        res = super(PartnerCreditLimit, self).default_get(fields)
        if not res.get('so_id') and self._context.get('active_id'):
            res['so_id'] = self._context['active_id']
        return res

    @api.multi
    def action_confirm_anyway(self):
        #print 'action_confirm_anyway'
        self.ensure_one()
        if self.so_id:
            self.so_id.action_confirm_anyway()


class SaleOrder(models.Model):
    _inherit = "sale.order"


    @api.multi
    def check_limit(self):
        """Check if credit limit for partner was exceeded."""
        self.ensure_one()
        today_dt = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
        partner = self.partner_id
        #print 'partner.name: ',partner.name

        #SEARCH SALE ORDERS
        so_amount = 0.0
        so_obj = self.env['sale.order']
        so_ids = so_obj.search([('partner_id','=',partner.id),('state','=','sale')])
        #print so_ids

        for so in so_ids:
            print 'so.name: ',so.name
            payment_term = so.payment_term_id or so.partner_id.property_payment_term_id
            days = 0
            print len(payment_term)
            if len(payment_term) > 0:
                days = payment_term.line_ids and payment_term.line_ids[0] and payment_term.line_ids[0].days
            #print 'so.payment_term_id: ',so.payment_term_id
            #print 'so.partner_id.property_payment_term_id: ',so.partner_id.property_payment_term_id
            #print 'payment_term: ',payment_term
            #print 'days: ',days
            #print type(days)
            confirmation_date = datetime.strptime(so.confirmation_date, "%Y-%m-%d %H:%M:%S")+timedelta(days=days)
            confirmation_date = datetime.strftime(confirmation_date,"%Y-%m-%d %H:%M:%S")
            #print 'confirmation_date: ',confirmation_date
            #print 'today_dt: ',today_dt
            if not so.invoice_ids and confirmation_date <= today_dt:
                #print 'so.NAME: ',so.name
                #print 'so.amount_total: ',so.amount_total
                #print '---------------'
                so_amount += so.amount_total
            elif so.invoice_ids:
                for inv in so.invoice_ids:
                    if inv.state not in ('open','paid','cancel'):
                        #print 'invoice: ',inv.name
                        #print 'date_invoice: ',date_invoice
                        payment_term = inv.payment_term_id or inv.partner_id.property_payment_term_id
                        days = 0
                        if len(payment_term) > 0:
                            days = payment_term.line_ids and payment_term.line_ids[0] and payment_term.line_ids[0].days
                        date_invoice = datetime.strptime(inv.date_invoice, "%Y-%m-%d %H:%M:%S")+timedelta(days=days)
                        date_invoice = datetime.strftime(date_invoice,"%Y-%m-%d %H:%M:%S")
                        if date_invoice < today_dt:
                            so_amount += inv.amount_total
                #so_amount += sum([inv.amount_total for inv in so.invoice_ids \
                #    if inv.state not in ('open','paid','cancel') and inv.date_invoice < today_dt])

        #print 'so_amount: ',so_amount

        moveline_obj = self.env['account.move.line']
        movelines = moveline_obj.\
            search([('partner_id', '=', partner.id),
                    ('account_id.user_type_id.type', 'in',
                    ['receivable', 'payable']),
                    ('full_reconcile_id', '=', False)])

        debit, credit = 0.0, 0.0 
        for line in movelines:
            #print 'line.name: ',line.name
            if line.date_maturity <= today_dt:
                credit += line.debit
                debit += line.credit

        #print 'so_amount: ',so_amount
        #print 'partner.credit_limit: ',partner.credit_limit
        #print 'credit - debit + self.amount_total + so_amount: ',credit - debit + self.amount_total + so_amount
        #if (credit - debit + self.amount_total) > partner.credit_limit:
        if (credit - debit + self.amount_total + so_amount) > partner.credit_limit:
            # Consider partners who are under a company.
            if partner.over_credit or (partner.parent_id and partner.parent_id.over_credit):
                # partner.write({
                #     'credit_limit': credit - debit + self.amount_total})
                return True
            else:
                #msg = "Favor de validar con el área de finanzas,"+\
                #"\n este cliente se encuentra en situación de crédito con saldo pendiente"

                #raise UserError(_('Credit Over Limits !\n' + msg))

                return False
        else:
            return True

    @api.multi
    def action_confirm(self):
        #print 'action_confirm'
        """Extend to check credit limit before confirming sale order."""
        for order in self:
            if not order.check_limit():
                view = self.env.ref('customer_credit_limit.customer_credit_limit_view')
                wiz = self.env['partner.credit.limit'].create({'so_id': self.id})
                return {
                    'name': _('Credit limit'),
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'partner.credit.limit',
                    'views': [(view.id, 'form')],
                    'view_id': view.id,
                    'target': 'new',
                    'res_id': wiz.id,
                    #'context': self.env.context,
                }
        return super(SaleOrder, self).action_confirm()


    @api.multi
    def action_confirm_anyway(self):
        #print 'action_confirm_anyway'
        """Extend to check credit limit before confirming sale order."""
        return super(SaleOrder, self).action_confirm()