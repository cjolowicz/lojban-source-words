from gismufiles import *
from gismutables import *

##
# Load data from a file into one or many tables.
#
class Loader(object):
    def __init__(self, file, *tables):
        self.file = file
        self.tables = tables

    def open(self):
        self.file.open()
        for table in self.tables:
            table.open()

    def load(self):
        for table in self.tables:
            table.create()
            table.commit()

        for fields in self.file.load():
            for table in self.tables:
                table.insert(fields)

        for table in self.tables:
            table.commit()

    def close(self):
        self.file.close()
        for table in self.tables:
            table.close()

##
# Load data from the gismu file into the gismu tables.
#
class GismuLoader(Loader):
    def __init__(self, connection, filename):
        super(GismuLoader, self).__init__(
            GismuFile(filename),
            DefinitionTable(connection),
            HintwordTable(connection),
            TextbookTable(connection),
            FrequencyTable(connection),
            RafsiTable(connection),
            KeywordTable(connection))

##
# Load data from the keywords file into the keywords table.
#
class ObliqueKeywordsLoader(Loader):
    def __init__(self, connection, filename):
        super(ObliqueKeywordsLoader, self).__init__(
            ObliqueKeywordsFile(filename),
            Table(
                connection,
                'Keywords',
                ['gismu', 'place', 'keyword']))

##
# Load data from a TAB separated file into one or many tables.
#
class TabLoader(Loader):
    def __init__(self, filename, *tables):
        super(TabLoader, self).__init__(
            TabFile(filename, [attribute
                               for table in tables
                               for attribute in table.attributes]),
            *tables)

##
# Load data into the Arabic table.
#
class ArabicLoader(TabLoader):
    def __init__(self, connection, filename):
        super(ArabicLoader, self).__init__(
            filename,
            ArabicTable(connection))

##
# Load data into the Chinese table.
#
class ChineseLoader(TabLoader):
    def __init__(self, connection, filename):
        super(ChineseLoader, self).__init__(
            filename,
            ChineseTable(connection))

##
# Load data into the English table.
#
class EnglishLoader(TabLoader):
    def __init__(self, connection, filename):
        super(EnglishLoader, self).__init__(
            filename,
            EnglishTable(connection))

##
# Load data into the Hindi table.
#
class HindiLoader(TabLoader):
    def __init__(self, connection, filename):
        super(HindiLoader, self).__init__(
            filename,
            HindiTable(connection))

##
# Load data into the Russian table.
#
class RussianLoader(TabLoader):
    def __init__(self, connection, filename):
        super(RussianLoader, self).__init__(
            filename,
            RussianTable(connection))

##
# Load data into the Spanish table.
#
class SpanishLoader(TabLoader):
    def __init__(self, connection, filename):
        super(SpanishLoader, self).__init__(
            filename,
            SpanishTable(connection))

##
# Load data into the Cmavo table.
#
class CmavoLoader(Loader):
    def __init__(self, connection, filename):
        super(CmavoLoader, self).__init__(
            CmavoFile(filename),
            CmavoTable(connection))
