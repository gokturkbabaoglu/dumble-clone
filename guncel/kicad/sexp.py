"""Küçük S-ifadesi okuyucu/yazıcı (KiCad dosyaları için)."""
import re

_tok = re.compile(r'\s*(?:(\()|(\))|("(?:[^"\\]|\\.)*")|([^\s()"]+))')


class Sym(str):
    """Tırnaksız atom (anahtar kelime / sayı)."""


def parse(text):
    pos, stack, cur = 0, [], []
    n = len(text)
    while pos < n:
        m = _tok.match(text, pos)
        if not m:
            if text[pos:].strip() == '':
                break
            raise ValueError('ayrıştırma hatası @%d' % pos)
        pos = m.end()
        o, c, s, a = m.groups()
        if o:
            stack.append(cur); cur = []
        elif c:
            done = cur; cur = stack.pop(); cur.append(done)
        elif s is not None:
            cur.append(s[1:-1].replace('\\"', '"').replace('\\\\', '\\'))
        elif a is not None:
            cur.append(Sym(a))
    return cur[0]


def q(s):
    return '"' + str(s).replace('\\', '\\\\').replace('"', '\\"') + '"'


def dump(e, ind=0):
    if isinstance(e, list):
        if not e:
            return '()'
        simple = all(not isinstance(x, list) for x in e)
        if simple:
            return '(' + ' '.join(dump(x) for x in e) + ')'
        out = '(' + ' '.join(dump(x) for x in e if not isinstance(x, list))
        # baştaki atomlardan sonra alt listeler
        first_list = next(i for i, x in enumerate(e) if isinstance(x, list))
        out = '(' + ' '.join(dump(x) for x in e[:first_list])
        for x in e[first_list:]:
            out += '\n' + '\t' * (ind + 1) + dump(x, ind + 1)
        return out + '\n' + '\t' * ind + ')'
    if isinstance(e, Sym):
        return str(e)
    return q(e)


def find(e, key):
    return [x for x in e if isinstance(x, list) and x and x[0] == key]


def first(e, key):
    r = find(e, key)
    return r[0] if r else None
