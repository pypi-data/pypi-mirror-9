import operator

# Operators used in binary expressions.
OP_AND = 'and'
OP_OR = 'or'

OP_EQ = '=='
OP_NE = '!='
OP_LT = '<'
OP_LTE = '<='
OP_GT = '>'
OP_GTE = '>='
# OP_IN = 'in'

opfunc = {
    OP_AND: operator.__and__,
    OP_OR:  operator.__or__,
    OP_EQ:  operator.eq,
    OP_NE:  operator.ne,
    OP_LT:  operator.lt,
    OP_LTE: operator.le,
    OP_GT:  operator.gt,
    OP_GTE: operator.ge
}

class Node(object):
    """Base-class for any part of a query which shall be composable."""
    def __init__(self, name=None):
        self.name = name

    def _e(op, inv=False):
        """
        Lightweight factory which returns a method that builds an Expression
        consisting of the left-hand and right-hand operands, using `op`.
        """
        def inner(self, rhs):
            if inv:
                return Expression(rhs, op, self)
            return Expression(self, op, rhs)
        return inner

    __and__ = _e(OP_AND)
    __or__ = _e(OP_OR)

    def __eq__(self, rhs):
        return Expression(self, OP_EQ, rhs)
    def __ne__(self, rhs):
        return Expression(self, OP_NE, rhs)

    __lt__ = _e(OP_LT)
    __le__ = _e(OP_LTE)
    __gt__ = _e(OP_GT)
    __ge__ = _e(OP_GTE)
    # __lshift__ = _e(OP_IN)

    def __str__(self):
        if self.name: return self.name
        else: return repr(self)

class Expression(Node):
    """A binary expression, e.g `foo == 1` or `bar < 7`"""
    def __init__(self, lhs, op, rhs, flat=False):
        super(Expression, self).__init__()
        self.lhs = lhs
        self.op = op
        self.rhs = rhs
        self.flat = flat

    def __str__(self):
        return '(' + str(self.lhs) + ' ' + str(self.op) + ' ' + str(self.rhs) + ')'

    def eval(self, target):
        if self.op == OP_AND or self.op == OP_OR:
            return opfunc[self.op](self.lhs.eval(target), self.rhs.eval(target))
        else:
            if target.has_key(self.lhs.name):
                return opfunc[self.op](target[self.lhs.name], self.rhs)
            else:
                return False

