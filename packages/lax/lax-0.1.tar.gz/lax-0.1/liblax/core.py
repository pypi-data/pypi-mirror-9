

FMT0 = lambda data: data
FMT1 = lambda data: '\\left(%s\\right)' % data
FMT2 = lambda rhs, lhs: '%s\cdot%s' % (rhs, lhs)


class Chk(object):
    def __init__(self, val):
        self.val = val

    def __add__(self, other):
        return Sum(self, other)

    def __radd__(self, other):
        return Sum(other, self)

    def __sub__(self, other):
        return Sub(self, other)

    def __rsub__(self, other):
        return Sub(other, self)

    def __str__(self, op=None):
        return self.val

    def __mul__(self, other):
        return Mul(self, other)

    def __rmul__(self, other):
        return Mul(other, self)

    def __div__(self, other):
        return Div(self, other)

    def __rdiv__(self, other):
        return Div(other, self)


    def __pow__(self, other):
        return Pow(self, other)

    def __rpow__(self, other):
        return Pow(other, self)

class Num(Chk):
    def __init__(self, val):
        Chk.__init__(self, val)

class Op(Chk):
    def __init__(self, lhs, rhs, arg_map, op_map, default_arg_map, default_op_map):
        self.lhs              = lhs
        self.rhs              = rhs
        self.arg_map          = arg_map
        self.op_map           = op_map
        self.default_arg_map  = default_arg_map
        self.default_op_map   = default_op_map

    def __str__(self, op=None):
        FMT_ARG = self.arg_map.get(op.__class__, self.default_arg_map)
        FMT_OP  = self.op_map.get((self.lhs.__class__, self.rhs.__class__), self.default_op_map)
        data    = FMT_OP(self.lhs.__str__(self), self.rhs.__str__(self))

        return FMT_ARG(data)

class Sum(Op):
    def __init__(self, lhs, rhs):
        SUM_ARG_MAP = {
                    Chk: FMT0,
                    Div: FMT0,
                    Sum: FMT0,
                    Sub: FMT0,
                    Mul: FMT1,
                    Pow: FMT1,
              }

        SUM_OP_MAP = {
                
        }

        DEFAULT_SUM_OP_MAP = lambda rhs, lhs: '%s+%s' % (rhs, lhs)

        Op.__init__(self, lhs, rhs, SUM_ARG_MAP, SUM_OP_MAP, FMT0, 
                    DEFAULT_SUM_OP_MAP)


class Sub(Op):
    def __init__(self, lhs, rhs):
        SUB_ARG_MAP = {
                Chk: FMT0,
                Div: FMT0,
                Sum: FMT0,
                Sub: FMT0,
                Mul: FMT1,
                Pow: FMT1,
              }

        SUB_OP_MAP = {
        
        }

        DEFAULT_SUB_OP_MAP = lambda rhs, lhs: '%s-%s' % (rhs, lhs)

        Op.__init__(self, lhs, rhs, SUB_ARG_MAP, SUB_OP_MAP, FMT0, 
                    DEFAULT_SUB_OP_MAP)



class Mul(Op):
    def __init__(self, lhs, rhs):
        MUL_ARG_MAP = {
                Chk: FMT0, 
                Div: FMT0, 
                Sum: FMT0,
                Sub: FMT0,
                Mul: FMT0,
                Pow: FMT1,

              }

        MUL_OP_MAP = {
            (Num, Num): FMT2,
            (Chk, Num): FMT2,
            (Sum, Num): FMT2,
            (Sub, Num): FMT2,
            (Div, Num): FMT2,
            (Mul, Num): FMT2,
            (Pow, Num): FMT2
        }

        DEFAULT_MUL_OP_MAP = lambda rhs, lhs: '%s%s' % (rhs, lhs)

        Op.__init__(self, lhs, rhs, MUL_ARG_MAP, MUL_OP_MAP, FMT0, 
                    DEFAULT_MUL_OP_MAP)


class Div(Op):
    def __init__(self, lhs, rhs):
        DIV_ARG_MAP = {
                Chk: FMT0,
                Div: FMT0,
                Sum: FMT0,
                Sub: FMT0,
                Mul: FMT0,
                Pow: FMT1,
              }

        DIV_OP_MAP = {

        }


        DEFAULT_DIV_OP_MAP = lambda rhs, lhs: '\\frac{%s}{%s}' % (rhs, lhs)

        Op.__init__(self, lhs, rhs, DIV_ARG_MAP, DIV_OP_MAP, FMT0, 
                    DEFAULT_DIV_OP_MAP)


class Pow(Op):
    def __init__(self, lhs, rhs):
        POW_ARG_MAP = {
                Chk: FMT0,
                Div: FMT0,
                Sum: FMT0,
                Sub: FMT0,
                Mul: FMT0,
                Pow: FMT0,
              }

        POW_OP_MAP = {

        }


        DEFAULT_POW_OP_MAP = lambda lhs, rhs: '\\sqrt[%s]{%s}' % (rhs, lhs)

        Op.__init__(self, lhs, rhs, POW_ARG_MAP, POW_OP_MAP, FMT0, 
                    DEFAULT_POW_OP_MAP)

# class Int(Op):
    # def __init__(self, lhs, rhs):
        # POW_ARG_MAP = {
                # Chk: FMT0,
                # Div: FMT0,
                # Sum: FMT0,
                # Sub: FMT0,
                # Mul: FMT0,
                # Pow: FMT0,
              # }
# 
        # POW_OP_MAP = {
# 
        # }
# 
# 
        # DEFAULT_POW_OP_MAP = lambda lhs, rhs: '\\sqrt[%s]{%s}' % (rhs, lhs)
# 
        # Op.__init__(self, lhs, rhs, POW_ARG_MAP, POW_OP_MAP, FMT0, 
                    # DEFAULT_POW_OP_MAP)
# 




