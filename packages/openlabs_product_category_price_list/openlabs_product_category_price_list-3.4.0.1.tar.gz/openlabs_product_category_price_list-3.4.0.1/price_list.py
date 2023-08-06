# -*- coding: utf-8 -*-
"""
    price_list.py

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from trytond.pool import PoolMeta, Pool
from trytond.model import fields
from trytond.pyson import Eval, Bool

__all__ = ['PriceList', 'PriceListLine']

__metaclass__ = PoolMeta


class PriceList:
    'Price List'
    __name__ = 'product.price_list'

    def compute(
        self, party, product, unit_price, quantity, uom,
        pattern=None
    ):
        '''
        Compute price based on price list of party

        :param unit_price: a Decimal for the default unit price in the
            company's currency and default uom of the product
        :param quantity: the quantity of product
        :param uom: a instance of the product.uom
        :param pattern: a dictionary with price list field as key
            and match value as value
        :return: the computed unit price
        '''
        if pattern is None:
            pattern = {}

        pattern = pattern.copy()

        pattern['category'] = product.category and product.category.id or None

        return super(PriceList, self).compute(
            party, product, unit_price, quantity, uom, pattern
        )


class PriceListLine:
    'Price List Line'
    __name__ = 'product.price_list.line'

    category = fields.Many2One(
        'product.category', 'Category',
        states={'readonly': Bool(Eval('product'))}, depends=['product']
    )

    @classmethod
    def __setup__(cls):
        super(PriceListLine, cls).__setup__()

        cls._error_messages.update({
            'not_allowed_together':
                "Product and category can not be defined together",
        })

        cls.product.states['readonly'] = Bool(Eval('category'))

    @fields.depends('category', 'product')
    def on_change_product(self):
        """
        Clear category field on change of product
        """
        if self.product:
            return {
                'category': None
            }
        return {}

    @fields.depends('category', 'product')
    def on_change_category(self):
        """
        Clear product field on change of category
        """
        if self.category:
            return {
                'product': None
            }
        return {}

    @classmethod
    def validate(cls, lines):
        """
        Validates price list lines
        """
        super(PriceListLine, cls).validate(lines)
        for line in lines:
            line.check_product_and_category()

    def check_product_and_category(self):
        """
        Checks that either of product or category must be there at a time,
        not both
        """
        if self.product and self.category:
            self.raise_user_error("not_allowed_together")

    def _match_category(self, category):
        """
        Match with the category and its parents
        """
        Category = Pool().get('product.category')
        category = Category(category)

        if not self.category:
            return False

        def is_a_match(pattern_category):
            if self.category.id == pattern_category.id:
                return True
            if pattern_category.parent:
                return is_a_match(pattern_category.parent)
            return False

        return is_a_match(category)

    def match(self, pattern):
        '''
        Match line on pattern

        This is reimplemented here because in version 3.2, the price list line
        matching is not really implemented well.

        :param pattern: a dictonary with price list line field as key
                and match value as value
        :return: a boolean
        '''
        res = True
        for field in pattern.keys():
            if field not in self._fields:
                continue
            if getattr(self, field) is None:
                continue
            if field == 'category' and pattern['category']:
                if not self._match_category(pattern['category']):
                    res = False
                    break
            elif self._fields[field]._type == 'many2one':
                if getattr(self, field).id != pattern[field]:
                    res = False
                    break
            elif field == 'quantity':
                if getattr(self, field) > pattern[field]:
                    res = False
                    break
            else:
                if getattr(self, field) != pattern[field]:
                    res = False
                    break
        return res
