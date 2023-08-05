# -*- coding: utf-8 -*-

"""
    This module implements a Python-to-SQLAlchemy syntax parser.
    Allows the SQLAlchemy data-layer to seamlessy respond to a
    Python-like query.

    :copyright: (c) 2013 by Andrew Mleczko and Tomasz Jezierski (Tefnet)
    :license: BSD, see LICENSE for more details.
"""
import re
import ast
import operator as sqla_op
import json

from eve.utils import str_to_date
from sqlalchemy.ext.associationproxy import AssociationProxy
from sqlalchemy.sql import expression as sqla_exp


class ParseError(ValueError):
    pass


def parse_dictionary(filter_dict, model):
    """
    Parse a dictionary into a list of SQLAlchemy BinaryExpressions to be used
    in query filters.

    :param filter_dict: Dictionary to convert
    :param model: SQLAlchemy model class used to create the BinaryExpressions
    :return list: List of conditions as SQLAlchemy BinaryExpressions
    """
    if len(filter_dict) == 0:
        return []

    conditions = []

    for k, v in filter_dict.items():
        # firts let's check with the expression parser

        try:
            conditions += parse('{0}{1}'.format(k, v), model)
        except ParseError:
            pass
        else:
            continue

        attr = getattr(model, k)

        if isinstance(attr, AssociationProxy):
            conditions.append(attr.contains(v))

        elif hasattr(attr, 'property') and \
                hasattr(attr.property, 'remote_side'):  # a relation
            for fk in attr.property.remote_side:
                conditions.append(sqla_op.eq(fk, v))

        else:
            try:
                new_o, v = parse_sqla_operators(v)
                new_filter = getattr(attr, new_o)(v)
            except (TypeError, ValueError):  # json/sql parse error
                if isinstance(v, list):  # we have an array
                    new_filter = attr.in_(v)
                else:
                    new_filter = sqla_op.eq(attr, v)
            conditions.append(new_filter)

    return conditions


def parse_sqla_operators(expression):
    """
    Parse expressions like:
        like('%john%')
        ilike('john%')
        in_(['a','b'])
    """
    m = re.match(r"(?P<operator>\w+)\((?P<value>.+)\)", expression)
    if m:
        o = m.group('operator')
        v = json.loads(m.group('value'))
        return o, v


def parse(expression, model):
    """
    Given a python-like conditional statement, returns the equivalent
    SQLAlchemy-like query expression. Conditional and boolean operators
    (==, <=, >=, !=, >, <) are supported.
    """
    v = SQLAVisitor(model)
    v.visit(ast.parse(expression))
    return v.sqla_query


class SQLAVisitor(ast.NodeVisitor):
    """Implements the python-to-sql parser. Only Python conditional
    statements are supported, however nested, combined with most common compare
    and boolean operators (And and Or).

    Supported compare operators: ==, >, <, !=, >=, <=
    Supported boolean operators: And, Or
    """
    op_mapper = {
        ast.Eq: sqla_op.eq,
        ast.Gt: sqla_op.gt,
        ast.GtE: sqla_op.ge,
        ast.Lt: sqla_op.lt,
        ast.LtE: sqla_op.le,
        ast.NotEq: sqla_op.ne,
        ast.Or: sqla_exp.or_,
        ast.And: sqla_exp.and_
    }

    def __init__(self, model):
        super(SQLAVisitor, self).__init__()
        self.model = model
        self.sqla_query = []
        self.ops = []
        self.current_value = None

    def visit_Module(self, node):
        """ Module handler, our entry point.
        """
        self.sqla_query = []
        self.ops = []
        self.current_value = None

        # perform the magic.
        self.generic_visit(node)

        # if we didn't obtain a query, it is likely that an unsupported
        # python expression has been passed.
        if not len(self.sqla_query):
            raise ParseError("Only conditional statements with boolean "
                             "(and, or) and comparison operators are "
                             "supported.")

    def visit_Expr(self, node):
        """ Make sure that we are parsing compare or boolean operators
        """
        if not (isinstance(node.value, ast.Compare) or
                isinstance(node.value, ast.BoolOp)):
            raise ParseError("Will only parse conditional statements")
        self.generic_visit(node)

    def visit_Compare(self, node):
        """ Compare operator handler.
        """

        self.visit(node.left)
        left = getattr(self.model, self.current_value)

        operation = self.op_mapper[node.ops[0].__class__]

        if node.comparators:
            comparator = node.comparators[0]
            self.visit(comparator)

        value = self.current_value

        if self.ops:
            self.ops[-1]['args'].append(operation(left, value))
        else:
            self.sqla_query.append(operation(left, value))

    def visit_BoolOp(self, node):
        """ Boolean operator handler.
        """
        op = self.op_mapper[node.op.__class__]
        self.ops.append({'op': op, 'args': []})
        for value in node.values:
            self.visit(value)

        tops = self.ops.pop()
        if self.ops:
            self.ops[-1]['args'].append(tops['op'](*tops['args']))
        else:
            self.sqla_query.append(tops['op'](*tops['args']))

    def visit_Call(self, node):
        # TODO ?
        pass

    def visit_Attribute(self, node):
        # FIXME ?
        self.visit(node.value)
        self.current_value += "." + node.attr

    def visit_Name(self, node):
        """ Names """
        self.current_value = node.id

    def visit_Num(self, node):
        """ Numbers """
        self.current_value = node.n

    def visit_Str(self, node):
        """ Strings """
        try:
            value = str_to_date(node.s)
            self.current_value = value if value is not None else node.s
        except ValueError:
            self.current_value = node.s
