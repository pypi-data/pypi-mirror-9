"""
Methods for parsing JSTOR Data-for-Research datasets.

.. autosummary::

   read
   ngrams
   read_corpus
   from_dir
   ngrams_from_dir
   corpus_from_dir

"""

from ..classes import Paper, Corpus

import os
import xml.etree.ElementTree as ET
import re
from ..utilities import dict_from_node, strip_non_ascii
from nltk.corpus import stopwords
import uuid
from collections import Counter

from unidecode import unidecode

class GramGenerator(object):
    """
    Yields N-gram data from on-disk dataset, to make loading big datasets a bit
    more memory-friendly.
    
    Reusable, in the sense that :func:`.items`\, :func:`.iteritems`\,
    :func:`.keys`\, and :func:`.values` all return new :class:`.GramGenerator`
    instances with the same path. This allows a :class:`.GramGenerator` to 
    sneakily pass as an ngrams dict in most practical situations.
    """

    def __init__(self, path, elem, values=False, keys=False, ignore_hash=True):
        """
        
        Parameters
        ----------
        path : str
            Path to unzipped JSTOR DfR folder containing N-grams (e.g. 
            'bigrams'). 
        elem : str
            Element in DfR dataset containing data of interest. E.g. 'bigrams'.
        values : bool
            If True, :func:`.next` returns only values. Otherwise, returns
            (key,value) tuples.
        """

        self.path = path
        self.elem = elem
        self.ignore_hash = ignore_hash
                
        self.files = os.listdir(path)
        self.N = len([ d for d in self.files if d.split('.')[-1] == 'XML' ])
        self.i = 0
        
        self.V = values
        self.K = keys
        
        if self.V and self.K:
            raise ValueError('values and keys cannot both be true.')
    
    def __len__(self):
        return self.N
    
    def __iter__(self):
        return self
    
    def __next__(self):
        return self.next()
    
    def next(self):
        if self.i < self.N:
            cur = int(self.i)
            self.i += 1
            return self._get(cur)
        else:
            raise StopIteration()
            
    def items(self):
        """
        Returns a :class:`GramGenerator` that produces key,value tuples.
        """    
        return GramGenerator(self.path, self.elem, ignore_hash=self.ignore_hash)
    
    def iteritems(self):
        """
        Returns a :class:`GramGenerator` that produces key,value tuples.
        """    
        return GramGenerator(self.path, self.elem, ignore_hash=self.ignore_hash)
    
    def values(self):
        """
        Returns a :class:`GramGenerator` that produces only values.
        """
        return GramGenerator(self.path, self.elem, values=True, 
                                                   ignore_hash=self.ignore_hash)
                                                   
    def keys(self):
        """
        Returns a :class:`GramGenerator` that produces only keys.
        """
        return GramGenerator(self.path, self.elem, keys=True, 
                                                   ignore_hash=self.ignore_hash)
                                                   
    def __getitem__(self, key):
        return self._get(key)
    
    def _get(self, i):
        """
        Retrieve data for the ith file in the dataset.
        """
        root = ET.parse(self.path + "/" + self.files[i]).getroot()
        doi = root.attrib['id']

        if self.K:  # Keys only.
            return doi

        grams = []
        for gram in root.findall(self.elem):
            text = unidecode(unicode(gram.text.strip()))
            if ( not self.ignore_hash or '#' not in list(text) ):
                c = ( text, int(gram.attrib['weight']) )
                grams.append(c)
        
        if self.V:  # Values only.
            return grams

        return doi, grams   # Default behavior.

def read(datapath, **kwargs):
    """
    Yields :class:`.Paper` s from JSTOR DfR package.

    Each :class:`.Paper` is tagged with an accession id for this
    read/conversion.

    Parameters
    ----------
    filepath : string
        Filepath to unzipped JSTOR DfR folder containing a citations.XML file.

    Returns
    -------
    papers : list
        A list of :class:`.Paper` objects.

    Examples
    --------

    .. code-block:: python

       >>> from tethne.readers import dfr
       >>> papers = dfr.read("/Path/to/DfR")
    """

    with open(datapath + "/citations.XML", mode='r') as f:
        data = f.read()
        data = data.replace('&', '&amp;')
        
        root = ET.fromstring(data)

    accession = str(uuid.uuid4())

    papers = kwargs.get('papers', [])
    for article in root:
        paper = _handle_paper(article)
        paper['accession'] = accession
        papers.append(paper)

    return papers

