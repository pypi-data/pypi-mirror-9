# -*- coding: utf-8 -*-
'''
Test some small, simple MARC snippets.

Requires http://pytest.org/ e.g.:

pip install pytest

Each test case is a triple of e.g. [SNIPPET_1, CONFIG_1, EXPECTED_1]

You must have matched series each with all 3 components matched up, otherwise the entire test suite will fall over like a stack of dominoes

----

Recipe for regenerating the test case expected outputs:

python -i test/test_marc_snippets.py #Ignore the SystemExit

Then:

all_snippets = sorted([ sym for sym in globals() if sym.startswith('SNIPPET') ])
all_config = sorted([ sym for sym in globals() if sym.startswith('CONFIG') ])
all_expected = sorted([ sym for sym in globals() if sym.startswith('EXPECTED') ])

for s, c, e in zip(all_snippets, all_config, all_expected):
    sobj, cobj, eobj = globals()[s], globals()[c], globals()[e]
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(None)
    m = memory.connection()
    instream = BytesIO(sobj.encode('utf-8'))
    outstream = StringIO()
    bfconvert(instream, model=m, out=outstream, config=cobj, canonical=True, loop=loop)
    print('EXPECTED from {0}:'.format(s))
    print(outstream.getvalue()) #This output becomes the EXPECTED stanza

'''

import sys
import logging
import asyncio
import difflib
from io import StringIO, BytesIO

from versa.driver import memory
from versa.util import jsondump, jsonload

from bibframe.reader.marcxml import bfconvert
import bibframe.plugin

import pytest

#Bits from http://www.loc.gov/standards/marcxml/Sandburg/sandburg.xml

#Leader + 008 + 1 control
SNIPPET_1 = '''<collection xmlns="http://www.loc.gov/MARC21/slim">
<record>
  <leader>01142cam 2200301 a 4500</leader>
  <controlfield tag="001">92005291</controlfield>
  <controlfield tag="008">920219s1993 caua j 000 0 eng</controlfield>
</record>
</collection>'''

CONFIG_1 = None

EXPECTED_1 = '''
[
    [
        "PZ-aV_fa",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "PZ-aV_fa",
        "http://bibfra.me/vocab/lite/controlCode",
        "92005291",
        {}
    ],
    [
        "PZ-aV_fa",
        "http://bibfra.me/vocab/lite/instantiates",
        "kP2G4QhW",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/Books",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/LanguageMaterial",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "encyclopedias",
        {}
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "legal articles",
        {}
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "surveys of literature",
        {}
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/vocab/marcext/tag-008",
        "920219s1993 caua j 000 0 eng",
        {}
    ]
]
'''

#Leader + 008 + 1 data
SNIPPET_2 = '''<collection xmlns="http://www.loc.gov/MARC21/slim">
<record>
  <leader>01142cam 2200301 a 4500</leader>
  <controlfield tag="008">920219s1993 caua j 000 0 eng</controlfield>
  <datafield tag="245" ind1="1" ind2="0">
    <subfield code="a">Arithmetic /</subfield>
    <subfield code="c">Carl Sandburg ; illustrated as an anamorphic adventure by Ted Rand.</subfield>
  </datafield>
</record>
</collection>'''

CONFIG_2 = None

EXPECTED_2 = '''
[
    [
        "uod_ls3S",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "uod_ls3S",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/Books",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "uod_ls3S",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/LanguageMaterial",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "uod_ls3S",
        "http://bibfra.me/vocab/lite/title",
        "Arithmetic /",
        {}
    ],
    [
        "uod_ls3S",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "encyclopedias",
        {}
    ],
    [
        "uod_ls3S",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "legal articles",
        {}
    ],
    [
        "uod_ls3S",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "surveys of literature",
        {}
    ],
    [
        "uod_ls3S",
        "http://bibfra.me/vocab/marc/titleStatement",
        "Carl Sandburg ; illustrated as an anamorphic adventure by Ted Rand.",
        {}
    ],
    [
        "uod_ls3S",
        "http://bibfra.me/vocab/marcext/tag-008",
        "920219s1993 caua j 000 0 eng",
        {}
    ],
    [
        "uqMAKS-3",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "uqMAKS-3",
        "http://bibfra.me/vocab/lite/instantiates",
        "uod_ls3S",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "uqMAKS-3",
        "http://bibfra.me/vocab/lite/title",
        "Arithmetic /",
        {}
    ],
    [
        "uqMAKS-3",
        "http://bibfra.me/vocab/marc/titleStatement",
        "Carl Sandburg ; illustrated as an anamorphic adventure by Ted Rand.",
        {}
    ]
]
'''

