# -*- coding: utf-8 -*-
"""
    product.py

    :copyright: (c) 2015 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from trytond.pool import PoolMeta
from trytond.model import fields
from trytond.pyson import Eval

__all__ = ['Product']
__metaclass__ = PoolMeta


class Product:
    __name__ = 'product.product'

    name = fields.Function(
        fields.Char('Name'),
        getter='on_change_with_name', searcher='search_rec_name'
    )

    variant_name = fields.Char(
        'Variant Name', translate=True,
        select=True, states={
            'readonly': ~Eval('active', True),
        }, depends=['active']
    )

    @fields.depends('variant_name', 'template')
    def on_change_with_name(self, name=None):  # pragma: no cover
        """
        This method changes the name to `variant_name` if it is set, or else it
        returns the template name.
        """
        return self.variant_name or self.template.name

    @classmethod
    def search_rec_name(cls, name, clause):
        """
        Downstream implementation of `search_rec_name` which adds the
        variant_name field to the domain.
        """
        domain = super(Product, cls).search_rec_name(name, clause)

        domain.append((('variant_name', ) + tuple(clause[1:])))
        return domain