def read_corpus(path, features=None, exclude=None, **kwargs):
    """
    Generate a :class:`.Corpus` from a single DfR dataset.
    
    If ``features`` is provided (see below), will also load ngrams.
    
    Parameters
    ----------
    filepath : string
        Filepath to unzipped JSTOR DfR folder containing a citations.XML file.
    features : list
        List of feature-grams (e.g. 'uni', 'bi', 'tri') to load from dataset.
    exclude : list
        Stoplist for feature-grams.
    **kwargs
        Use this to pass kwargs to :func:`.ngrams`.
        
    Returns
    -------
    :class:`.Corpus`
    
    Examples
    --------

    .. code-block:: python

       >>> from nltk.corpus import stopwords    # Get a stoplist.
       >>> stoplist = stopwords.words()
       >>> from tethne.readers import dfr
       >>> MyCorpus = dfr.read_corpus("/Path/to/DfR", ['uni'], stoplist)
    """

    papers = read(path)
    grams = {}
    if features is not None:
        for feat in features:
            grams[feat+'grams'] = ngrams(path, feat, **kwargs)

    return Corpus(papers, features=grams, index_by='doi', exclude=exclude)

def from_dir(path):
    """
    Convenience function for generating a list of :class:`.Paper` from a
    directory of JSTOR DfR datasets.

    Parameters
    ----------
    path : string
        Path to directory containing DfR dataset directories.

    Returns
    -------
    papers : list
        A list of :class:`.Paper` objects.

    Raises
    ------
    IOError
        Invalid path.

    Examples
    --------

    .. code-block:: python

       >>> from tethne.readers import dfr
       >>> papers = dfr.from_dir("/Path/to/datadir")

    """

    papers = []

    try:
        files = os.listdir(path)
    except IOError:
        raise IOError("Invalid path.")  # Ignore hidden files.

    for f in files:
        if not f.startswith('.') and os.path.isdir(path + "/" + f):
            try:
                papers += read(path + "/" + f)
            except (IOError, UnboundLocalError):    # Ignore directories that
                pass                                #  don't contain DfR data.

    return papers

def ngrams_from_dir(path, N='uni', ignore_hash=True, mode='heavy'):
    """
    Load ngrams from a directory of JSTOR DfR datasets.
    
    Parameters
    ----------
    path : string
        Path to directory containing DfR dataset directories.
    N : string
        'uni', 'bi', 'tri', or 'quad'
    ignore_hash : bool
        If True, will exclude all N-grams that contain the hash '#' character.
    mode : str
        If 'heavy' (default), loads all data into memory and returns a dict. If
        'light', returns a (somewhat) reusable :class:`.GramGenerator`\. See
        :class:`.GramGenerator` for usage.
        
    Returns
    -------
    ngrams : dict
        Keys are paper DOIs, values are lists of (Ngram, frequency) tuples.
        
    Examples
    --------
    
    .. code-block:: python
    
       >>> from tethne.readers import dfr
       >>> ngrams = dfr.ngrams_from_dir("/Path/to/datadir", 'uni')
       
    """

    grams = {}
    try:
        files = os.listdir(path)
    except IOError:
        raise IOError('Invalid path.')

    for f in files:
        if not f.startswith('.') and os.path.isdir(path + '/' + f):
            try:
                fpath = path + '/' + f
                grams.update(ngrams(fpath, N, ignore_hash, mode))
            except (IOError, UnboundLocalError, OSError):
                pass

    return grams
                                
def corpus_from_dir(path, features=None, exclude=None, **kwargs):
    """
    Generate a :class:`.Corpus` from a directory containing multiple DfR 
    datasets.
    
    If ``features`` is provided (see below), will also load ngrams.

    Parameters
    ----------
    path : string
        Path to directory containing DfR dataset directories.
    features : list
        List of feature-grams (e.g. 'uni', 'bi', 'tri') to load from dataset.
    exclude : list
        Stoplist for feature-grams.
    **kwargs
        Use this to pass kwargs to :func:`.ngrams`.
    
    Returns
    -------
    :class:`.Corpus`
    
    Examples
    --------
    
    .. code-block:: python
    
       >>> from nltk.corpus import stopwords    # Get a stoplist.
       >>> stoplist = stopwords.words()
       >>> from tethne.readers import dfr
       >>> C = dfr.corpus_from_dir('/path/to/DfR/datasets', 'uni', stoplist)

    """

    papers = from_dir(path)
    grams = {}
    if features is not None:
        for feat in features:
            grams[feat+'grams'] = ngrams_from_dir(path, **kwargs)

    return Corpus(papers, features=grams, index_by='doi', exclude=exclude)

