import re
from collections import defaultdict

_NEST_SCOPES = {'[': ']', '(': ')', '{': '}'}
_STR_SCOPES = '"' + "'"

#: Regex to find function calls.
_fre = re.compile(r"(\w+)\s?\((.*)\)")


def rewrite(text, kwfmt='_kw_{}'):
    """Rewrite all occurrences of functions calls adding a keyword to each
    non-keyword arg after a keyword arg.

    The generating format for the keyword can be specified using the kwfmt argument
    where the place holder is formatted to a number starting from 0.
    """
    _repl = lambda mo: repl(mo, kwfmt)
    return _fre.sub(_repl, text)


def repl(match):
    """Helper function for rewrite."""

    func, args = match.groups()

    fmt = kwfmt + '={}'
    scopes = defaultdict(int)
    ret = []

    n = -1
    found_first_kw = False
    current, has_kw = '', False

    for c in args + ',':
        in_scope = any(scopes.values())
        in_string = any(scopes[k] for k in _STR_SCOPES)

        if c in _NEST_SCOPES.keys():
            scopes[_NEST_SCOPES[c]] += 1

        elif c in _NEST_SCOPES.values() and not in_string:
            scopes[c] -= 1

        elif c in _STR_SCOPES:
            scopes[c] = not scopes[c]

        elif c == '=' and not in_scope:
            has_kw = True
            found_first_kw = True
            n = -1

        elif c == ',' and not in_scope:
            if current:
                current = rewrite(current.strip()).strip()
                if has_kw or not found_first_kw:
                    ret.append(current)
                else:
                    ret.append(fmt.format(n, current))

            n += 1
            current, has_kw = '', False
            continue

        current += c

    return '{}({})'.format(func, ', '.join(ret))

assert rewrite('f()') == 'f()'
assert rewrite('f1()') == 'f1()'
assert rewrite('fun32()') == 'fun32()'
assert rewrite('f ()') == 'f()'
assert rewrite('f(x)') == 'f(x)'
assert rewrite('f(len(s))') == 'f(len(s))'
assert rewrite('f(k=1)') == 'f(k=1)'
assert rewrite('f(k=")")') == 'f(k=")")'
assert rewrite('f(k=(1, 2, 3))') == 'f(k=(1, 2, 3))'
assert rewrite('f(k=1, y)') == 'f(k=1, _kw_0=y)'
assert rewrite('f(1, k=1, y)') == 'f(1, k=1, _kw_0=y)'
assert rewrite('f(g(k=1, y))') == 'f(g(k=1, _kw_0=y))'
assert rewrite('w = f(k=1, y)') == 'w = f(k=1, _kw_0=y)'
assert rewrite('with f(k=1, y) as fp') == 'with f(k=1, _kw_0=y) as fp'
assert rewrite('with f(k=1, y) as fp\n    w = f(k=1, y)') == 'with f(k=1, _kw_0=y) as fp\n    w = f(k=1, _kw_0=y)'