#Leader + 008 + 1 control + 1 data field
SNIPPET_3 = '''<collection xmlns="http://www.loc.gov/MARC21/slim">
<record>
  <leader>01142cam 2200301 a 4500</leader>
  <controlfield tag="001">92005291</controlfield>
  <controlfield tag="008">920219s1993 caua j 000 0 eng</controlfield>
  <datafield tag="245" ind1="1" ind2="0">
    <subfield code="a">Arithmetic /</subfield>
    <subfield code="c">Carl Sandburg ; illustrated as an anamorphic adventure by Ted Rand.</subfield>
  </datafield>
</record>
</collection>'''

CONFIG_3 = None

EXPECTED_3 = '''
[
    [
        "uod_ls3S",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "uod_ls3S",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/Books",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "uod_ls3S",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/LanguageMaterial",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "uod_ls3S",
        "http://bibfra.me/vocab/lite/title",
        "Arithmetic /",
        {}
    ],
    [
        "uod_ls3S",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "encyclopedias",
        {}
    ],
    [
        "uod_ls3S",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "legal articles",
        {}
    ],
    [
        "uod_ls3S",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "surveys of literature",
        {}
    ],
    [
        "uod_ls3S",
        "http://bibfra.me/vocab/marc/titleStatement",
        "Carl Sandburg ; illustrated as an anamorphic adventure by Ted Rand.",
        {}
    ],
    [
        "uod_ls3S",
        "http://bibfra.me/vocab/marcext/tag-008",
        "920219s1993 caua j 000 0 eng",
        {}
    ],
    [
        "uqMAKS-3",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "uqMAKS-3",
        "http://bibfra.me/vocab/lite/controlCode",
        "92005291",
        {}
    ],
    [
        "uqMAKS-3",
        "http://bibfra.me/vocab/lite/instantiates",
        "uod_ls3S",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "uqMAKS-3",
        "http://bibfra.me/vocab/lite/title",
        "Arithmetic /",
        {}
    ],
    [
        "uqMAKS-3",
        "http://bibfra.me/vocab/marc/titleStatement",
        "Carl Sandburg ; illustrated as an anamorphic adventure by Ted Rand.",
        {}
    ]
]
'''

SNIPPET_4 = SNIPPET_1

CONFIG_4 = {
    "plugins": [
        {"id": "http://bibfra.me/tool/pybibframe#labelizer",
                "lookup": {
                    "http://bibfra.me/vocab/lite/Work": "http://bibfra.me/vocab/lite/title",
                    "http://bibfra.me/vocab/lite/Instance": "http://bibfra.me/vocab/lite/title",
                    "http://bibfra.me/vocab/lite/Agent": "http://bibfra.me/vocab/lite/name",
                    "http://bibfra.me/vocab/lite/Person": "http://bibfra.me/vocab/lite/name",
                    "http://bibfra.me/vocab/lite/Organization": "http://bibfra.me/vocab/lite/name",
                    "http://bibfra.me/vocab/lite/Place": "http://bibfra.me/vocab/lite/name",
                    "http://bibfra.me/vocab/lite/Collection": "http://bibfra.me/vocab/lite/name",
                    "http://bibfra.me/vocab/lite/Meeting": "http://bibfra.me/vocab/lite/name",
                    "http://bibfra.me/vocab/lite/Topic": "http://bibfra.me/vocab/lite/name",
                    "http://bibfra.me/vocab/lite/Genre": "http://bibfra.me/vocab/lite/name"}
                }
    ]
}

