from abc import ABCMeta, abstractproperty
from dis import Bytecode, opname, opmap, hasjabs, hasjrel, HAVE_ARGUMENT
from types import CodeType

# Opcodes with attribute access.
ops = type(
    'Ops', (dict,), {'__getattr__': lambda self, name: self[name]},
)(opmap)


def _sparse_args(instrs):
    """
    Makes the arguments sparse so that instructions live at the correct
    index for the jump resolution step.
    The `None` instructions will be filtered out.
    """
    for instr in instrs:
        yield instr
        if instr.opcode >= HAVE_ARGUMENT:
            yield None
            yield None


class CodeTransformer(object, metaclass=ABCMeta):
    """
    A code object transformer, simmilar to the AstTransformer from the ast
    module.
    """

    # TODO: Calculate this for the user.
    @abstractproperty
    def stack_modifier(self):
        """
        How much does this transformer affect the maximum stack usage.
        """
        return 0

    def __init__(self):
        self._instrs = None
        self._consts = None

    def __getitem__(self, idx):
        return self._instrs[idx]

    def index(self, instr):
        """
        Returns the index of an `Instruction`.
        """
        return self._instrs.index(instr)

    def __iter__(self):
        return iter(self._instrs)

    def const_index(self, obj):
        """
        The index of a constant.
        If `obj` is not already a constant, it will be added to the consts
        and given a new const index.
        """
        try:
            return self._consts[obj]
        except KeyError:
            self._consts[obj] = ret = self._const_idx
            self._const_idx += 1
            return ret

    def visit_generic(self, instr):
        if instr is None:
            yield None
            return

        yield from getattr(self, 'visit_' + instr.opname, lambda *a: a)(instr)

    def visit_const(self, const):
        """
        Override this method to transform the `co_consts` of the code object.
        """
        if isinstance(const, CodeType):
            return type(self).visit(const)
        else:
            return const

    def _id(self, obj):
        """
        Identity function.
        """
        return obj

    visit_name = _id
    visit_varname = _id
    visit_freevar = _id
    visit_cellvar = _id
    visit_default = _id

    del _id

    def visit(self, co, name=None):
        """
        Visit a code object, applying the transforms.
        """
        # WARNING:
        # This is setup in this double assignment way because jump args
        # must backreference their original jump target before any transforms.
        # Don't refactor this into a single pass.
        self._instrs = tuple(_sparse_args([
            Instruction(b.opcode, b.arg) for b in Bytecode(co)
        ]))
        self._instrs = tuple(filter(bool, (
            instr and instr._with_jmp_arg(self) for instr in self._instrs
        )))

        self._consts = {
            self.visit_const(k): idx for idx, k in enumerate(co.co_consts)
        }

        self._const_idx = len(co.co_consts)  # used for adding new consts.

        # Apply the transforms.
        self._instrs = tuple(_sparse_args(sum(
            (tuple(self.visit_generic(_instr)) for _instr in self),
            (),
        )))

        return CodeType(
            co.co_argcount,
            co.co_kwonlyargcount,
            co.co_nlocals,
            co.co_stacksize + self.stack_modifier,
            co.co_flags,
            b''.join(
                (instr or b'') and instr.to_bytecode(self) for instr in self
            ),
            tuple(sorted(self._consts, key=lambda c: self._consts[c])),
            tuple(self.visit_name(n) for n in co.co_names),
            tuple(self.visit_varname(n) for n in co.co_varnames),
            co.co_filename,
            name if name is not None else co.co_name,
            co.co_firstlineno,
            co.co_lnotab,
            tuple(self.visit_freevar(c) for c in co.co_freevars),
            tuple(self.visit_cellvar(c) for c in co.co_cellvars),
        )

    def __repr__(self):
        return '<{cls}: {instrs!r}>'.format(
            cls=type(self).__name__,
            instrs=self._instrs,
        )

    def LOAD_CONST(self, const):
        """
        Shortcut for loading a constant value.
        Returns an instruction object.
        """
        return Instruction(ops.LOAD_CONST, self.const_index(const))


class Instruction(object):
    """
    An abstraction of an instruction.
    """
    def __init__(self, opcode, arg=None):
        self.opcode = opcode
        self.arg = arg
        self.reljmp = False
        self.absjmp = False
        self._stolen_by = None

    def _with_jmp_arg(self, transformer):
        """
        If this is a jump opcode, then convert the arg to the instruction
        to jump to.
        """
        opcode = self.opcode
        if opcode in hasjrel:
            self.arg = transformer[self.index(transformer) + self.arg - 1]
            self.reljmp = True
        elif opcode in hasjabs:
            self.arg = transformer[self.arg]
            self.absjmp = True
        return self

    @property
    def opname(self):
        return opname[self.opcode]

    def to_bytecode(self, transformer):
        """
        Convert an instruction to the bytecode form inside of a transformer.
        This needs a transformer as context because it must know how to
        resolve jumps.
        """
        bs = bytes((self.opcode,))
        arg = self.arg
        if isinstance(arg, Instruction):
            if self.absjmp:
                bs += arg.jmp_index(transformer).to_bytes(2, 'little')
            elif self.reljmp:
                bs += (
                    arg.jmp_index(transformer) - self.index(transformer) + 1
                ).to_bytes(2, 'little')
            else:
                raise ValueError('must be relative or absolute jump')
        elif arg is not None:
            bs += arg.to_bytes(2, 'little')
        return bs

    def index(self, transformer):
        """
        This instruction's index within a transformer.
        """
        return transformer.index(self)

    def jmp_index(self, transformer):
        """
        This instruction's jump index within a transformer.
        This checks to see if it was stolen.
        """
        return (self._stolen_by or self).index(transformer)

    def __repr__(self):
        arg = self.arg
        return '<{cls}: {opname}{arg}>'.format(
            cls=type(self).__name__,
            opname=self.opname,
            arg=': ' + str(arg) if self.arg is not None else '',
        )

    def steal(self, instr):
        """
        Steal the jump index off of `instr`.
        This makes anything that would have jumped to `instr` jump to
        this Instruction instead.
        """
        instr._stolen_by = self
        return self
