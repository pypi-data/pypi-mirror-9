#!/usr/bin/env python
# coding: utf-8

from __future__ import unicode_literals

from unicodedata import normalize

import pandas as pd
from pandas.compat import PY3, iteritems, u_safe, reduce
import pandas.core.common as com

import pandas.core.strings as strings


# requires special handling
_HSOUNDMARK = ['ｶﾞ', 'ｷﾞ', 'ｸﾞ', 'ｹﾞ', 'ｺﾞ',
               'ｻﾞ', 'ｼﾞ', 'ｽﾞ', 'ｾﾞ', 'ｿﾞ',
               'ﾀﾞ', 'ﾁﾞ', 'ﾂﾞ', 'ﾃﾞ', 'ﾄﾞ',
               'ﾊﾞ', 'ﾋﾞ', 'ﾌﾞ', 'ﾍﾞ', 'ﾎﾞ',
               'ﾊﾟ', 'ﾋﾟ', 'ﾌﾟ', 'ﾍﾟ', 'ﾎﾟ', 'ｳﾞ']

_HKANA = 'ｧｱｨｲｩｳｪｴｫｵｶｷｸｹｺｻｼｽｾｿﾀﾁｯﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓｬﾔｭﾕｮﾖﾗﾘﾙﾚﾛﾜｦﾝﾞｰ･｢｣｡､'
_ZALPHA = ('ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ'
           'ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ')
_ZSYMBOL = '！＂＃＄％＆＇（）＊＋，－．／：；＜＝＞？＠［＼］＾＿｀｛｜｝～　'
_ZDIGIT = '０１２３４５６７８９'

# mapping from full-width to half width
_KANA_MAPPER = {normalize('NFKC', c): c for c in _HKANA}
_ALPHA_MAPPER = {c: normalize('NFKC', c) for c in _ZALPHA}
_DIGIT_MAPPER = {c: normalize('NFKC', c) for c in _ZDIGIT}
_SYMBOL_MAPPER = {c: normalize('NFKC', c) for c in _ZSYMBOL}


def _reverse_dict(dict):
    return {v: k for k, v in iteritems(dict)}

def _ord_dict(dict):
    return {ord(k): v for k, v in iteritems(dict)}


# for unicode.translate
_Z2H_KANA = _ord_dict(_KANA_MAPPER)
_Z2H_ALPHA = _ord_dict(_ALPHA_MAPPER)
_Z2H_DIGIT = _ord_dict(_DIGIT_MAPPER)
_Z2H_SYMBOL = _ord_dict(_SYMBOL_MAPPER)
_H2Z_KANA = _ord_dict(_reverse_dict(_KANA_MAPPER))
_H2Z_ALPHA = _ord_dict(_reverse_dict(_ALPHA_MAPPER))
_H2Z_DIGIT = _ord_dict(_reverse_dict(_DIGIT_MAPPER))
_H2Z_SYMBOL = _ord_dict(_reverse_dict(_SYMBOL_MAPPER))


# for multiple replace
_Z2H_SOUNDMARK = {normalize('NFKC', c): c for c in _HSOUNDMARK}
_H2Z_SOUNDMARK = _reverse_dict(_Z2H_SOUNDMARK)


def _h2z_sm(text):
    return (text.replace("ｶﾞ", "ガ").replace("ｷﾞ", "ギ").replace("ｸﾞ", "グ").replace("ｹﾞ", "ゲ").
            replace("ｺﾞ", "ゴ").replace("ｻﾞ", "ザ").replace("ｼﾞ", "ジ").replace("ｽﾞ", "ズ").
            replace("ｾﾞ", "ゼ").replace("ｿﾞ", "ゾ").replace("ﾀﾞ", "ダ").replace("ﾁﾞ", "ヂ").
            replace("ﾂﾞ", "ヅ").replace("ﾃﾞ", "デ").replace("ﾄﾞ", "ド").replace("ﾊﾞ", "バ").
            replace("ﾋﾞ", "ビ").replace("ﾌﾞ", "ブ").replace("ﾍﾞ", "ベ").replace("ﾎﾞ", "ボ").
            replace("ﾊﾟ", "パ").replace("ﾋﾟ", "ピ").replace("ﾌﾟ", "プ").replace("ﾍﾟ", "ペ").
            replace("ﾎﾟ", "ポ").replace("ｳﾞ", "ヴ"))

    # for k, v in iteritems(_H2Z_SOUNDMARK):
    #     text = text.replace(k, v)
    # return text

    # return reduce(lambda t, kv: t.replace(*kv),
    #               iteritems(_H2Z_SOUNDMARK), text)