def ngrams(datapath, N='uni', ignore_hash=True, mode='heavy'):
    """
    Yields N-grams from a JSTOR DfR dataset.

    Parameters
    ----------
    datapath : string
        Path to unzipped JSTOR DfR folder containing N-grams (e.g. 'bigrams').
    N : string
        'uni', 'bi', 'tri', or 'quad'
    ignore_hash : bool
        If True, will exclude all N-grams that contain the hash '#' character.
    mode : str
        If 'heavy' (default), loads all data into memory and returns a dict. If
        'light', returns a (somewhat) reusable :class:`.GramGenerator`\. See
        :class:`.GramGenerator` for usage.

    Returns
    -------
    ngrams : dict
        Keys are paper DOIs, values are lists of (Ngram, frequency) tuples.

    Examples
    --------

    .. code-block:: python

       >>> from tethne.readers import dfr
       >>> trigrams = dfr.ngrams("/Path/to/DfR", N='tri')
    """

    if  N =='uni':
        gram_dir = "/wordcounts"
        elem = "wordcount"
    else:
        gram_dir = "/" + N + "grams"
        elem = N + "gram"
    gram_path = datapath + gram_dir

    if mode == 'light':
        return GramGenerator(gram_path, elem, ignore_hash=ignore_hash)
        
    elif mode == 'heavy':
        ngrams = {}

        for file in os.listdir(gram_path):
            if file.split('.')[-1] == 'XML':
                root = ET.parse(gram_path + "/" + file).getroot()
                doi = root.attrib['id']
                grams = []
                for gram in root.findall(elem):
                    text = unidecode(unicode(gram.text.strip()))
                    if ( not ignore_hash or '#' not in list(text) ):
                        c = ( text, int(gram.attrib['weight']) )
                        grams.append(c)

                ngrams[doi] = grams

        return ngrams
        
def tokenize(ngrams, min_tf=2, min_df=2, min_len=3, apply_stoplist=False):
    """
    Builds a vocabulary, and replaces words with vocab indices.
    
    Parameters
    ----------
    ngrams : dict
        Keys are paper DOIs, values are lists of (Ngram, frequency) tuples.
    apply_stoplist : bool
        If True, will exclude all N-grams that contain words in the NLTK
        stoplist.        
        
    Returns
    -------
    t_ngrams : dict
        Tokenized ngrams, as doi:{i:count}.
    vocab : dict
        Vocabulary as i:term.
    token_tf : :class:`.Counter`
        Term counts for corpus, as i:count.
    """

    vocab = {}
    vocab_ = {}
    word_tf = Counter()
    word_df = Counter()
    token_tf = Counter()
    token_df = Counter()
    t_ngrams = {}
    
    # Get global word counts, first.
    for grams in ngrams.values():
        for g,c in grams:
            word_tf[g] += c
            word_df[g] += 1
            
    if apply_stoplist:
        stoplist = stopwords.words()
            
    # Now tokenize.
    for doi,grams in ngrams.iteritems():
        t_ngrams[doi] = []
        for g,c in grams:
            ignore = False
                        
            # Ignore extremely rare words (probably garbage).
            if word_tf[g] < min_tf or word_df[g] < min_df or len(g) < min_len:
                ignore = True

            # Stoplist.
            elif apply_stoplist:
                for w in g.split():
                    if w in stoplist:
                        ignore = True            

            if not ignore:
                
                # Coerce unicode to string.
                if type(g) is str:
                    g = unicode(g)
                g = unidecode(g)
                
                if g not in vocab.values():
                    i = len(vocab)
                    vocab[i] = g
                    vocab_[g] = i
                else:
                    i = vocab_[g]
                token_tf[i] += c
                token_df[i] += 1

                t_ngrams[doi].append( (i,c) )

    return t_ngrams, vocab, token_tf

