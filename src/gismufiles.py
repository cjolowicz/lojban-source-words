import codecs

##
# Process a file line by line.
#
class File(object):
    def __init__(self, filename):
        self.filename = filename

    def open(self):
        self.file = codecs.open(self.filename, 'r', 'utf-8')

    def load(self):
        for line in self.file:
            for fields in self.process(line):
                yield fields

    def process(self, line):
        pass

    def close(self):
        self.file.close()

##
# Process a file with tab-separated data.
#
class TabFile(File):
    def __init__(self, filename, attributes):
        super(TabFile, self).__init__(filename)
        self.attributes = attributes

    def process(self, line):
        yield dict(zip(self.attributes,
                       map(unicode.strip,
                           line.split('\t'))))

##
# Process a file with fixed offsets.
#
class OffsetFile(File):
    def __init__(self, filename, offsets):
        super(OffsetFile, self).__init__(filename)
        self.offsets = offsets

    def process(self, line):
        fields = {}

        for (attribute, (begin, end)) in self.offsets.iteritems():
            if end == -1:
                fields[attribute] = line[begin:].strip()
            else:
                fields[attribute] = line[begin:end].strip()

        yield fields

##
# Process a file with fixed offsets.
#
class ObliqueKeywordsFile(File):
    def process(self, line):
        temp, keywords = line.split(';', 1)

        # skip cmavo
        if len(temp) != 6:
            return

        for keyword in keywords.split(';'):
            yield dict(gismu=temp[:5],
                       place=int(temp[5]),
                       keyword=keyword.strip())

##
# Process the gismu file.
#
class GismuFile(OffsetFile):
    def __init__(self, filename):
        super(GismuFile, self).__init__(
            filename,
            dict(gismu=(1, 7),
                 cvc=(7, 11),
                 ccv=(11, 15),
                 cvv=(15, 20),
                 keyword=(20, 41),
                 hintword=(41, 62),
                 definition=(62, 159),
                 textbook=(159, 161),
                 frequency=(161, 169),
                 comment=(169, -1)))

    def open(self):
        super(GismuFile, self).open()
        # skip the first line
        for line in self.file:
            break

    def process(self, line):
        for fields in super(GismuFile, self).process(line):
            # skip cmavo
            if len(fields['gismu']) != 5:
                continue

            yield self.parse(fields)

    def parse(self, fields):
        comment = fields.pop('comment')
        fields['comments'] = []
        fields['xrefs'] = []

        comments = self.splitComment(comment)

        xreflists = []
        for part in comments:
            part = part.strip()
            if part.startswith('cf'):
                fields['xrefs'].append(part)
            else:
                fields['comments'].append(part)

        fields['xrefs'] = '; '.join(fields['xrefs'])
        fields['comments'] = '; '.join(fields['comments'])

        return fields

    def splitComment(self, comment):
        comment = self.fixComment(comment)

        parens = []
        part = ''
        parts = []

        for c in comment:
            if c in '([':
                parens.append(c)
                if len(parens) != 1:
                    part += c
            elif c == ')' and parens and parens[-1] == '(' or \
                 c == ']' and parens and parens[-1] == '[':
                parens.pop()
                if parens:
                    part += c
                    continue
                part = part.strip()
                parts.append(part)
                part = ''
            elif parens:
                part += c

        part = part.strip()
        if part:
            parts.append(part)

        return parts

    def fixComment(self, comment):
        return self.brokenComments.get(comment, comment)

    brokenComments = dict([
        ('[x3 sides/surfaces should include number, size, and shape; also polyhedron (= pitybli having flat/planar sides/surfaces)], regular polyhedron (= kubybli, blikubli), brick (= kitybli); (cf. tapla, kubli, tanbo, canlu, kojna, sefta, bolci, kurfa, tarmi)',
         '[x3 sides/surfaces should include number, size, and shape; also polyhedron (= pitybli having flat/planar sides/surfaces), regular polyhedron (= kubybli, blikubli), brick (= kitybli)]; (cf. tapla, kubli, tanbo, canlu, kojna, sefta, bolci, kurfa, tarmi)'),

        ('[also (adjective:) x1, x2, x4 is/are commercial (better expressed as ka canja, kamcanja)]; x2/x3 may be a specific object, a commodity (mass), an event (possibly service), or a property; pedantically, for objects/commodities, this is sumti-raising from ownership of the object/commodity (= posycanja for unambiguous semantics); (cf. dunda, friti, vecnu, zarci, jdini, pleji, jdima, jerna, kargu; see note at jdima on cost/price/value distinction, banxa, cirko, dunda, janta, kargu, prali, sfasa, zivle)',
         '[also (adjective:) x1, x2, x4 is/are commercial (better expressed as ka canja, kamcanja); x2/x3 may be a specific object, a commodity (mass), an event (possibly service), or a property; pedantically, for objects/commodities, this is sumti-raising from ownership of the object/commodity (= posycanja for unambiguous semantics)]; (cf. dunda, friti, vecnu, zarci, jdini, pleji, jdima, jerna, kargu; see note at jdima on cost/price/value distinction, banxa, cirko, dunda, janta, kargu, prali, sfasa, zivle)')
        ])

##
# Process the cmavo file.
#
class CmavoFile(OffsetFile):
    def __init__(self, filename):
        super(CmavoFile, self).__init__(
            filename,
            dict(cmavo=(1, 11),
                 selmao=(11, 20),
                 keyword=(20, 62),
                 definition=(62, 168),
                 comment=(168, -1)))
        # definition=(62, 112), # or 145, or 146, or 168
        # comment=(112, 146), # or 145, or 168; or from 109 (sepu'a), 110 (tepu'a), 107 (teta'i)
        # picture=(146, 168), # or from 145

    def open(self):
        super(CmavoFile, self).open()
        # skip the first line
        for line in self.file:
            break
