#!/usr/bin/env python
"""Extendable command bot quirk, intended for fun."""
from __future__ import print_function
import re
import random

class PrefixError(Exception):
    """Raised when the prefix of the message does not match."""


class ParserError(Exception):
    """Raised when the parser attempts to parse garbage."""


class ParserGraft(object):
    """Graft objects that parsers modify to keep track of parsed tokens."""
    __slots__ = ('value', 'index')

    def __init__(self, value, index):
        self.value = value
        self.index = index

    def __repr__(self):
        return (
            '%s(%r, %d)'
            % (self.__class__.__name__, self.value, self.index)
            )


class BaseParser(object):
    __slots__ = ()

    def __call__(self, tokens, seek=0):
        NotImplemented

    def __add__(self, other):
        return ConcatParser(self, other)

    def __or__(self, other):
        return SelectParser(self, other)

    def __xor__(self, other):
        return WrapprParser(self, other)


class ItemParser(BaseParser):
    """Parses tokens based on their values. Case-sensitive."""
    __slots__ = ('ref',)

    def __init__(self, ref):
        self.ref = ref

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.ref)

    def __call__(self, tokens, seek=0):
        try:
            if tokens[seek][0] == self.ref:
                return ParserGraft(tokens[seek][0], seek+1)
        except IndexError:
            pass
        return None


class CapsParser(BaseParser):
    """Parses tokens based on their values. Not case-sensitive."""
    __slots__ = ('ref',)

    def __init__(self, ref):
        self.ref = ref

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.ref)

    def __call__(self, tokens, seek=0):
        try:
            if tokens[seek][0].lower() == self.ref.lower():
                return ParserGraft(tokens[seek][0], seek+1)
        except IndexError:
            pass
        return None


class TagsParser(BaseParser):
    """Parses tokens based on their tags."""
    __slots__ = ('tag',)

    def __init__(self, tag):
        self.tag = tag

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.tag)

    def __call__(self, tokens, seek=0):
        try:
            if tokens[seek][1] == self.tag:
                return ParserGraft(tokens[seek][0], seek+1)
        except IndexError:
            pass
        return None


def isPrimitive(obj):
    return (
        isinstance(obj, ItemParser)
        or isinstance(obj, TagsParser)
        or isinstance(obj, CapsParser)
        or isinstance(obj, OptionParser)
        or isinstance(obj, RepeatParser)
        or isinstance(obj, StrictParser)
        )


class ConcatParser(BaseParser):
    """Parses two expressions if they are found to be concatenated."""
    __slots__ = ('lexp', 'rexp')

    def __init__(self, lexp, rexp):
        self.lexp = lexp
        self.rexp = rexp

    def __repr__(self):
        if (isinstance(self.lexp, self.__class__)
            or isPrimitive(self.lexp)
            ):
            lstr = repr(self.lexp)
        else:
            lstr = '(%r)' % self.lexp
        if (isinstance(self.rexp, self.__class__)
            or isPrimitive(self.rexp)
            ):
            rstr = repr(self.rexp)
        else:
            rstr = '(%r)' % self.rexp
        return lstr + ' + ' + rstr

    def __call__(self, tokens, seek=0):
        lans = self.lexp(tokens, seek)
        if lans:
            rans = self.rexp(tokens, lans.index)
            if rans:
                if isinstance(lans.value, tuple):
                    val = lans.value + (rans.value,)
                else:
                    val = (lans.value, rans.value)
                return ParserGraft(val, rans.index)
        return None


class SelectParser(BaseParser):
    """Parses the first expression if valid, otherwise the second."""
    __slots__ = ('lexp', 'rexp')

    def __init__(self, lexp, rexp):
        self.lexp = lexp
        self.rexp = rexp

    def __repr__(self):
        if (isinstance(self.lexp, self.__class__)
            or isPrimitive(self.lexp)
            ):
            lstr = repr(self.lexp)
        else:
            lstr = '(%r)' % self.lexp
        if (isinstance(self.rexp, self.__class__)
            or isPrimitive(self.rexp)
            ):
            rstr = repr(self.rexp)
        else:
            rstr = '(%r)' % self.rexp
        return lstr + ' | ' + rstr

    def __call__(self, tokens, seek=0):
        return self.lexp(tokens, seek) or self.rexp(tokens, seek)


class WrapprParser(BaseParser):
    """Parses an expression, and wraps the result in a function."""
    __slots__ = ('expr', 'func')

    def __init__(self, expr, func):
        self.expr = expr
        self.func = func

    def __repr__(self):
        if (isinstance(self.expr, self.__class__)
            or isPrimitive(self.expr)
            ):
            lstr = repr(self.expr)
        else:
            lstr = '(%r)' % self.expr
        if (isinstance(self.func, self.__class__)
            or isPrimitive(self.func)
            ):
            rstr = repr(self.func)
        else:
            rstr = '(%r)' % self.func
        return lstr + ' ^ ' + rstr

    def __call__(self, tokens, seek=0):
        value = self.expr(tokens, seek)
        if value:
            return ParserGraft(self.func(value.value), value.index)
        return None


class OptionParser(BaseParser):
    """Parses an expression, but always returns a Graft object."""
    __slots__ = ('expr',)

    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.expr)

    def __call__(self, tokens, seek=0):
        return self.expr(tokens, seek) or ParserGraft(None, seek)