def _handle_paper(article):
    """
    Yields a :class:`.Paper` from an article ET node.

    Parameters
    ----------
    article : Element
        ElementTree Element 'article'.

    Returns
    -------
    paper : :class:`.Paper`
    """
    paper = Paper()
    pdata = dict_from_node(article)

    # Direct mappings.
    translator = _dfr2paper_map()
    for key, value in translator.iteritems():
        if key in pdata:    # Article may not have all keys of interest.
            datum = pdata[key]
            if type(datum) is str:
                datum = unicode(datum)
            if type(datum) is unicode:
                datum = unidecode(datum).upper()

            try:    # For now, ignore weird types that come through in datum.
                paper[value] = datum
            except ValueError:  
                pass

    # Handle author names.
    paper['aulast'], paper['auinit'] = _handle_authors(pdata['author'])

    # Handle pubdate.
    paper['date'] = _handle_pubdate(pdata['pubdate'])

    # Handle pagerange.
    paper['spage'], paper['epage'] = _handle_pagerange(pdata['pagerange'])

    # Generate ayjid.
    try:
        paper['ayjid'] = _create_ayjid(paper['aulast'][0], paper['auinit'][0], \
                                       paper['date'], paper['jtitle'])
    except IndexError:  # Article may not have authors.
        pass

    return paper

def _handle_pagerange(pagerange):
    """
    Yields start and end pages from DfR pagerange field.

    Parameters
    ----------
    pagerange : str or unicode
        DfR-style pagerange, e.g. "pp. 435-444".

    Returns
    -------
    start : str
        Start page.
    end : str
        End page.
    """

    try:
        pr = re.compile("pp\.\s([0-9]+)\-([0-9]+)")
        start, end = re.findall(pr, pagerange)[0]
    except IndexError:
        start = end = 0

    return str(start), str(end)

def _handle_pubdate(pubdate):
    """
    Yields a date integer from DfR pubdate field.
    """

    return int(pubdate[0:4])

def _handle_authors(authors):
    """
    Yields aulast and auinit lists from value of authors node.

    Parameters
    ----------
    authors : list, str, or unicode
        Value or values of 'author' element in DfR XML.

    Returns
    -------
    aulast : list
        A list of author surnames (string).
    auinit : list
        A list of author first-initials (string).
    """

    aulast = []
    auinit = []
    if type(authors) is list:
        for author in authors:
            if type(author) is str:
                author = unicode(author)
            author = unidecode(author)
            try:
                l,i = _handle_author(author)
                aulast.append(l)
                auinit.append(i)
            except ValueError:
                pass
    elif type(authors) is str or type(authors) is unicode:
        if type(authors) is str:
            authors = unicode(authors)
        author = unidecode(authors)
        try:
            l,i = _handle_author(author)
            aulast.append(l)
            auinit.append(i)
        except ValueError:
            pass
    else:
        raise ValueError("authors must be a list or a string")

    return aulast, auinit

def _handle_author(author):
    """
    Yields aulast and auinit from an author's full name.

    Parameters
    ----------
    author : str or unicode
        Author fullname, e.g. "Richard L. Nixon".

    Returns
    -------
    aulast : str
        Author surname.
    auinit : str
        Author first-initial.
    """

    lname = author.split(' ')

    try:
        auinit = lname[0][0]
        final = lname[-1].upper()
        if final in ['JR.', 'III']:
            aulast = lname[-2].upper() + " " + final.strip(".")
        else:
            aulast = final
    except IndexError:
        raise ValueError("malformed author name")

    return aulast, auinit

def _dfr2paper_map():
    """
    Defines the direct relationships between DfR article elements and
    :class:`.Paper` fields.

    Returns
    -------
    translator : dict
        A 'translator' dictionary.
    """

    translator = {  'doi': 'doi',
                    'title': 'atitle',
                    'journaltitle': 'jtitle',
                    'volume': 'volume',
                    'issue': 'issue'    }

    return translator

def _create_ayjid(aulast=None, auinit=None, date=None, jtitle=None, **kwargs):
    """
    Convert aulast, auinit, and jtitle into the fuzzy identifier ayjid
    Returns 'Unknown paper' if all id components are missing (None).

    Parameters
    ----------
    Kwargs : dict
        A dictionary of keyword arguments.
    aulast : string
        Author surname.
    auinit: string
        Author initial(s).
    date : string
        Four-digit year.
    jtitle : string
        Title of the journal.

    Returns
    -------
    ayj : string
        Fuzzy identifier ayjid, or 'Unknown paper' if all id components are
        missing (None).

    """
    if aulast is None:
        aulast = ''
    elif isinstance(aulast, list):
        aulast = aulast[0]

    if auinit is None:
        auinit = ''
    elif isinstance(auinit, list):
        auinit = auinit[0]

    if date is None:
        date = ''

    if jtitle is None:
        jtitle = ''

    ayj = aulast + ' ' + auinit + ' ' + str(date) + ' ' + jtitle

    if ayj == '   ':
        ayj = 'Unknown paper'

    return ayj.upper()
