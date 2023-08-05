__author__ = 'maik'


# Copyright (C) 2013 Angel Yanguas-Gil
# This program is free software, licensed under GPLv2 or later.
# A copy of the GPLv2 license is provided in the root directory of
# the source code.

"""Parse WOK and Refman's RIS files"""

import re
import types

woktag = "^[A-Z][A-Z0-9] |^ER$|^EF$"
ristag = "^[A-Z][A-Z0-9]  - "
riscounter = "^[0-9]+."

wokpat = re.compile(woktag)
rispat = re.compile(ristag)
riscounterpat = re.compile(riscounter)

ris_boundtags = ('TY', 'ER')
wok_boundtags = ('PT', 'ER')

wok_ignoretags = ['FN', 'VR', 'EF']
ris_ignoretags = []

LIST_TYPE_KEYS = [
    'A1',
    'A2',
    'A3',
    'A4',
    'AU',
    'KW',
]

TAG_KEY_MAPPING = {
    'TY': "type_of_reference",
    'A1': "first_authors", #ListType
    'A2': "secondary_authors", #ListType
    'A3': "tertiary_authors", #ListType
    'A4': "subsidiary_authors", #ListType
    'AB': "abstract",
    'AD': "author_address",
    'AN': "accession_number",
    'AU': "authors", #ListType
    'C1': "custom1",
    'C2': "custom2",
    'C3': "custom3",
    'C4': "custom4",
    'C5': "custom5",
    'C6': "custom6",
    'C7': "custom7",
    'C8': "custom8",
    'CA': "caption",
    'CN': "call_number",
    'CY': "place_published",
    'DA': "date",
    'DB': "name_of_database",
    'DO': "doi",
    'DP': "database_provider",
    'ET': "edition",
    'EP': "end_page",
    'ID': "id",
    'IS': "number",
    'J2': "alternate_title1",
    'JA': "alternate_title2",
    'JF': "alternate_title3",
    'KW': "keywords", #ListType
    'L1': "file_attachments1",
    'L2': "file_attachments2",
    'L4': "figure",
    'LA': "language",
    'LB': "label",
    'M1': "note",
    'M3': "type_of_work",
    'N1': "notes",
    'N2': "abstract",
    'NV': "number_of_Volumes",
    'OP': "original_publication",
    'PB': "publisher",
    'PY': "year",
    'RI': "reviewed_item",
    'RN': "research_notes",
    'RP': "reprint_edition",
    'SE': "version",
    'SN': "issn",
    'SP': "start_page",
    'ST': "short_title",
    'T1': "primary_title",
    'T2': "secondary_title",
    'T3': "tertiary_title",
    'TA': "translated_author",
    'TI': "title",
    'TT': "translated_title",
    'UR': "url",
    'VL': "volume",
    'Y1': "publication_year",
    'Y2': "access_date",
    'ER': "end_of_reference"
}

TYPE_OF_REFERENCE_MAPPING = {
    'ABST': 'Abstract',
    'ADVS': 'Audiovisual material',
    'AGGR': 'Aggregated Database',
    'ANCIENT': 'Ancient Text',
    'ART': 'Art Work',
    'BILL': 'Bill',
    'BLOG': 'Blog',
    'BOOK': 'Whole book',
    'CASE': 'Case',
    'CHAP': 'Book chapter',
    'CHART': 'Chart',
    'CLSWK': 'Classical Work',
    'COMP': 'Computer program',
    'CONF': 'Conference proceeding',
    'CPAPER': 'Conference paper',
    'CTLG': 'Catalog',
    'DATA': 'Data file',
    'DBASE': 'Online Database',
    'DICT': 'Dictionary',
    'EBOOK': 'Electronic Book',
    'ECHAP': 'Electronic Book Section',
    'EDBOOK': 'Edited Book',
    'EJOUR': 'Electronic Article',
    'ELEC': 'Web Page',
    'ENCYC': 'Encyclopedia',
    'EQUA': 'Equation',
    'FIGURE': 'Figure',
    'GEN': 'Generic',
    'GOVDOC': 'Government Document',
    'GRANT': 'Grant',
    'HEAR': 'Hearing',
    'ICOMM': 'Internet Communication',
    'INPR': 'In Press',
    'JFULL': 'Journal (full)',
    'JOUR': 'Journal',
    'LEGAL': 'Legal Rule or Regulation',
    'MANSCPT': 'Manuscript',
    'MAP': 'Map',
    'MGZN': 'Magazine article',
    'MPCT': 'Motion picture',
    'MULTI': 'Online Multimedia',
    'MUSIC': 'Music score',
    'NEWS': 'Newspaper',
    'PAMP': 'Pamphlet',
    'PAT': 'Patent',
    'PCOMM': 'Personal communication',
    'RPRT': 'Report',
    'SER': 'Serial publication',
    'SLIDE': 'Slide',
    'SOUND': 'Sound recording',
    'STAND': 'Standard',
    'STAT': 'Statute',
    'THES': 'Thesis/Dissertation',
    'UNPB': 'Unpublished work',
    'VIDEO': 'Video recording',
}

