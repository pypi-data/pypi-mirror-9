# -*- coding: utf-8 -*-
"""
    production.py

    :copyright: (c) 2015 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from trytond.pool import PoolMeta
from trytond.model import fields
from trytond.pyson import Eval, If, Bool
from trytond.modules.production import production

__metaclass__ = PoolMeta
__all__ = ['Production']
BOM_CHANGES = production.BOM_CHANGES + ['from_location', 'to_location']


class Production:
    __name__ = "production"

    from_location = fields.Many2One(
        'stock.location', 'From Location', domain=[
            ('type', 'not in', ('warehouse', 'view')),
            ('parent', 'child_of', If(
                Bool(Eval('warehouse')), [Eval('warehouse')], []
            ))
        ], states={
            'readonly': ~Eval('state').in_(['request', 'draft']),
        }, depends=['state', 'warehouse'],
        help="From location for production input lines"
    )
    to_location = fields.Many2One(
        'stock.location', 'To Location', domain=[
            ('type', 'not in', ('warehouse', 'view')),
            ('parent', 'child_of', If(
                Bool(Eval('warehouse')), [Eval('warehouse')], []
            ))
        ], states={
            'readonly': ~Eval('state').in_(['request', 'draft']),
        }, depends=['state', 'warehouse'],
        help="To location for production output lines"
    )

    def explode_bom(self):
        """By default on_change of bom fills storage_location of warehouse
        into from and to location of inputs and outputs respectively.
        Following implementation allows us to pick these values from
        from_location and to_location fields.
        """
        res = super(Production, self).explode_bom()

        if not res:
            return res

        if self.from_location:
            for _, added_input in res['inputs']['add']:
                added_input['from_location'] = self.from_location.id
                added_input['from_location.rec_name'] = \
                    self.from_location.rec_name

        if self.to_location:
            for _, added_output in res['outputs']['add']:
                added_output['to_location'] = self.to_location.id
                added_output['to_location.rec_name'] = self.to_location.rec_name

        return res

    @fields.depends('from_location', 'to_location')
    def on_change_product(self):
        return super(Production, self).on_change_product()

    @fields.depends('from_location', 'to_location')
    def on_change_bom(self):
        return super(Production, self).on_change_bom()

    @fields.depends('from_location', 'to_location')
    def on_change_uom(self):  # pragma: no cover
        return super(Production, self).on_change_uom()

    @fields.depends('from_location', 'to_location')
    def on_change_quantity(self):
        return super(Production, self).on_change_quantity()

    @fields.depends(*BOM_CHANGES)
    def on_change_from_location(self):
        return self.explode_bom()

    @fields.depends(*BOM_CHANGES)
    def on_change_to_location(self):
        return self.explode_bom()
