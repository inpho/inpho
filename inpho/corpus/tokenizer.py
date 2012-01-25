"""
Base Tokenization class
"""
from elementtree.TidyTools import *
import re

import inpho.lib

class Tokenizer(object):
    """
    Abstract tokenization class, methods must be overloaded for each corpus
    type.
    """
    def article():
        raise NotImplementedError
    def paragraph():
        raise NotImplementedError
    def sentence():
        raise NotImplementedError
    def word():
        raise NotImplementedError

    def bibliography():
        raise NotImplementedError
    def citation():
        raise NotImplementedError
    
    def write_plaincorpus(self, outfile):
        """ Writes the plain text version of the corpus to a file """
        with codecs.open(outfile, encoding='utf-8', mode='w') as f:
            f.write(self.plain)

class SEPTokenizer(Tokenizer):
    def __init__(self, path):
        """
        Constructor takes a path to a SEP article and intializes a Tokenizer
        object. 
        """
        self.tree = tidy(path)
        self.title = # something from path
        self.plain = clean(self.tree)           # get paragraphs
        self.plain = '\n\n'.join(self.plain)    # join with 2 breaks
        self.plain = inpho.lib.unidecode(self.plain)    # unicode -> ascii range 

    def clean(self, tree, title):
        """
        Takes an ElementTree object and a string (title of the article)
        and returns the textual content of the article as a list of
        strings.
        """
        if self.html:
            # SEP Specific
            clr_pubinfo(self.html)
            clr_toc(self.html)
            clr_bib(self.html)
            clr_sectnum(self.html)

            # general routines
            proc_imgs(self.html)
            clr_inline(self.html)
            fill_par(self.html)
            return flatten(self.html)
        else:
            return title

    def _cp_map(self, tree=None):
        """
        Takes an ElementTree object and returns a child:parent dictionary.
        """
        if tree is None:
            tree = self.tree

        root = tree.getroot()
        return dict((c, p) for p in root.getiterator() for c in p)
    
    def clr_pubinfo(self, tree):
        """
        Takes an ElementTree object and child:parent dictionary and
        removes any node with the id attribute 'pubinfo'. (For SEP)
        """
        # TODO: Turn into a pop()-like function, return pubinfo
        cp = self._cp_map(tree)
        for el in filter_by_tag(tree.getiterator(), 'div'):
            if (el.attrib.has_key('id') and
                el.attrib['id'] == 'pubinfo'):
                cp[el].remove(el)
                return

        print '** Pub info not found **'
    
    def clr_toc(tree):
        """
        Takes an ElementTree and child:parent dictionary and removes any
        subtrees which are unordered lists of anchors. Such things are
        tables of contents in the SEP.
        """
        # TODO: Turn into a pop()-like function, return toc
        cp = self._cp_map(tree)
        uls = filter_by_tag(tree.getiterator(), 'ul')
        for ul in uls[:]:
            if reduce(lambda v1, v2: v1 and v2,
                      [filter_by_tag(li.getiterator(), 'a') is not []
                       for li in filter_by_tag(ul.getiterator(), 'li')]):
                cp[ul].remove(ul)
                return
        print '** TOC not found **'
        return
    
    def clr_bib(tree):
        """
        Takes an ElementTree and child:parent dictionary and removes nodes
        which are likely candidates for the bibliography in the SEP.
        """
        # TODO: Turn into a pop()-like function, return bib
        cp = self._cp_map(tree)

        hs = (filter_by_tag(tree.getiterator(), 'h2') +
              filter_by_tag(tree.getiterator(), 'h3'))
    
        for h in hs:
            for el in h.getiterator() + [h]:
                if ((el.text and
                     re.search(r'Bibliography', el.text)) or
                    (el.tail and
                     re.search(r'Bibliography', el.tail))):
                    p = cp[h]
                    i = list(p).index(h)
                    for node in p[i:]:
                        p.remove(node)
                    return
        print '** Bibliography not found. **'
        return
    
    def clr_sectnum(tree):
        """
        Takes an ElementTree object and child:parent dictionary and
        removes SEP text identifying section numbers.
        """
        hs = (filter_by_tag(tree.getiterator(), 'h1') +
              filter_by_tag(tree.getiterator(), 'h2') +
              filter_by_tag(tree.getiterator(), 'h3') +
              filter_by_tag(tree.getiterator(), 'h4') +
              filter_by_tag(tree.getiterator(), 'h5') +
              filter_by_tag(tree.getiterator(), 'h6'))
    
        n = re.compile('^[a-zA-Z ]*[0-9 \.]+ *')
        for h in hs[:]:
            els = h.getiterator()
            for el in els + [h]:
                if el.text:
                    el.text = re.sub(n, '', el.text)
    
    def proc_imgs(tree):
        """
        Takes an ElementTree object and child:parent dictionary and
        removes img nodes or replaces them with div nodes containing the
        alt text.
        """
        imgs = filter_by_tag(tree.getiterator(), 'img')
    
        for img in imgs:
            alt = img.attrib['alt']
            if alt:
                img.tag = get_prefix(img) + 'div'
                img.text = alt
        
    def fill_par(tree):
        """
        Takes an ElementTree object and removes extraneous spaces and line
        breaks from text and tail attributes.
        """
        els = tree.getiterator()
    
        sp = re.compile(' +')
        nl = re.compile('\n+')
        le = re.compile('^ +')
        tr = re.compile(' +$')
    
        for el in els[:]:
            if el.text:
                el.text = re.sub(nl, ' ', el.text)
                el.text = re.sub(sp, ' ', el.text)
                el.text = re.sub(le, '', el.text)
            if el.tail:
                el.tail = re.sub(nl, ' ', el.tail)
                el.tail = re.sub(sp, ' ', el.tail)
                el.tail = re.sub(tr, '', el.tail)
                
        return
    

    @property
    def html(self):
        """
        Returns the body of an SEP article, including the bibliography, all html
        tags, etc.
        """
        for elt in filter_by_tag(self.tree.getiterator(), 'div'):
            if elt.attrib['id'] == 'aueditable':
                return elt