def readris(filename, mapping=None, wok=False):
    """Parse a ris file and return a list of entries.

    Entries are codified as dictionaries whose keys are the
    different tags. For single line and singly ocurring tags,
    the content is codified as a string. In the case of multiline
    or multiple key ocurrences, the content is returned as a list
    of strings.

    Keyword arguments:
    filename -- path of input ris file
    mapping -- custom RIS tags mapping
    wok -- flag, Web of Knowledge format is used if True, otherwise
           Refman's RIS specifications are used.

    """
    ignored_lines = []

    if not mapping:
        mapping = TAG_KEY_MAPPING

    if wok:
        gettag = lambda line: line[0:2]
        getcontent = lambda line: line[2:].strip()
        istag = lambda line: (wokpat.match(line) is not None)
        starttag, endtag = wok_boundtags
        ignoretags = wok_ignoretags
    else:
        gettag = lambda line: line[0:2]
        getcontent = lambda line: line[6:].strip()
        istag = lambda line: (rispat.match(line) is not None)
        iscounter = lambda line: (riscounterpat.match(line) is not None)
        starttag, endtag = ris_boundtags
        ignoretags = ris_ignoretags

    filelines = open(filename, 'r').readlines()
    # Corrects for BOM in utf-8 encodings while keeping an 8-bit
    # string representation
    st = filelines[0]
    if (st[0], st[1], st[2]) == ('\xef', '\xbb', '\xbf'):
        filelines[0] = st[3:]

    inref = False
    tag = None
    current = {}
    ln = 0

    for line in filelines:
        ln += 1
        if istag(line):
            tag = gettag(line)
            if tag in ignoretags:
                continue
            elif tag == endtag:
                # Close the active entry and yield it
                yield current
                current = {}
                inref = False
            elif tag == starttag:
                # New entry
                if inref:
                    text = "Missing end of record tag in line %d:\n %s" % (
                        ln, line)
                    raise IOError(text)
                current[mapping[tag]] = getcontent(line)
                inref = True
            else:
                if not inref:
                    text = "Invalid start tag in line %d:\n %s" % (ln, line)
                    raise IOError(text)
                if tag in LIST_TYPE_KEYS:
                    if mapping[tag] not in current:
                        current[mapping[tag]] = []
                    current[mapping[tag]].append(getcontent(line))
                elif mapping[tag] not in current:
                    current[mapping[tag]] = getcontent(line)
                else:
                    ignored_lines.append(line)

        else:
            if not line.strip():
                continue
            if inref:
                # Active reference
                if tag is None:
                    text = "Expected tag in line %d:\n %s" % (ln, line)
                    raise IOError(text)
                else:
                    # Active tag
                    if hasattr(current[mapping[tag]], '__iter__'):
                        current[mapping[tag]].append(line.strip())
                    else:
                        current[mapping[tag]] = [
                            current[mapping[tag]], line.strip()]
            else:
                if iscounter(line):
                    continue
                text = "Expected start tag in line %d:\n %s" % (ln, line)
                raise IOError(text)
