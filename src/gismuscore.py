##
# Generate all subsequences of xs.
#
# A subsequence t of s is a subset of s such that all members in t
# occur in the same order as in s.
#
# Example.
#   subsequences([a,b,c])
#   -> [a,b,c]
#   -> [a,b]
#   -> [a,c]
#   -> [a]
#   -> [b,c]
#   -> [b]
#   -> [c]
#   -> []
#
def subsequences(xs):
    def f(xs):
        if not xs:
            yield []
        while xs:
            x = xs.pop()
            for ys in f(xs):
                yield ys + [x]
                yield ys
    return f(list(xs))

##
# Return true if haystack is a subsequence of needle.
#
def isSubsequence(haystack, needle):
    i = -1
    for c in needle:
        i = haystack.find(c, i + 1)
        if i == -1:
            return False
    return True

##
# Return the number of common subsequences.
#
def commonSubsequences(gismu, word):
    max = 0
    for sub in subsequences(word):
        sub = ''.join(sub)
        if isSubsequence(gismu, sub):
            l = len(sub)
            if l > max:
                max = l
    return max

##
# Generate the letter pairs.
#
# A letter pair of w is defined as a pair of letters which are either
# adjacent in w or separated by a single letter.
#
def letterpairs(word):
    for i in xrange(len(word)):
        if i + 1 >= len(word):
            break
        yield word[i] + word[i+1]
        if i + 2 >= len(word):
            break
        yield word[i] + word[i+2]

##
# Generate offsets at which c occurs in s.
#
def findall(s, c):
    i = -1
    while True:
        i = s.find(c, i + 1)
        if i == -1:
            break
        yield i

##
# Return true if there is a common letter pair.
#
def commonLetterpair(gismu, word):
    for c, d in letterpairs(word):
        for i in findall(gismu, c):
            if i <= 3 and d == gismu[i+1]:
                return True
            if i <= 2 and d == gismu[i+2]:
                return True
    return False

##
# Return the score of word for gismu.
#
# The score is the number of common subsequences if this number
# exceeds 2.  Otherwise, the score is two if there is a common letter
# pair. Otherwise, the score is zero.
#
def score(gismu, word):
    matches = commonSubsequences(gismu, word)
    if matches >= 3:
        return matches
    if commonLetterpair(gismu, word):
        return 2
    return 0
