# -*- coding: utf-8 -*-
import re

from wng.pattern import parse_term, parse_name_and_terms, \
    parse_groups


class TestPattern(object):
    def test_parse_term(self):
        # Simple strings: tag, word, both
        t = parse_term("FOO")
        assert re.match(t, "bar\tFOO\n")
        t = parse_term("{bar}")
        assert re.match(t, "bar\tFOO\n")
        t = parse_term("FOO{bar}")
        assert re.match(t, "bar\tFOO\n")
        # Regex dots
        t = parse_term("F.O")
        assert re.match(t, "bar\tFOO\n")
        t = parse_term("{b.r}")
        assert re.match(t, "bar\tFOO\n")
        t = parse_term("F.O{b.r}")
        assert re.match(t, "bar\tFOO\n")
        # Regex plus
        t = parse_term("FO+")
        assert re.match(t, "bar\tFOO\n")
        t = parse_term("{ba+}")
        assert re.match(t, "baa\tFOO\n")
        t = parse_term("FO+{ba+}")
        assert re.match(t, "baa\tFOO\n")
        # Regex classes
        t = parse_term("F[OX]+")
        assert re.match(t, "bar\tFX\n")
        t = parse_term("{b[ar]}")
        assert re.match(t, "ba\tFOO\n")
        t = parse_term("F[OX]{b[ar]}")
        assert re.match(t, "br\tFX\n")
        # Regex options
        t = parse_term("FOO|BAR")
        assert re.match(t, "bar\tBAR\n")
        t = parse_term("{bar|foo}")
        assert re.match(t, "foo\tFOO\n")
        t = parse_term("FOO|BAR{bar|foo}")
        assert re.match(t, "foo\tBAR\n")
        # Question mark
        t = parse_term("FOO ?")
        assert re.match(t, "")
        t = parse_term("{bar} ?")
        assert re.match(t, "")
        t = parse_term("FOO{bar} ?")
        assert re.match(t, "")
        # Plus
        t = parse_term("FOO +")
        assert re.match(t, "bar\tFOO\nbar\tFOO\n")
        t = parse_term("{bar} +")
        assert re.match(t, "bar\tFOO\nbar\tFOO\n")
        t = parse_term("FOO{bar} +")
        assert re.match(t, "bar\tFOO\nbar\tFOO\n")
        # Star
        t = parse_term("FOO *")
        assert re.match(t, "bar\tFOO\nbar\tFOO\n")
        assert re.match(t, "")
        t = parse_term("{bar} *")
        assert re.match(t, "bar\tFOO\nbar\tFOO\n")
        assert re.match(t, "")
        t = parse_term("FOO{bar} *")
        assert re.match(t, "bar\tFOO\nbar\tFOO\n")
        assert re.match(t, "")
        # Named results
        t = parse_term("FOO as foo")
        m = re.match(t, "bar\tFOO\n")
        assert m
        assert m.group("foo_word") == "bar"
        assert m.group("foo_tag") == "FOO"

    def test_parse_name_and_terms(self):
        t = parse_name_and_terms("""foo:
FOO""")
        assert t[0] == "foo"
        assert re.match(t[1], "bar\tFOO\n")

    def test_parse_groups(self):
        t = parse_groups("""foo:
        FOO
        ==
        bar:
        {bar}""")
        assert len(t) == 2
        assert t[0][0] == "foo"
        assert re.match(t[0][1], "bar\tFOO\n")
        assert t[1][0] == "bar"
        assert re.match(t[1][1], "bar\tFOO\n")

    def test_example1(self):
        text = """I\tPRO
haue\tHVP
not\tNEG
,\t,
I\tPRO
did\tDOD
not\tNEG
desire\tVB
,\t,
nor\tCONJ
intend\tVB
to\tTO
declare\tVB
my\tPRO$
opinion\tN
in\tP
that\tD
point\tN
.\t."""
        pattern = parse_groups("""PRO as subject
ADV *
DOD|DOP
ADV *
NEG
ADV *
VB as verb""")[0][1]
        assert pattern.search(text)

    def test_example2(self):
        text = """I\tPRO
know\tVBP
not\tNEG
only\tADV
Bob\tNPR
but\tCONJ
also\tADV
Jim\tNPR"""
        pattern = parse_groups("""PRO as subject
ADV *
VBP|VBD as verb
ADV|PRO *
NEG
{(?!only|onely).*} as foll1
.* as foll2""")[0][1]
        assert not pattern.search(text)
        text2 = """I\tPRO
know\tVBP
not\tNEG
Bob\tNPR
but\tCONJ
also\tADV
Jim\tNPR"""
        assert pattern.search(text2)

    # def test_parse_terms(self):
    #     t = parse_terms("FOO\nBAR")
    #     assert t.match("bar\tFOO\nbar\tBAR\n")
    #     t = parse_terms("{foo}\n{bar}")
    #     assert t.match("foo\tFOO\nbar\tBAR\n")
    #     t = parse_terms("FOO{foo}\nBAR{bar}")
    #     assert t.match("foo\tFOO\nbar\tBAR\n")