def _z2h_sm(text):
    return (text.replace("ガ", "ｶﾞ").replace("ギ", "ｷﾞ").replace("グ", "ｸﾞ").replace("ゲ", "ｹﾞ").
            replace("ゴ", "ｺﾞ").replace("ザ", "ｻﾞ").replace("ジ", "ｼﾞ").replace("ズ", "ｽﾞ").
            replace("ゼ", "ｾﾞ").replace("ゾ", "ｿﾞ").replace("ダ", "ﾀﾞ").replace("ヂ", "ﾁﾞ").
            replace("ヅ", "ﾂﾞ").replace("デ", "ﾃﾞ").replace("ド", "ﾄﾞ").replace("バ", "ﾊﾞ").
            replace("ビ", "ﾋﾞ").replace("ブ", "ﾌﾞ").replace("ベ", "ﾍﾞ").replace("ボ", "ﾎﾞ").
            replace("パ", "ﾊﾟ").replace("ピ", "ﾋﾟ").replace("プ", "ﾌﾟ").replace("ペ", "ﾍﾟ").
            replace("ポ", "ﾎﾟ").replace("ヴ", "ｳﾞ"))


def str_z2h(self, kana=True, alpha=True, digit=True, symbol=True):
    mapper = dict()
    if kana:
        mapper.update(_Z2H_KANA)
    if alpha:
        mapper.update(_Z2H_ALPHA)
    if digit:
        mapper.update(_Z2H_DIGIT)
    if symbol:
        mapper.update(_Z2H_SYMBOL)

    if kana:
        if PY3:
            f = lambda x: _z2h_sm(x).translate(mapper)
        else:
            f = lambda x: _z2h_sm(u_safe(x)).translate(mapper)
    else:
        if PY3:
            f = lambda x: x.translate(mapper)
        else:
            f = lambda x: u_safe(x).translate(mapper)
    return self._wrap_result(strings._na_map(f, self.series))


def str_h2z(self, kana=True, alpha=True, digit=True, symbol=True):
    mapper = dict()
    if kana:
        mapper.update(_H2Z_KANA)
    if alpha:
        mapper.update(_H2Z_ALPHA)
    if digit:
        mapper.update(_H2Z_DIGIT)
    if symbol:
        mapper.update(_H2Z_SYMBOL)

    if kana:
        if PY3:
            f = lambda x: _h2z_sm(x).translate(mapper)
        else:
            f = lambda x: _h2z_sm(u_safe(x)).translate(mapper)
    else:
        if PY3:
            f = lambda x: x.translate(mapper)
        else:
            f = lambda x: u_safe(x).translate(mapper)
    return self._wrap_result(strings._na_map(f, self.series))


def str_normalize(self, form='NFKC'):
    if PY3:
        f = lambda x: normalize(form, x)
    else:
        f = lambda x: normalize(form, u_safe(x))
    return self._wrap_result(strings._na_map(f, self.series))


# do not overwrite existing func
if not hasattr(strings.StringMethods, 'normalize'):
    strings.StringMethods.normalize = str_normalize


if not hasattr(strings.StringMethods, 'z2h'):
    strings.StringMethods.z2h = str_z2h


if not hasattr(strings.StringMethods, 'h2z'):
    strings.StringMethods.h2z = str_h2z