EXPECTED_4 = '''
[
    [
        "PZ-aV_fa",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "PZ-aV_fa",
        "http://bibfra.me/vocab/lite/controlCode",
        "92005291",
        {}
    ],
    [
        "PZ-aV_fa",
        "http://bibfra.me/vocab/lite/instantiates",
        "kP2G4QhW",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "PZ-aV_fa",
        "http://www.w3.org/2000/01/rdf-schema#label",
        "",
        {}
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/Books",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/LanguageMaterial",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "encyclopedias",
        {}
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "legal articles",
        {}
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "surveys of literature",
        {}
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/vocab/marcext/tag-008",
        "920219s1993 caua j 000 0 eng",
        {}
    ],
    [
        "kP2G4QhW",
        "http://www.w3.org/2000/01/rdf-schema#label",
        "",
        {}
    ]
]
'''

SNIPPET_5 = '''<record xmlns="http://www.loc.gov/MARC21/slim">
<leader>02915cam a2200601 a 4500</leader>
<controlfield tag="008">020613s1860 ja a 000 0 jpn</controlfield>
<datafield tag="245" ind1="1" ind2="0">
  <subfield code="6">880-02</subfield>
  <subfield code="a">Ishinpō /</subfield>
  <subfield code="c">Tanba no Sukune Yasuyori sen.</subfield>
</datafield>
<datafield tag="880" ind1="1" ind2="0">
  <subfield code="6">245-02/$1</subfield>
  <subfield code="a">醫心方 /</subfield>
  <subfield code="c">丹波宿袮康頼撰.</subfield>
</datafield>
</record>
'''

CONFIG_5 = None

EXPECTED_5 = '''
[
    [
        "GoXwXAgG",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "GoXwXAgG",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/Books",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "GoXwXAgG",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/LanguageMaterial",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "GoXwXAgG",
        "http://bibfra.me/vocab/lite/title",
        "Ishinp\u014d /",
        {}
    ],
    [
        "GoXwXAgG",
        "http://bibfra.me/vocab/lite/title",
        "\u91ab\u5fc3\u65b9 /",
        {}
    ],
    [
        "GoXwXAgG",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "programmed texts",
        {}
    ],
    [
        "GoXwXAgG",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "surveys of literature",
        {}
    ],
    [
        "GoXwXAgG",
        "http://bibfra.me/vocab/marc/titleStatement",
        "Tanba no Sukune Yasuyori sen.",
        {}
    ],
    [
        "GoXwXAgG",
        "http://bibfra.me/vocab/marc/titleStatement",
        "\u4e39\u6ce2\u5bbf\u88ae\u5eb7\u983c\u64b0.",
        {}
    ],
    [
        "GoXwXAgG",
        "http://bibfra.me/vocab/marcext/tag-008",
        "020613s1860 ja a 000 0 jpn",
        {}
    ],
    [
        "GoXwXAgG",
        "http://bibfra.me/vocab/marcext/tag-880-10-6",
        "245-02/$1",
        {}
    ],
    [
        "GoXwXAgG",
        "http://bibfra.me/vocab/marcext/tag-880-10-a",
        "\u91ab\u5fc3\u65b9 /",
        {}
    ],
    [
        "GoXwXAgG",
        "http://bibfra.me/vocab/marcext/tag-880-10-c",
        "\u4e39\u6ce2\u5bbf\u88ae\u5eb7\u983c\u64b0.",
        {}
    ],
    [
        "dF3pns7f",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "dF3pns7f",
        "http://bibfra.me/vocab/lite/instantiates",
        "GoXwXAgG",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "dF3pns7f",
        "http://bibfra.me/vocab/lite/title",
        "Ishinp\u014d /",
        {}
    ],
    [
        "dF3pns7f",
        "http://bibfra.me/vocab/lite/title",
        "\u91ab\u5fc3\u65b9 /",
        {}
    ],
    [
        "dF3pns7f",
        "http://bibfra.me/vocab/marc/titleStatement",
        "Tanba no Sukune Yasuyori sen.",
        {}
    ],
    [
        "dF3pns7f",
        "http://bibfra.me/vocab/marc/titleStatement",
        "\u4e39\u6ce2\u5bbf\u88ae\u5eb7\u983c\u64b0.",
        {}
    ]
]
'''

#Test the uncombined version of the character after testing the combined one
#Another useful test would be using e.g. '\u2166', which is NFKC normalized to 3 separate characters VII
SNIPPET_6 = SNIPPET_5.replace('ō', 'ō')

CONFIG_6 = None

EXPECTED_6 = EXPECTED_5

