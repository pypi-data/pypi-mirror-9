#!/usr/bin/env python
#coding:utf-8
def cap_split(phrase, li=[]):
    #把一个字符串根据单词split
    #print cap_split('FuckMyAssHole')
    #>>['Fuck', 'My', 'Ass', 'Hole']
    def find_next_upper(s, start):
        for n, i in enumerate(s[start:]):
            if i.upper() == i:
                return n + start
    for n, i in enumerate(phrase):
        if i.upper() == i:
            next_loc = find_next_upper(phrase, n+1)
            if next_loc:
                li.append(phrase[:next_loc])
                return cap_split(phrase[next_loc:], li)
            else:
                li.append(phrase)
                return li

def txt_rstrip(txt):
    if type(txt) is unicode:
        txt = txt.encode('utf-8', "ignore")
    return '\n'.join(
        map(
            str.rstrip,
            txt.replace('\r\n', '\n')
               .replace('\r', '\n').rstrip('\n ')
               .split('\n')
        )
    )


def make_tag_list(tag_txt):
    _tag_list = txt_rstrip(tag_txt).split('\n')
    result = []
    for i in _tag_list:
        tag = i.strip()
        if not tag:
            continue
        if tag not in result:
            result.append(tag)
    return result

def to_s(s):
    if isinstance(s, unicode):
        return s.encode("utf-8")
    elif isinstance(s, list):
        return "[%s]" % ", ".join(map(to_s, s))
    elif isinstance(s, dict):
        result = {}
        for k,v in s.iteritems():
            result[to_s(k)] = to_s(v)
        return '{%s}' % ',\n'.join("'%s': '%s'" % pair for pair in result.iteritems())
    elif isinstance(s, (int, long, float, complex)):
        return str(s)
    else:
        return s

if __name__ == "__main__":
    print cap_split('FuckMyAssHole')
    pass
    print make_tag_list('sss wefwegf wegweg')
