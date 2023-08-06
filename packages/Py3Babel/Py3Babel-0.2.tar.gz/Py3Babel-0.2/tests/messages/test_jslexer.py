# -*- coding: utf-8 -*-

from py3babel.messages import jslexer


def test_unquote():
    assert jslexer.unquote_string('""') == ''
    assert jslexer.unquote_string(r'"h\u00ebllo"') == u"hëllo"
