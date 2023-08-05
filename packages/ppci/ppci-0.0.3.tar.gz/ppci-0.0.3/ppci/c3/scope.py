"""
    This file contains the scope and context classes.
    Scopes are used for scoping modules, functions.
    A context is the space where the whole program lives.
"""

from .astnodes import Constant, Variable, Function, BaseType, Symbol
from .astnodes import ArrayType, StructureType, DefinedType, PointerType
from .astnodes import StructField
from . import astnodes as ast
from ..common import CompilerError


class SemanticError(CompilerError):
    """ Error thrown when a semantic issue is observed """
    pass


class Scope:
    """ A scope contains all symbols in a scope. It also has a parent scope,
        when looking for a symbol, also the parent scopes are checked. """
    def __init__(self, parent=None):
        self.symbols = {}
        self.parent = parent

    def __iter__(self):
        # Iterate in a deterministic manner:
        return iter(self.constants + self.variables + self.functions)

    @property
    def syms(self):
        """ Get all the symbols defined in this scope """
        syms = self.symbols.values()
        return sorted(syms, key=lambda v: v.name)

    @property
    def types(self):
        """ Returns all the types in this scope """
        return [s for s in self.syms if isinstance(s, DefinedType)]

    @property
    def constants(self):
        """ All defined constants in this scope """
        return [s for s in self.syms if type(s) is Constant]

    @property
    def variables(self):
        """ All variables defined in the current scope """
        return [s for s in self.syms if isinstance(s, Variable)]

    @property
    def functions(self):
        """ Gets all the functions in the current scope """
        return [s for s in self.syms if type(s) is Function]

    def get_symbol(self, name):
        """ Get symbol from this or parent scope """
        if name in self.symbols:
            return self.symbols[name]
        # Look for symbol:
        elif self.parent:
            return self.parent.get_symbol(name)
        else:
            raise KeyError(name)

    def __getitem__(self, key):
        return self.get_symbol(key)

    def has_symbol(self, name, include_parent=True):
        """ Check if name is a defined symbol in this or parent scope """
        if name in self.symbols:
            return True
        elif self.parent and include_parent:
            return self.parent.has_symbol(name)
        else:
            return False

    def __contains__(self, name):
        return self.has_symbol(name)

    def add_symbol(self, sym):
        """ Add a symbol to this scope """
        assert sym.name not in self.symbols
        assert isinstance(sym, Symbol)
        self.symbols[sym.name] = sym

    def __repr__(self):
        return 'Scope with {} symbols'.format(len(self.symbols))


def create_top_scope(target):
    """ Create a scope that is the root of the scope tree. This includes
        the built-in types """
    scope = Scope()

    # stdlib types:
    scope.add_symbol(BaseType('uint64_t', 8))
    scope.add_symbol(BaseType('uint32_t', 4))
    scope.add_symbol(BaseType('uint16_t', 2))
    scope.add_symbol(BaseType('uint8_t', 1))

    # buildin types:
    int_type = BaseType('int', target.byte_sizes['int'])
    scope.add_symbol(int_type)
    scope.add_symbol(BaseType('double', 8))
    scope.add_symbol(BaseType('void', 0))
    scope.add_symbol(BaseType('bool', 1))
    byte_type = BaseType('byte', 1)
    scope.add_symbol(byte_type)

    # Construct string type from others:
    len_field = StructField('len', int_type)
    txt = StructField('txt', ArrayType(byte_type, 0))
    string_type = PointerType(StructureType([len_field, txt]))
    string_def_type = DefinedType('string', string_type, None)
    scope.add_symbol(string_def_type)
    return scope


