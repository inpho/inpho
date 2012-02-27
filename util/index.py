from inpho.corpus.lexicon import DatabaseLexicon
from inpho.corpus.reader import FileReader

print "parsing document"
reader = FileReader('/Users/jammurdo/chapter.txt')
reader.plain = reader.plain.replace('\xc0', ' ')
reader.plain = reader.plain.replace('\xc2', ' ')
reader.plain = reader.plain.replace('  ', ' ')

print "parsing index"
index = FileReader('/Users/jammurdo/index.txt')
index.plain = index.plain.replace('\n\n', ' ')

print "retrieving lexicon"
lexicon = DatabaseLexicon()
print "processing document"
terms = lexicon.document_occurrences(reader)
print terms
print "processing index"
index_terms = lexicon.document_occurrences(index)
print index_terms

print "yielding terms"
for term in terms:
    if term not in index_terms:
        print term

