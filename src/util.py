##
# Remove elements containing item.
#
def removelike(sequence, item):
    def f(sequence, item):
        if sequence:
            elem = sequence.pop()
            if item in elem:
                return f(sequence, item)
            return f(sequence, item) + [elem]
        return []
    return f(sequence[:], item)

##
# Test case.
#
def test():
    xs = ['abc', 'def', 'ghi']
    print removelike(xs, 'e')

##
# Main entry point.
#
if __name__ == '__main__':
    test()