SNIPPET_7 = '''<collection xmlns="http://www.loc.gov/MARC21/slim">
<record>
  <leader>01142cam 2200301 a 4500</leader>
  <controlfield tag="008">920219s1993 caua j 000 0 eng</controlfield>
  <datafield tag="100" ind1="1" ind2=" ">
    <subfield code="a">Sandburg, Carl,</subfield>
    <subfield code="d">1878-1967.</subfield>
  </datafield>
  </record>
</collection>'''

CONFIG_7 = None

EXPECTED_7 = '''
[
    [
        "Ht2FQsIY",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "Ht2FQsIY",
        "http://bibfra.me/vocab/lite/instantiates",
        "XsrrgYIS",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "Uer3F4eM",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Person",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "Uer3F4eM",
        "http://bibfra.me/vocab/lite/date",
        "1878-1967.",
        {}
    ],
    [
        "Uer3F4eM",
        "http://bibfra.me/vocab/lite/name",
        "Sandburg, Carl,",
        {}
    ],
    [
        "Uer3F4eM",
        "http://bibfra.me/vocab/marcext/sf-a",
        "Sandburg, Carl,",
        {}
    ],
    [
        "Uer3F4eM",
        "http://bibfra.me/vocab/marcext/sf-d",
        "1878-1967.",
        {}
    ],
    [
        "XsrrgYIS",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "XsrrgYIS",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/Books",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "XsrrgYIS",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/LanguageMaterial",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "XsrrgYIS",
        "http://bibfra.me/vocab/lite/creator",
        "Uer3F4eM",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "XsrrgYIS",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "encyclopedias",
        {}
    ],
    [
        "XsrrgYIS",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "legal articles",
        {}
    ],
    [
        "XsrrgYIS",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "surveys of literature",
        {}
    ],
    [
        "XsrrgYIS",
        "http://bibfra.me/vocab/marcext/tag-008",
        "920219s1993 caua j 000 0 eng",
        {}
    ]
]
'''

SNIPPET_8 = '''<collection xmlns="http://www.loc.gov/MARC21/slim">
<record>
  <leader>02415cas a2200637 a 4500</leader>
  <controlfield tag="008">010806c20019999ru br p       0   a0eng d</controlfield>
  <datafield tag="780" ind1="1" ind2="4">
    <subfield code="t">Doklady biochemistry</subfield>
    <subfield code="x">0012-4958</subfield>
    <subfield code="w">(DLC)   96646621</subfield>
    <subfield code="w">(OCoLC)1478787</subfield>
    <subfield code="w">(DNLM)7505458</subfield>
  </datafield>
  </record>
</collection>'''

CONFIG_8 = None

EXPECTED_8 = '''
[
    [
        "IoGxK0TV",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "IoGxK0TV",
        "http://bibfra.me/vocab/lite/authorityLink",
        "http://lccn.loc.gov/96646621",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "IoGxK0TV",
        "http://bibfra.me/vocab/lite/authorityLink",
        "http://www.ncbi.nlm.nih.gov/nlmcatalog?term=7505458",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "IoGxK0TV",
        "http://bibfra.me/vocab/lite/authorityLink",
        "http://www.worldcat.org/oclc/1478787",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "IoGxK0TV",
        "http://bibfra.me/vocab/lite/title",
        "Doklady biochemistry",
        {}
    ],
    [
        "IoGxK0TV",
        "http://bibfra.me/vocab/marc/issn",
        "0012-4958",
        {}
    ],
    [
        "IoGxK0TV",
        "http://bibfra.me/vocab/marcext/sf-t",
        "Doklady biochemistry",
        {}
    ],
    [
        "IoGxK0TV",
        "http://bibfra.me/vocab/marcext/sf-w",
        "(DLC)   96646621",
        {}
    ],
    [
        "IoGxK0TV",
        "http://bibfra.me/vocab/marcext/sf-w",
        "(DNLM)7505458",
        {}
    ],
    [
        "IoGxK0TV",
        "http://bibfra.me/vocab/marcext/sf-w",
        "(OCoLC)1478787",
        {}
    ],
    [
        "IoGxK0TV",
        "http://bibfra.me/vocab/marcext/sf-x",
        "0012-4958",
        {}
    ],
    [
        "PZ-aV_fa",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "PZ-aV_fa",
        "http://bibfra.me/vocab/lite/instantiates",
        "kP2G4QhW",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/Collection",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/ContinuingResources",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/LanguageMaterial",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/vocab/marc/characteristic",
        "periodical",
        {}
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/vocab/marc/entryConvention",
        "successive entry",
        {}
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/vocab/marc/frequency",
        "bimonthly",
        {}
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/vocab/marc/originalAlphabetOrScriptOfTitle",
        "basic roman",
        {}
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/vocab/marc/regularity",
        "regular",
        {}
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/vocab/marcext/tag-008",
        "010806c20019999ru br p       0   a0eng d",
        {}
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/vocab/relation/unionOf",
        "IoGxK0TV",
        {
            "@target-type": "@iri-ref"
        }
    ]
]
'''

