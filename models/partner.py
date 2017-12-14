# -*- coding: utf-8 -*-
# Copyright 2016 Serpent Consulting Services Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import fields,api, models, _
from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def create(self,fields):
        term_obj = self.env['account.payment.term']
        if 'property_payment_term_id' in fields:
            term = term_obj.search([('id','=', fields['property_payment_term_id'] )])
        else:
            term = False

        if 'credit_limit' in fields:
            credit_limit =  fields['credit_limit']
        else:
            credit_limit = 0

        #print 'credit_limit: ',credit_limit
        #print term.line_ids[0] and term.line_ids[0].days
        if term and term.line_ids[0] and term.line_ids[0].days > 0 and credit_limit <= 0:
            raise UserError(_('Tiene que establecer un limite de credito de cliente mayor a 0 para poder'\
                +'\n asignar un termino de pago distinto a Pago inmediato'))

        return super(ResPartner,self).create(fields)

    # def write(self,fields):
    #     #print 'ResPartner write'
    #     term_obj = self.env['account.payment.term']
    #     if 'property_payment_term_id' in fields:
    #         term = term_obj.search([('id','=', fields['property_payment_term_id'] )])
    #     else:
    #         term = self.property_payment_term_id

    #     if 'credit_limit' in fields:
    #         credit_limit =  fields['credit_limit']
    #     else:
    #         credit_limit = self.credit_limit

    #     #print 'credit_limit: ',credit_limit
    #     #print term.line_ids[0] and term.line_ids[0].days
    #     if term and term.line_ids and term.line_ids[0] and term.line_ids[0].days > 0 and credit_limit <= 0:
    #         raise UserError(_('Tiene que establecer un limite de credito de cliente mayor a 0 para poder'\
    #             +'\n asignar un termino de pago distinto a Pago inmediato'))

    #     return super(ResPartner,self).write(fields)

    @api.multi
    def write(self,fields):
        print 'ResPartner write'
        term_obj = self.env['account.payment.term']

        for rec in self:
            if 'property_payment_term_id' in fields:
                term = term_obj.search([('id','=', fields['property_payment_term_id'] )])
            else:
                term = rec.property_payment_term_id

            if 'credit_limit' in fields:
                credit_limit =  fields['credit_limit']
            else:
                credit_limit = rec.credit_limit

            # print 'rec.name: ',rec.name
            # print 'credit_limit: ',credit_limit
            # print term.line_ids[0] and term.line_ids[0].days
            # print 'rec.parent_id: ',rec.parent_id.id
            # print '-------'
            # if rec.parent_id.id == False:
            #     print 'FALSO'
            if term and term.line_ids and term.line_ids[0] and term.line_ids[0].days > 0 and credit_limit <= 0 and rec.parent_id.id == False:
                raise UserError(_('Tiene que establecer un limite de credito de cliente mayor a 0 para poder'\
                    +'\n asignar un termino de pago distinto a Pago inmediato'))

        return super(ResPartner,self).write(fields)

    over_credit = fields.Boolean('Allow Over Credit?')
