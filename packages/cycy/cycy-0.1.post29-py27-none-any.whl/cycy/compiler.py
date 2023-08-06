from characteristic import Attribute, attributes

from cycy import bytecode
from cycy.objects import W_Char, W_Function, W_Int32, W_String
from cycy.parser import ast


@attributes(
    [
        Attribute(name="instructions"),
        Attribute(name="constants"),
        Attribute(name="variables"),
    ],
    apply_with_init=False,
)
class Context(object):
    """
    The compilation context, which stores the state during interpretation.

    .. attribute:: instructions

        a :class:`list` of bytecode instructions (:class:`int`\ s)

    .. attribute:: constants

        the :class:`list` of contents that the bytecode indexes into.

        .. note::

            These are C-level objects (i.e. they're wrapped).

    .. attribute:: variables

        a mapping between variable names (:class:`str`\ s) and the
        indices in an array that they should be assigned to

    """

    def __init__(self):
        self.instructions = []
        self.constants = []
        self.variables = {}

    def emit(self, byte_code, arg=bytecode.NO_ARG):
        self.instructions.append(byte_code)
        self.instructions.append(arg)

    def register_variable(self, name):
        self.variables[name] = len(self.variables)
        return len(self.variables) - 1

    def register_constant(self, constant):
        self.constants.append(constant)
        return len(self.constants) - 1

    def build(self, arguments=[], name="<input>"):
        return bytecode.Bytecode(
            instructions=self.instructions,
            name=name,
            arguments=arguments,
            constants=self.constants,
            variables=self.variables,
        )

class __extend__(ast.Function):
    def compile(self, context):
        for param in self.params:
            param.compile(context=context)
        self.body.compile(context=context)

class __extend__(ast.Block):
    def compile(self, context):
        for statement in self.statements:
            statement.compile(context=context)

class __extend__(ast.BinaryOperation):
    def compile(self, context):
        # compile RHS then LHS so that their results end up on the stack
        # in reverse order; then we can pop in order in the interpreter
        self.right.compile(context=context)
        self.left.compile(context=context)
        context.emit(bytecode.BINARY_OPERATION_BYTECODE[self.operator])

class __extend__(ast.Int32):
    def compile(self, context):
        wrapped = W_Int32(value=self.value)
        index = context.register_constant(wrapped)
        context.emit(bytecode.LOAD_CONST, index)

class __extend__(ast.Char):
    def compile(self, context):
        wrapped = W_Char(char=self.value)
        index = context.register_constant(wrapped)
        context.emit(bytecode.LOAD_CONST, index)


class __extend__(ast.Assignment):
    def compile(self, context):
        self.right.compile(context=context)
        index = context.variables.get(self.left.name, -42)
        if index == -42:
            raise Exception("Attempt to use undeclared variable '%s'" % self.left.name)
        context.emit(bytecode.STORE_VARIABLE, index)

class __extend__(ast.String):
    def compile(self, context):
        wrapped = W_String(value=self.value)
        index = context.register_constant(wrapped)
        context.emit(bytecode.LOAD_CONST, index)

class __extend__(ast.ReturnStatement):
    def compile(self, context):
        if self.value:
            self.value.compile(context)
        context.emit(bytecode.RETURN, int(bool(self.value)))

class __extend__(ast.For):
    def compile(self, context):
        jump_ix = len(context.instructions)
        self.condition.compile(context)
        jump_nz = len(context.instructions)
        context.emit(bytecode.JUMP_IF_ZERO, 0)
        self.body.compile(context)
        context.emit(bytecode.JUMP, jump_ix)
        context.instructions[jump_nz + 1] = len(context.instructions)

class __extend__(ast.VariableDeclaration):
    def compile(self, context):
        vtype = self.vtype
        assert isinstance(vtype, ast.Type)

        if vtype.base_type == "int" and vtype.length == 32:
            variable_index = context.register_variable(self.name)
            if self.value:
                self.value.compile(context)
                context.emit(bytecode.STORE_VARIABLE, variable_index)
            # else we've declared the variable, but it is
            # uninitialized... TODO: how to handle this
        elif vtype.base_type == "pointer":
            ref = vtype.reference
            assert isinstance(ref, ast.Type)
            if ref.base_type == "int" and ref.length == 8:
                variable_index = context.register_variable(self.name)
                if self.value:
                    self.value.compile(context)
                    context.emit(bytecode.STORE_VARIABLE, variable_index)
        else:
            raise NotImplementedError("Variable type %s not supported" % vtype)

class __extend__(ast.Variable):
    def compile(self, context):
        variable_index = context.variables.get(self.name, -42)
        if variable_index == -42:
            # XXX: this should be either a runtime or compile time exception
            raise Exception("Attempt to use undeclared variable '%s'" % self.name)
        context.emit(bytecode.LOAD_VARIABLE, variable_index)

class __extend__(ast.Call):
    def compile(self, context):
        num_args = len(self.args)
        assert num_args < 256  # technically probably should be smaller?
        for arg in reversed(self.args):
            arg.compile(context)
        if self.name == "putchar":
            # TODO we should implement putchar in bytecode once we have
            # working asm blocks
            context.emit(bytecode.PUTC, bytecode.NO_ARG)
            return
        wrapped_func = W_Function(self.name, len(self.args))
        func_index = context.register_constant(wrapped_func)
        context.emit(bytecode.CALL, func_index)

class __extend__(ast.ArrayDereference):
    def compile(self, context):
        self.index.compile(context=context)
        self.array.compile(context=context)

        context.emit(bytecode.DEREFERENCE, bytecode.NO_ARG)


def compile(an_ast):
    context = Context()
    an_ast.compile(context=context)
    if isinstance(an_ast, ast.Function):
        arguments = []
        for param in an_ast.params:
            assert isinstance(param, ast.VariableDeclaration)
            arguments.append(param.name)
    else:
        arguments = []
    return context.build(arguments=arguments, name="<don't know>")
