"""
Parser for parsing a regular expression.
Take a string representing a regular expression and return the root node of its
parse tree.

usage::

    root_node = parse_regex('(hello|world)')

Remarks:
- The regex parser processes multiline, it ignores all whitespace and supports
  multiple named groups with the same name and #-style comments.

Limitations:
- Lookahead is not supported.
"""
from __future__ import unicode_literals
import re

__all__ = (
    'Repeat',
    'Variable',
    'Regex',
    'Lookahead',

    'tokenize_regex',
    'parse_regex',
)


class Node(object):
    """
    Base class for all the grammar nodes.
    (You don't initialize this one.)
    """
    def __add__(self, other_node):
        return Sequence([self, other_node])

    def __or__(self, other_node):
        return Any([self, other_node])


class Any(Node):
    """
    Union operation (OR operation) between several grammars. You don't
    initialize this yourself, but it's a result of a "Grammar1 | Grammar2"
    operation.
    """
    def __init__(self, children):
        self.children = children

    def __or__(self, other_node):
        return Any(self.children + [other_node])

    def __repr__(self):
        return 'Any(%r)' % (self.children, )


class Sequence(Node):
    """
    Concatenation operation of several grammars. You don't initialize this
    yourself, but it's a result of a "Grammar1 + Grammar2" operation.
    """
    def __init__(self, children):
        self.children = children

    def __add__(self, other_node):
        return Sequence(self.children + [other_node])

    def __repr__(self):
        return 'Sequence(%r)' % (self.children, )


class Regex(Node):
    """
    Regular expression.
    """
    def __init__(self, regex):
        re.compile(regex)  # Validate

        self.regex = regex

    def __repr__(self):
        return '/%s/' % (self.regex, )


class Lookahead(Node):
    """
    Lookahead expression.
    """
    def __init__(self, childnode, negative=False):
        self.childnode = childnode
        self.negative = negative

    def __repr__(self):
        return 'Lookahead(%r)' % self.childnode


class Variable(Node):
    """
    Mark a variable in the regular grammar. This will be translated into a
    named group. Each variable can have his own completer, validator, etc..

    :param childnode: The grammar which is wrapped inside this variable.
    :param varname: String.
    """
    def __init__(self, childnode, varname=None):
        self.childnode = childnode
        self.varname = varname

    def __repr__(self):
        return 'Variable(childnode=%r, varname=%r)' % (self.childnode, self.varname)


class Repeat(Node):
    def __init__(self, childnode, min_repeat=0, max_repeat=None):
        self.childnode = childnode
        self.min_repeat = min_repeat
        self.max_repeat = max_repeat

    def __repr__(self):
        return 'Repeat(childnode=%r)' % (self.childnode, )


def tokenize_regex(input):
    """
    Takes a string, representing a regular expression as input, and tokenizes
    it.

    :param input: string, representing a regular expression.
    :returns: List of tokens.
    """
    # Regular expression for tokenizing other regular expressions.
    p = re.compile(r'''^(
        \(\?P\<[a-zA-Z0-9_-]+\>  | # Start of named group.
        \(\?#[^)]*\)             | # Comment
        \(\?=                    | # Start of lookahead assertion
        \(\?!                    | # Start of negative lookahead assertion
        \(\?<=                   | # If preceded by.
        \(\?<                    | # If not preceded by.
        \(?:                     | # Start of group. (non capturing.)
        \(                       | # Start of group.
        \(?[iLmsux]              | # Flags.
        \(?P=[a-zA-Z]+\)         | # Back reference to named group
        \)                       | # End of group.
        \{[^{}]*\}               | # Repetition
        \* | \+ | \?             | # Repetition
        \*\? | \+\? | \?\?\      | # Non greedy repetition.
        \#.*\n                   | # Comment
        \\. |

        # Character group.
        \[
            ( [^\]\\]  |  \\.)*
        \]                  |

        [^(){}]             |
        .
    )''', re.VERBOSE)

    tokens = []

    while input:
        m = p.match(input)
        if m:
            token, input = input[:m.end()], input[m.end():]
            if not token.isspace():
                tokens.append(token)
        else:
            raise Exception('Could not tokenize input regex.')

    return tokens


def parse_regex(regex_tokens):
    """
    Takes a list of tokens from the tokenizer, and returns a parse tree.
    """
    # We add a closing brace because that represents the final pop of the stack.
    tokens = [')'] + regex_tokens[::-1]

    def wrap(lst):
        """ Turn list into sequence when it contains several items. """
        if len(lst) == 1:
            return lst[0]
        else:
            return Sequence(lst)

    def _parse():
        or_list = []
        result = []

        def wrapped_result():
            if or_list == []:
                return wrap(result)
            else:
                or_list.append(result)
                return Any([wrap(i) for i in or_list])

        while tokens:
            t = tokens.pop()

            if t.startswith('(?P<'):
                variable = Variable(_parse(), varname=t[4:-1])
                result.append(variable)

            elif t == '*':
                result[-1] = Repeat(result[-1])

            elif t == '+':
                result[-1] = Repeat(result[-1], min_repeat=1)

            elif t == '?':
                if result == []:
                    raise Exception('Nothing to repeat.' + repr(tokens))
                else:
                    result[-1] = Repeat(result[-1], min_repeat=0, max_repeat=1)

            elif t == '|':
                or_list.append(result)
                result = []

            elif t in ('(', '(?:'):
                result.append(_parse())

            elif t == '(?!':
                result.append(Lookahead(_parse(), negative=True))

            elif t == '(?=':
                result.append(Lookahead(_parse(), negative=False))

            elif t == ')':
                return wrapped_result()

            elif t.startswith('#'):
                pass

            elif t.startswith('{'):
                # TODO: implement!
                raise Exception('{}-style repitition not yet supported' % t)

            elif t.startswith('(?'):
                raise Exception('%r not supported' % t)

            elif t.isspace():
                pass
            else:
                result.append(Regex(t))

        raise Exception("Expecting ')' token")

    result = _parse()

    if len(tokens) != 0:
        raise Exception("Unmatched parantheses.")
    else:
        return result