class StrictParser(BaseParser):
    """Parses an expression if the full tokenlist fits its pattern."""
    __slots__ = ('expr',)

    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.expr)

    def __call__(self, tokens, seek=0):
        value = self.expr(tokens, seek)
        if value and value.index == len(tokens):
            return value
        return None


class RepeatParser(BaseParser):
    """Parses an expression until it fails, generating a list."""
    __slots__ = ('expr',)

    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.expr)

    def __call__(self, tokens, seek=0):
        graft = self.expr(tokens, seek)
        if not graft:
            return None
        graftlist = []
        while graft:
            graftlist.append(graft.value)
            index = graft.index
            graft = self.expr(tokens, index)
        return ParserGraft(graftlist, index)


class UnLazyParser(BaseParser):
    """Evaluates the expression it's parsing ONLY when called."""
    __slots__ = ('func', 'expr')

    def __init__(self, func):
        self.func = func
        self.expr = None

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.func)

    def __call__(self, tokens, seek=0):
        if not self.expr:
            self.expr = self.func()
        return self.expr(tokens, seek)


def dice_roller():
    """Sample command function, a dice rolling bot."""
    def execute(ndice, nfaces, mod):
        """Does the actual dice rolling."""
        if ndice > 20:
            return 'Attempted to roll too many dice!'
        if nfaces > 120:
            return 'Attempted to roll dice with too many faces!'
        rolls = [
            random.randrange(nfaces) + 1
            for _ in range(ndice)
            ]
        rollsum = sum(rolls)
        rolltext = ' + '.join(str(roll) for roll in rolls)
        if mod:
            modsgn = '-' if mod < 0 else '+'
            modstr = modsgn + ' ' + str(abs(mod))
            rollstr = (
                'Rolled %dd%d%s%d: '
                % (ndice, nfaces, modsgn, mod)
                )
            return (
                '%s(%s) %s = %d'
                % (rollstr, rolltext, modstr, rollsum + mod)
                )
        return 'Rolled %dd%d: %s = %d' % (ndice, nfaces, rolltext, rollsum)

    def wrapper(parsed):
        """Roll format: <dice>d<faces>[+-]<mod>"""
        # Wraps tuple of tokens in the execute function.
        ndice, _, nfaces, qmod = parsed
        if not qmod or not qmod[0]:
            mod = 0
        else:
            if qmod[0] == '-':
                mod = -int(qmod[1])
            else:
                mod = int(qmod[1])
        return execute(int(ndice), int(nfaces), mod)
    # Parser object application, showing how the pattern:
    # r'^>roll\s+(\d+)\s*d\s*(\d+)\s*([-+]\s*\d+)?$'
    # can be captured and used.
    return StrictParser(
        TagsParser('INT')
        + CapsParser('d')
        + TagsParser('INT')
        + OptionParser(
            (ItemParser('+') | ItemParser('-'))
            + TagsParser('INT')
            )
        ) ^ wrapper


# Add more commands here...


class CommandDispatcher(object):
    """Dispatches commands based on predetermined command functions."""
    __slots__ = ('prefix',)
    __patterns = [
        (re.compile(pattern), tag)
        for pattern, tag in (
            (r'\s+', None),
            (r'[-+]', 'SIGN'),
            (r'([\'"])[^\1]*?\1', 'STRING'),
            (r'(\d+\.\d*|\.\d+)([eE][-+]?\d+)?', 'FLOAT'),
            (r'\d+', 'INT'),
            (r'[a-zA-Z]+', 'WORD'),
            (r'[@#a-zA-Z]\w*', 'NAME'),
            )
        ]
    __commands = {
        'roll': dice_roller(),
        # Add more command name entries here...
        }

    def __init__(self, prefix):
        self.prefix = prefix

    def tokenize(self, msg):
        """Built-in lexer."""
        match = re.match(re.escape(self.prefix), msg)
        if not match:
            raise PrefixError('Prefix does not match')
        # Only proceed if prefix matched.
        tokens = []
        seek = match.end(0)
        msglen = len(msg)
        # Build token list
        while seek < msglen:
            oldseek = seek
            for pattern, tag in self.__patterns:
                match = pattern.match(msg, seek)
                if match:
                    if tag:
                        tokens.append((match.group(0), tag))
                    seek = match.end(0)
                    break
            else:
                raise SyntaxError('Bad character: %s' % msg[seek])
        return tokens

    def dispatch(self, msg):
        """Handles execution flow, dispatching the correct function."""
        try:
            tokens = self.tokenize(msg)
        except PrefixError:
            return msg
        except SyntaxError as exc:
            return exc.args[0]
        else:
            try:
                graft = self.__commands[tokens[0][0]](tokens[1:])
            except KeyError:
                return msg
            else:
                if graft:
                    return graft.value
                return self.__commands[tokens[0][0]].func.__doc__


bot = CommandDispatcher('>')
def quirkbot(msg):
    return bot.dispatch(msg)
quirkbot.command = 'quirkbot'

if __name__ == '__main__':
    print(bot.dispatch('>roll 8d8'))
    print(bot.dispatch('>roll 8d8+8'))
    print(bot.dispatch('>roll 8d8-8'))
    print(bot.dispatch('>roll 8d8+0'))
    print(bot.dispatch('>roll 8d8-0'))

    print(bot.dispatch('!roll 8d8+8'))
    print(bot.dispatch('>call 8d8+8'))
    print(bot.dispatch('>roll bluh'))
    print(bot.dispatch('>roll 1d'))

    print(bot.dispatch('>roll 100d8+8'))
    print(bot.dispatch('>roll 8d200+8'))
