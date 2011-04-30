##
# Print data to a file using a format string.
#
class Formatter(object):
    def write(self, file, data):
        file.write(data)

    def __call__(self, file):
        begin, end = 0, -1

        while True:
            end = self.format.find('%', begin)
            if end == -1:
                file.write(self.format[begin:])
                break

            file.write(self.format[begin:end])

            if self.format[end+1] == '%':
                file.write('%')
                begin = end + 2
                continue

            if self.format[end+1] != '(':
                raise Exception, "missing `('"

            begin = self.format.find(')', end + 2)
            if begin == -1:
                raise Exception, "missing `)'"

            name = self.format[end+2:begin]
            begin += 1

            attr = getattr(self, name)
            if hasattr(attr, '__call__'):
                attr(file)
            elif type(attr) == unicode or type(attr) == str:
                self.write(file, attr)
            elif hasattr(attr, '__str__'):
                self.write(file, str(attr))
            else:
                raise Exception, \
                    "attribute `%s' is neither callable nor printable" % name

##
# Simple formatter for testing.
#
class TestFormatter(Formatter):
    # Test callable.
    def longname(self, file):
        self.write(file, 'Internet Message Access Protocol')

    # Test unicode object.
    version = u'4rev1'

    # Test string.
    shortname = 'IMAP4rev1'

    # Test printable.
    section = 3

    # Format string.
    format = '''\
   The %(longname), Version %(version) (%(shortname))
   allows a client to access and manipulate electronic mail messages on
   a server.  %(shortname) permits manipulation of mailboxes (remote
   message folders) in a way that is functionally equivalent to local
   folders.  %(shortname) also provides the capability for an offline
   client to resynchronize with the server.

   %(section))    Although the list-wildcard characters ("%%" and "*") are valid
         in a mailbox name, it is difficult to use such mailbox names
         with the LIST and LSUB commands due to the conflict with
         wildcard interpretation.
'''

##
# Main entry point.
#
if __name__ == '__main__':
    import sys
    TestFormatter()(sys.stdout)
