"""
Base Tokenization class
"""
import re
import os.path

import inpho.lib
from inpho.corpus import sep

from elementtree.TidyTools import *
from elementtree.ElementTree import ElementTree


class Reader(object):
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

def flatten(t):
    """
    Takes an Element and returns a list of strings, extracted from the
    text and tail attributes of the nodes in the tree, in a sensible
    order.
    """
    pre = pre_iter(t)
    post = post_iter(t)

    out = [tag.text for tag in pre]

    i = 0
    for k,n in enumerate(post):
        j = pre.index(n) + k
        i = j if j > i else i + 1
        out.insert(i+1, n.tail)

    return [text for text in out if text]

def pre_iter(t, tag=None):
    """
    Takes an Element, and optionally a tag name, and performs a
    preorder traversal and returns a list of nodes visited ordered
    accordingly.
    """
    return t.getiterator(tag)

def post_iter(t, tag=None):
    """
    Takes an Element object, and optionally a tag name, and performs a
    postorder traversal and returns a list of nodes visited ordered
    accordingly.
    """
    nodes = []
    for node in t._children:
        nodes.extend(post_iter(node, tag))
    if tag == "*":
        tag = None
    if tag is None or t.tag == tag:
        nodes.append(t)
    return nodes

def cp_map(tree):
    """
    Takes an Element object and returns a child:parent dictionary.
    """
    return dict((c, p) for p in tree.getiterator() for c in p)

def match_qname(local, qname):
    """
    Expects a tag name given as the local portion of a QName (e.g.,
    'h1') and matches it against a full QName.
    """
    return re.search('^\{.*\}' + local, qname)

def filter_by_tag(elems, tag):
    """
    Takes a list of Element objects and filters it by a local tag
    name (e.g., 'h1').
    """
    return [el for el in elems if match_qname(tag, el.tag)]

def get_prefix(t):
    """
    Takes an Element object and returns the prefix portion of the
    QName (its tag). For example, if t is XHTML, the QName may be
    'http://www.w3.org/1999/xhtml'. (A typical tag in t would be
    '{http://www.w3.org/1999/xhtml}div').
    """
    p = re.compile('^\{.*\}')
    m = re.search(p, t.tag)
    if m is None:
        return ''
    else:
        return m.group(0)