class Context:
    """ A context is the space where all modules live in.
        It is actually the container of modules and the top
        level scope.
    """
    def __init__(self, target):
        self.scope = create_top_scope(target)
        self.module_map = {}
        self.const_map = {}
        self.var_map = {}    # Maps variables to storage locations.
        self.const_workset = set()
        self.pointerSize = 4

    def has_module(self, name):
        """ Check if a module with the given name exists """
        return name in self.module_map

    def get_module(self, name):
        """ Gets or creates the module with the given name """
        if name not in self.module_map:
            self.module_map[name] = ast.Module(name, None)
        return self.module_map[name]

    def get_type(self, name):
        """ Get the type with the given name """
        typ = self.scope[name]
        return typ

    @property
    def modules(self):
        """ Get all the modules in this context """
        return self.module_map.values()

    def resolve_symbol(self, sym):
        """ Find out what is designated with x """
        if type(sym) is ast.Member:
            base = self.resolve_symbol(sym.base)
            if type(base) is not ast.Module:
                raise SemanticError('Base is not a module', sym.loc)
            scope = base.innerScope
            name = sym.field
        elif type(sym) is ast.Identifier:
            scope = sym.scope
            name = sym.target
        else:
            raise NotImplementedError(str(sym))

        if name in scope:
            sym = scope[name]
        else:
            raise SemanticError('{} undefined'.format(name), sym.loc)
        assert isinstance(sym, ast.Symbol)
        return sym

    def get_constant_value(self, const):
        """ Get the constant value, calculate if required """
        assert isinstance(const, ast.Constant)
        if const not in self.const_map:
            if const in self.const_workset:
                varnames = ', '.join(wc.name for wc in self.const_workset)
                msg = 'Constant loop detected involving: {}'.format(varnames)
                raise SemanticError(msg, const.loc)
            self.const_workset.add(const)
            self.const_map[const] = self.eval_const(const.value)
            self.const_workset.remove(const)
        return self.const_map[const]

    def eval_const(self, expr):
        """ Evaluates a constant expression. This is done by first generating
            ir-code, to check for types, and then evaluating this code """

        # TODO: check types!!
        assert isinstance(expr, ast.Expression)
        if isinstance(expr, ast.Literal):
            return expr.val
        elif isinstance(expr, ast.Binop):
            a = self.eval_const(expr.a)
            b = self.eval_const(expr.b)
            if expr.op == '+':
                return a + b
            elif expr.op == '-':
                return a - b
            elif expr.op == '*':
                return a * b
        elif isinstance(expr, ast.Identifier):
            target = self.resolve_symbol(expr)
            if isinstance(target, ast.Constant):
                return self.get_constant_value(target)
            else:
                raise SemanticError('Cannot evaluate {}'.format(expr), None)
        else:
            raise SemanticError('Cannot evaluate constant {}'
                                .format(expr), None)

    def get_common_type(self, a, b):
        """ Determine the greatest common type.
            This is used for coercing binary operators.
            For example
                int + float -> float
                byte + int -> int
                byte + byte -> byte
                pointer to x + int -> pointer to x
        """
        intType = self.get_type('int')
        byteType = self.get_type('byte')
        table = {
            (intType, intType): intType,
            (intType, byteType): intType,
            (byteType, intType): intType,
            (byteType, byteType): byteType,
            (intType, ast.PointerType): intType,
            }
        loc = a.loc
        typ_a = self.the_type(a.typ)
        typ_b = self.the_type(b.typ)
        # Handle pointers:
        if isinstance(typ_a, ast.PointerType) and \
                self.equal_types(typ_b, 'int'):
            return typ_a

        # Handle non-pointers:
        key = (typ_a, typ_b)
        if key not in table:
            raise SemanticError(
                "Types {} and {} do not commute".format(typ_a, typ_b), loc)
        return table[(typ_a, typ_b)]

    def the_type(self, typ, reveil_defined=True):
        """ Recurse until a 'real' type is found
            When reveil_defined is True, defined types are resolved to
            their backing types.
        """
        # Convenience:
        if type(typ) is str:
            typ = self.get_type(typ)

        # Find the type:
        if type(typ) is ast.DefinedType:
            if reveil_defined:
                typ = self.the_type(typ.typ)
        elif type(typ) in [ast.Identifier, ast.Member]:
            typ = self.the_type(self.resolve_symbol(typ), reveil_defined)
        elif isinstance(typ, ast.Type):
            # This case also catches the defined type!
            # TODO: make this if sequence less error prone..
            pass
        else:
            raise NotImplementedError(str(typ))
        assert isinstance(typ, ast.Type)
        return typ

    def size_of(self, typ):
        """ Determine the byte size of a type """
        typ = self.the_type(typ)

        if type(typ) is ast.BaseType:
            return typ.byte_size
        elif type(typ) is ast.StructureType:
            return sum(self.size_of(mem.typ) for mem in typ.mems)
        elif type(typ) is ast.ArrayType:
            if isinstance(typ.size, ast.Expression):
                num = self.eval_const(typ.size)
            else:
                num = int(typ.size)
            return num * self.size_of(typ.element_type)
        elif type(typ) is ast.PointerType:
            return self.pointerSize
        else:
            raise NotImplementedError(str(typ))

    def equal_types(self, a, b, byname=False):
        """ Compare types a and b for structural equavalence.
            if byname is True stop on defined types.
        """
        # Recurse into named types:
        a = self.the_type(a, not byname)
        b = self.the_type(b, not byname)

        # Check types for sanity:
        self.check_type(a)
        self.check_type(b)

        # Do structural equivalence check:
        if type(a) is type(b):
            if type(a) is ast.BaseType:
                return a.name == b.name
            elif type(a) is ast.PointerType:
                # If a pointed type is detected, stop structural
                # equivalence:
                return self.equal_types(a.ptype, b.ptype, byname=True)
            elif type(a) is ast.StructureType:
                if len(a.mems) != len(b.mems):
                    return False
                return all(self.equal_types(am.typ, bm.typ) for am, bm in
                           zip(a.mems, b.mems))
            elif type(a) is ast.ArrayType:
                return self.equal_types(a.element_type, b.element_type)
            elif type(a) is ast.DefinedType:
                # Try by name in case of defined types:
                return a.name == b.name
            else:
                raise NotImplementedError('{} not implemented'.format(type(a)))
        return False

    def check_type(self, t, first=True, byname=False):
        """ Determine struct offsets and check for recursiveness by using
            mark and sweep algorithm.
            The calling function could call this function with first set
            to clear the marks.
        """

        # Reset the mark and sweep:
        if first:
            self.got_types = set()

        # Resolve the type:
        t = self.the_type(t, not byname)

        # Check for recursion:
        if t in self.got_types:
            raise SemanticError('Recursive data type {}'.format(t), None)

        if type(t) is ast.BaseType:
            pass
        elif type(t) is ast.PointerType:
            # If a pointed type is detected, stop structural
            # equivalence:
            self.check_type(t.ptype, first=False, byname=True)
        elif type(t) is ast.StructureType:
            self.got_types.add(t)
            # Setup offsets of fields. Is this the right place?:
            # TODO: move this struct offset calculation.
            offset = 0
            for struct_member in t.mems:
                self.check_type(struct_member.typ, first=False)
                struct_member.offset = offset
                offset = offset + self.size_of(struct_member.typ)
        elif type(t) is ast.ArrayType:
            self.check_type(t.element_type, first=False)
        elif type(t) is ast.DefinedType:
            pass
        else:
            raise NotImplementedError('{} not implemented'.format(type(t)))