#Leader + 008 + 1 data
SNIPPET_9 = '''<collection xmlns="http://www.loc.gov/MARC21/slim">
<record>
  <leader>01025cas a22003251  4500</leader>
  <controlfield tag="008">821218d18821919ja uu p       0||||0jpn b</controlfield>
  <datafield tag="260" ind1=" " ind2=" ">
      <subfield code="a">Tokyo.</subfield>
  </datafield>
</record>
</collection>'''

CONFIG_9 = None

EXPECTED_9 = '''
[
    [
        "PZ-aV_fa",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "PZ-aV_fa",
        "http://bibfra.me/vocab/lite/instantiates",
        "kP2G4QhW",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "PZ-aV_fa",
        "http://bibfra.me/vocab/marc/publication",
        "_Pdjp3p_",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "ZFkTPkl8",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Place",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "ZFkTPkl8",
        "http://bibfra.me/vocab/lite/name",
        "Tokyo.",
        {}
    ],
    [
        "ZFkTPkl8",
        "http://bibfra.me/vocab/marcext/sf-a",
        "Tokyo.",
        {}
    ],
    [
        "_Pdjp3p_",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/ProviderEvent",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "_Pdjp3p_",
        "http://bibfra.me/vocab/lite/providerPlace",
        "ZFkTPkl8",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "_Pdjp3p_",
        "http://bibfra.me/vocab/marcext/sf-a",
        "Tokyo.",
        {}
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/Collection",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/ContinuingResources",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/LanguageMaterial",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/vocab/marc/characteristic",
        "periodical",
        {}
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/vocab/marc/entryConvention",
        "successive entry",
        {}
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/vocab/marc/frequency",
        "unknown frequency",
        {}
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/vocab/marc/regularity",
        "unknown",
        {}
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/vocab/marcext/tag-008",
        "821218d18821919ja uu p       0||||0jpn b",
        {}
    ]
]
'''

SNIPPET_10 = '''<collection xmlns="http://www.loc.gov/MARC21/slim">
<record>
  <leader>02386cas a2200637 a 4500</leader>
  <controlfield tag="001">37263290</controlfield>
  <controlfield tag="003">OCoLC</controlfield>
  <controlfield tag="005">20141208144405.0</controlfield>
  <controlfield tag="006">m     o  d f      </controlfield>
  <controlfield tag="007">cr gn|||||||||</controlfield>
  <controlfield tag="008">970709c19679999dcugr   o hr f0   a0eng  </controlfield>
</record></collection>
'''

CONFIG_10 = {}

EXPECTED_10 = '''
[
    [
        "PZ-aV_fa",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "PZ-aV_fa",
        "http://bibfra.me/vocab/lite/controlCode",
        "37263290",
        {}
    ],
    [
        "PZ-aV_fa",
        "http://bibfra.me/vocab/lite/instantiates",
        "kP2G4QhW",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "PZ-aV_fa",
        "http://bibfra.me/vocab/marc/formOfItem",
        "online",
        {}
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/Collection",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/ContinuingResources",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/LanguageMaterial",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/vocab/marc/entryConvention",
        "successive entry",
        {}
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/vocab/marc/frequency",
        "biennial",
        {}
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/vocab/marc/frequency",
        "monthly",
        {}
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/vocab/marc/governmentPublication",
        "federal national government publication",
        {}
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "dictionaries",
        {}
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/vocab/marc/natureOfContents",
        "directories",
        {}
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/vocab/marc/natureOfEntireWork",
        "reviews",
        {}
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/vocab/marc/originalAlphabetOrScriptOfTitle",
        "basic roman",
        {}
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/vocab/marc/regularity",
        "regular",
        {}
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/vocab/marcext/tag-003",
        "OCoLC",
        {}
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/vocab/marcext/tag-005",
        "20141208144405.0",
        {}
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/vocab/marcext/tag-006",
        "m     o  d f      ",
        {}
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/vocab/marcext/tag-007",
        "cr gn|||||||||",
        {}
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/vocab/marcext/tag-008",
        "970709c19679999dcugr   o hr f0   a0eng  ",
        {}
    ]
]
'''