class SEPReader(Reader):
    def __init__(self, article=None):
        """
        Constructor takes a path to a SEP article and intializes a Reader
        object. 
        """
        # intialize sepdir and path arguments
        if os.path.exists(article):
            if os.path.isdir(article):
                self.path = os.path.join(article, 'index.html')
            else:
                self.path = article
            self.sepdir = None
        else:
            self.path = None
            self.sepdir = article

        # automatically build path using sepdir
        if self.sepdir and self.path is None:
            self.path = os.path.join(inpho.corpus.path, self.sepdir, 'index.html')
        # automatically extract sepdir from path
        elif self.path and self.sepdir is None:
            self.sepdir = os.path.dirname(self.path)
            self.sepdir = os.path.split(self.sepdir)[1]

        self.title = sep.get_title(self.sepdir)
        # import the DOM of the SEP article
        self.tree = tidy(self.path)
        self.plain = self.clean()           # get paragraphs
        self.plain = '\n\n'.join(self.plain)    # join with 2 breaks
        self.plain = inpho.lib.unidecode(self.plain)    # unicode -> ascii range 

    def clean(self):
        """
        Takes an ElementTree object and a string (title of the article)
        and returns the textual content of the article as a list of
        strings.
        """

        self.tree = self.tree.getroot()
        self.tree = self.get_auedit()

        if self.tree:
            # SEP Specific
            self.clr_pubinfo()
            self.clr_toc()
            self.clr_bib()
            self.clr_sectnum()

            # general routines
            self.proc_imgs()
            self.clr_inline()
            self.fill_par()
            return flatten(self.tree)
        else:
            return self.title

    # def _cp_map(self, tree=None):
    #     """
    #     Takes an Element object and returns a child:parent dictionary.
    #     """
    #     if tree is None:
    #         tree = self.tree

    #     return dict((c, p) for p in root.getiterator() for c in p)
    
    def clr_pubinfo(self):
        """
        Takes an Element object and removes any node with the id
        attribute 'pubinfo'. (For SEP)
        """
        # TODO: Turn into a pop()-like function, return pubinfo
        cp = cp_map(self.tree)
        for el in filter_by_tag(self.tree.getiterator(), 'div'):
            if (el.attrib.has_key('id') and
                el.attrib['id'] == 'pubinfo'):
                cp[el].remove(el)
                return

        print '** Pub info not found **'
    
    def clr_toc(self):
        """
        Takes an Element object and removes any subtrees which are
        unordered lists of anchors. Such things are tables of contents
        in the SEP.
        """
        # TODO: Turn into a pop()-like function, return toc
        cp = cp_map(self.tree)
        uls = filter_by_tag(self.tree.getiterator(), 'ul')
        for ul in uls[:]:
            if reduce(lambda v1, v2: v1 and v2,
                      [filter_by_tag(li.getiterator(), 'a') is not []
                       for li in filter_by_tag(ul.getiterator(), 'li')]):
                cp[ul].remove(ul)
                return
        print '** TOC not found **'
        return
    
    def clr_bib(self):
        """
        Takes an Element object and removes nodes which are likely
        candidates for the bibliography in the SEP.
        """
        # TODO: Turn into a pop()-like function, return bib
        cp = cp_map(self.tree)

        hs = (filter_by_tag(self.tree.getiterator(), 'h2') +
              filter_by_tag(self.tree.getiterator(), 'h3'))
    
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
    
    def clr_sectnum(self):
        """
        Takes an Element object and child:parent dictionary and
        removes SEP text identifying section numbers.
        """
        hs = (filter_by_tag(self.tree.getiterator(), 'h1') +
              filter_by_tag(self.tree.getiterator(), 'h2') +
              filter_by_tag(self.tree.getiterator(), 'h3') +
              filter_by_tag(self.tree.getiterator(), 'h4') +
              filter_by_tag(self.tree.getiterator(), 'h5') +
              filter_by_tag(self.tree.getiterator(), 'h6'))
    
        n = re.compile('^[a-zA-Z ]*[0-9 \.]+ *')
        for h in hs[:]:
            els = h.getiterator()
            for el in els + [h]:
                if el.text:
                    el.text = re.sub(n, '', el.text)
    
    def proc_imgs(self):
        """
        Takes an Element object and child:parent dictionary and
        removes img nodes or replaces them with div nodes containing the
        alt text.
        """
        imgs = filter_by_tag(self.tree.getiterator(), 'img')
    
        for img in imgs:
            alt = img.attrib['alt']
            if alt:
                img.tag = get_prefix(img) + 'div'
                img.text = alt

    def clr_inline(self):
        """
        Takes an Element object, looks for nodes whose tags are xhmtl
        inline tags, and removes these nodes while appending the contents
        of their text and tail attributes in the appropriate places.
        """
        inline = ['b', 'em', 'i', 'tt', 'big', 'small', 'bdo',
                  'strong', 'dfn', 'code', 'samp', 'kbd', 'var',
                  'cite', 'span', 'font', 'sub', 'sup', 's',
                  'strike', 'center', 'a', 'abbr', 'acronym',
                  'u', 'br', 'del', 'ins', 'q']
    
        # Recall that text in xhtml documents will show up in two places
        # in an ElementTree Element Object: either in the text or in the tail
        # attribute. Suppose you have this chunk of html
        # '<p>real<em>foo</em>bar</p>'. The text attribute for the node
        # corresponding to the p tag has value 'real'. The text attribute for
        # the node corresponding to the em tag has value 'foo'. Where should
        # 'bar' go? In fact, the *tail* attribute of em stores 'bar'.
    
        def clr(t, cp):
            for node in t[:]:
                clr(node, cp_map(t))
            if [inl for inl in inline if match_qname(inl, t.tag)]:
                i = list(cp[t]).index(t)
                if i == 0:
                    # no left sibling
                    if cp[t].text is None:
                        cp[t].text = ''
                    if t.text:
                        cp[t].text = cp[t].text + t.text
                    if t.tail:
                        cp[t].text = cp[t].text + t.tail
                    cp[t].remove(t)
                else:
                    # left sibling
                    if cp[t][i-1].tail is None:
                        cp[t][i-1].tail = ''
                    if t.text:
                        cp[t][i-1].tail = cp[t][i-1].tail + t.text
                    if t.tail:
                        cp[t][i-1].tail = cp[t][i-1].tail + t.tail
                    cp[t].remove(t)
            return
       
        for el in self.tree[:]:
            clr(el, cp_map(self.tree))
        return
        
    def fill_par(self):
        """
        Takes an Element object and removes extraneous spaces and line
        breaks from text and tail attributes.
        """
        els = self.tree.getiterator()
    
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
    

    def get_auedit(self):
        """
        Takes an Element object and returns a subtree containing only the body
        of an SEP article.
        """
        #TODO: Merge with self.html property definition
        for el in filter_by_tag(self.tree.getiterator(), 'div'):
            if el.attrib['id'] == 'aueditable':
                return el