# a couple degenerate cases
SNIPPET_11 = '''
<collection xmlns="http://www.loc.gov/MARC21/slim">
<record xmlns="http://www.loc.gov/MARC21/slim"><leader>00000ngm a2200000Ka 4500</leader><controlfield tag="001">881466</controlfield></record>
</collection>
'''

CONFIG_11 = {}

EXPECTED_11 = '''
[
    [
        "PZ-aV_fa",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "PZ-aV_fa",
        "http://bibfra.me/vocab/lite/controlCode",
        "881466",
        {}
    ],
    [
        "PZ-aV_fa",
        "http://bibfra.me/vocab/lite/instantiates",
        "kP2G4QhW",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/marc/MovingImage",
        {
            "@target-type": "@iri-ref"
        }
    ]
]
'''

SNIPPET_12 = '''
<collection xmlns="http://www.loc.gov/MARC21/slim">
<record xmlns="http://www.loc.gov/MARC21/slim"><controlfield tag="001">881466</controlfield></record>
</collection>
'''

CONFIG_12 = {}

EXPECTED_12 = '''
[
    [
        "PZ-aV_fa",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Instance",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "PZ-aV_fa",
        "http://bibfra.me/vocab/lite/controlCode",
        "881466",
        {}
    ],
    [
        "PZ-aV_fa",
        "http://bibfra.me/vocab/lite/instantiates",
        "kP2G4QhW",
        {
            "@target-type": "@iri-ref"
        }
    ],
    [
        "kP2G4QhW",
        "http://bibfra.me/purl/versa/type",
        "http://bibfra.me/vocab/lite/Work",
        {
            "@target-type": "@iri-ref"
        }
    ]
]'''

all_snippets = sorted([ sym for sym in globals() if sym.startswith('SNIPPET') ])
all_config = sorted([ sym for sym in globals() if sym.startswith('CONFIG') ])
all_expected = sorted([ sym for sym in globals() if sym.startswith('EXPECTED') ])

all_snippets = [ (sym, globals()[sym]) for sym in all_snippets ]
all_config = [ (sym, globals()[sym]) for sym in all_config ]
all_expected = [ (sym, globals()[sym]) for sym in all_expected ]

def file_diff(s_orig, s_new):
    diff = difflib.unified_diff(s_orig.split('\n'), s_new.split('\n'))
    return '\n'.join(list(diff))


def run_one(snippet, expected, desc, entbase=None, config=None, loop=None, canonical=True):
    m = memory.connection()
    m_expected = memory.connection()
    instream = BytesIO(snippet.encode('utf-8'))
    outstream = StringIO()
    bfconvert(instream, model=m, out=outstream, config=config, canonical=canonical, loop=loop)
    outstream.seek(0)
    jsonload(m, outstream)

    expected_stream = StringIO(expected)
    jsonload(m_expected, expected_stream)

    assert m == m_expected, "Discrepancies found ({0}):\n{1}".format(desc, file_diff(repr(m_expected), repr(m)))


@pytest.mark.parametrize('snippet, config, expected', zip(all_snippets, all_config, all_expected))
def test_snippets(snippet, config, expected):
    #Use a new event loop per test instance, and so one call of bfconvert per test
    desc = '|'.join([ t[0] for t in (snippet, config, expected) ])
    snippet, config, expected = [ t[1] for t in (snippet, config, expected) ]
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(None)

    run_one(snippet, expected, desc, config=config, loop=loop)


if __name__ == '__main__':
    raise SystemExit("use py.test")

