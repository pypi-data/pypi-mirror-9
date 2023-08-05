"""
Methods for generating networks in which papers are vertices.

.. autosummary::
   :nosignatures:

   author_coupling
   bibliographic_coupling
   cocitation
   direct_citation
   topic_coupling

"""

import networkx as nx
from .. import utilities as util
import helpers
import operator
import numpy
from collections import Counter

from ..classes.paper import Paper

def direct_citation(papers, node_id='ayjid', node_attribs=['date'], **kwargs):
    """
    Create a traditional directed citation network.

    Direct-citation graphs are `directed acyclic graphs`__ in which vertices are
    papers, and each (directed) edge represents a citation of the target
    paper by the source paper. The :func:`.networks.papers.direct_citation`
    method generates both a global citation graph, which includes all cited and
    citing papers, and an internal citation graph that describes only citations
    among papers in the original dataset.

    .. _dag: http://en.wikipedia.org/wiki/Directed_acyclic_graph

    __ dag_

    To generate direct-citation graphs, use the
    :func:`.networks.papers.direct_citation` method. Note the size difference
    between the global and internal citation graphs.

    .. code-block:: python

       >>> gDC, iDC = nt.papers.direct_citation(papers)
       >>> len(gDC)
       5998
       >>> len(iDC)
       163

    ==============     =========================================================
    Element            Description
    ==============     =========================================================
    Node               Papers, represented by node_id.
    Edge               From a paper to a cited reference.
    Edge Attribute     Publication date of the citing paper.
    ==============     =========================================================

    Parameters
    ----------
    papers : list
        A list of :class:`.Paper` instances.

    node_id : int
        A key from :class:`.Paper` to identify the nodes. Default is 'ayjid'.

    node_attribs : list
        List of user provided optional arguments apart from the provided
        positional arguments.

    Returns
    -------
    citation_network : networkx.DiGraph
        Global citation network (all citations).
    citation_network_internal : networkx.DiGraph
        Internal citation network where only the papers in the list are nodes in
        the network.

    Raises
    ------
    KeyError : If node_id is not present in the meta_list.
    """
    citation_network = nx.DiGraph(type='citations')
    citation_network_internal = nx.DiGraph(type='citations')

    # Check node_id validity.
    meta_dict = Paper()
    meta_keys = meta_dict.keys()
    if node_id not in meta_keys:
        raise KeyError('node_id:' + node_id + 'is not in the set of' +
                       'meta_keys')

    for entry in papers:
        # Check the head.
        head_has_id = True
        if entry[node_id] is None:
            head_has_id = False

        if head_has_id:
            # Then create node to both global and internal networks.
            node_attrib_dict = util.subdict(entry, node_attribs)
            citation_network.add_node(entry[node_id], node_attrib_dict)
            citation_network_internal.add_node(entry[node_id],
                                               node_attrib_dict)
        if entry['citations'] is not None:
            for citation in entry['citations']:
                # Check the tail.
                tail_has_id = True
                if citation[node_id] is None:
                    tail_has_id = False

                if tail_has_id:
                    # Then create node to global but not internal network.
                    node_attrib_dict = util.subdict(citation, node_attribs)
                    citation_network.add_node(citation[node_id],
                                              node_attrib_dict)

                if head_has_id and tail_has_id:
                    # Then draw an edge in the network.
                    citation_network.add_edge(entry[node_id],
                                              citation[node_id],
                                              date=entry['date'])

                    # And check if it can be added to the internal network, too.
                    if (util.contains (papers,
                                       lambda wos_obj:
                                       wos_obj[node_id] == citation[node_id])):
                        citation_network_internal.add_edge(
                            entry[node_id],
                            citation[node_id],
                            date=entry['date'])

    # Checking if both the graphs are Directed Acyclic Graphs.
    if not nx.is_directed_acyclic_graph(citation_network):
        raise nx.NetworkXError("Citation graph is not a DAG.")
    elif not nx.is_directed_acyclic_graph(citation_network_internal):
        raise nx.NetworkXError("Internal citation graph is not a DAG.")
    else:
        return citation_network, citation_network_internal

def bibliographic_coupling(papers, citation_id='ayjid', threshold=1,
                           node_id='ayjid', node_attribs=['date'],
                           weighted=False, **kwargs):
    """
    Generate a bibliographic coupling network.

    Two papers are **bibliographically coupled** when they both cite the same,
    third, paper. You can generate a bibliographic coupling network using the
    :func:`.networks.papers.bibliographic_coupling` method.

    .. code-block:: python

       >>> BC = nt.papers.bibliographic_coupling(papers)
       >>> BC
       <networkx.classes.graph.Graph object at 0x102eec710>

    Especially when working with large datasets, or disciplinarily narrow
    literatures, it is usually helpful to set a minimum number of shared
    citations required for two papers to be coupled. You can do this by setting
    the **`threshold`** parameter.

    .. code-block:: python

       >>> BC = nt.papers.bibliographic_coupling(papers, threshold=1)
       >>> len(BC.edges())
       1216
       >>> BC = nt.papers.bibliographic_coupling(papers, threshold=2)
       >>> len(BC.edges())
       542

    ===============    =========================================================
    Element            Description
    ===============    =========================================================
    Node               Papers represented by node_id.
    Node Attributes    node_attribs in :class:`.Paper`
    Edge               (a,b) in E(G) if a and b share x citations where x >=
                       threshold.
    Edge Attributes    overlap: the number of citations shared
    ===============    =========================================================


    Parameters
    ----------
    papers : list
        A list of wos_objects.
    citation_id: string
        A key from :class:`.Paper` to identify the citation overlaps.  Default
        is 'ayjid'.
    threshold : int
        Minimum number of shared citations to consider two papers "coupled".
    node_id : string
        Field in :class:`.Paper` used to identify the nodes. Default is 'ayjid'.
    node_attribs : list
        List of fields in :class:`.Paper` to include as node attributes in
        graph.
    weighted : bool
        If True, edge attribute `overlap` is a float in {0-1} calculated as
        :math:`\cfrac{N_{ij}}{\sqrt{N_{i}N_{j}}}` where :math:`N_{i}` and
        :math:`N_{j}` are the number of references in :class:`.Paper` *i* and
        *j*, respectively, and :math:`N_{ij}` is the number of references
        shared by papers *i* and *j*.

    Returns
    -------
    bcoupling : networkx.Graph
        A bibliographic coupling network.

    Raises
    ------
    KeyError : Raised when citation_id is not present in the meta_list.

    Notes
    -----
    Lists cannot be attributes? causing errors for both gexf and graphml also
    nodes cannot be none.
    """

    bcoupling = nx.Graph(type='biblio_coupling')
    nattr = {}

    # Validate identifiers.
    meta_dict = Paper()
    meta_keys = meta_dict.keys()
    if node_id not in meta_keys:
        raise KeyError('node_id' + node_id + ' is not a meta_dict key.')

    # 'citations' is the only invalid meta_key for citation_id
    meta_keys.remove('citations')
    if citation_id not in meta_keys:
        raise KeyError('citation_id' + citation_id + ' is not a meta_dict' +
                       ' key or otherwise cannot be used to detect citation' +
                       ' overlap.')

    for i in xrange(len(papers)):
        # Make a list of citation_id's for each paper...
        i_list = []
        if papers[i]['citations'] is not None:
            for citation in papers[i]['citations']:
                i_list.append(citation[citation_id])

        # ...and construct that paper's node.
        node_i_attribs = util.subdict(papers[i], node_attribs)

        for j in xrange(i+1, len(papers)):
            # Make a list of citation_id's for each paper...
            j_list = []
            if papers[j]['citations'] is not None:
                for citation in papers[j]['citations']:
                    j_list.append(citation[citation_id])

            # ...and construct that paper's node.
            node_j_attribs = util.subdict(papers[j], node_attribs)

            # Add nodes and edge if the citation overlap is sufficiently high.
            overlap = util.overlap(i_list, j_list)

            if weighted:
                if len(overlap) > 0:
                    w = (float(len(i_list)) * float(len(j_list)))**0.5
                    similarity = float(len(overlap)) / w
                else:
                    similarity = 0
            else:
                similarity = len(overlap)

            
            if similarity >= threshold:
                nattr[papers[i][node_id]] = node_i_attribs
                nattr[papers[j][node_id]] = node_j_attribs
                #nx.set_node_attributes(bcoupling,"",node_i_attribs)

                bcoupling.add_edge(papers[i][node_id],
                                   papers[j][node_id],
                                   similarity=similarity)
                                   
        # Set node attributes.
        node_attributes = {}
        for k, v in nattr.iteritems():
            for vk, vv in v.iteritems():
                try:
                    node_attributes[vk][k] = vv
                except KeyError:
                    node_attributes[vk] = {k:vv}
                    
        for k, v in node_attributes.iteritems():
            nx.set_node_attributes(bcoupling, k, v)
        
    return bcoupling

def cocitation(papers, threshold=1, node_id='ayjid', topn=None, verbose=False,\
                node_attribs=['date'], **kwargs):
    """
    Generate a cocitation network.

    A **cocitation network** is a network in which vertices are papers, and
    edges indicate that two papers were cited by the same third paper.
    `CiteSpace <http://cluster.cis.drexel.edu/~cchen/citespace/doc/jasist2006.pdf>`_
    is a popular desktop application for co-citation analysis, and you can read
    about the theory behind it
    `here <http://cluster.cis.drexel.edu/~cchen/citespace/>`_. Co-citation
    analysis is generally performed with a temporal component, so building a
    :class:`.GraphCollection` from a :class`.Corpus` sliced by ``date``
    is recommended.

    You can generate a co-citation network using the
    :func:`.networks.papers.cocitation` method:

    .. code-block:: python

       >>> CC = nt.papers.cocitation(papers)
       >>> CC
       <networkx.classes.graph.Graph object at 0x102eec790>

    For large datasets, you may wish to set a minimum number of co-citations
    required for an edge between two papers Keep in mind that all of the
    references in a single paper are co-cited once, so a threshold of at least
    2 is prudent. Note the dramatic decrease in the number of edges when the
    threshold is changed from 2 to 3.

    .. code-block:: python

       >>> CC = nt.papers.cocitation(papers, threshold=2)
       >>> len(CC.edges())
       8889
       >>> CC = nt.papers.cocitation(papers, threshold=3)
       >>> len(CC.edges())
       1493

    ===============    =========================================================
    Element            Description
    ===============    =========================================================
    Node               Cited papers represented by :class:`.Paper` ayjid.
    Edge               (a, b) if a and b are cited by the same paper.
    Edge Attributes    weight: number of times two papers are co-cited
                       together.
    ===============    =========================================================

    Parameters
    ----------
    papers : list
        a list of :class:`.Paper` objects.
    threshold : int
        Minimum number of co-citations required to create an edge.
    topn : int or float, or None
        If provided, only the topn (int) or topn percent (float) most cited
        papers will be included in the cocitation network. If None (default),
        network will include all cited papers (NOTE: this can cause severe
        memory consumption for even moderately-sized datasets).
    verbose : bool
        If True, prints status messages.

    Returns
    -------
    cocitation : networkx.Graph
        A cocitation network.

    """

    cocitation_graph = nx.Graph(type='cocitation')

    if verbose:
        print "Generating a cocitation network with " + str(N) + " nodes..."

    counts = helpers.citation_count(papers, key=node_id)

    # 61670334: networks.citations.cocitation should have a "top cited"
    #  parameter.
    if topn is not None:
        cvalues = numpy.array(counts.values())
        if type(topn) is int:
            top_values = cvalues.argsort()[-topn:][::-1]
        if type(topn) is float:
            topn_ = round(topn * float(len(counts)))
            top_values = cvalues.argsort()[-topn_:][::-1]
        top_cited = set([ counts.keys()[i] for i in top_values ])

    cocited = Counter()
    for paper in papers:
        try:
            these_citations = set( [ c[node_id] for c in paper['citations'] ] )
            if topn is not None:
                allowed = list(these_citations & top_cited)
            else:
                allowed = list(these_citations)
            
            n = len(allowed)
            for i in xrange(n):
                i_id = allowed[i]
                if topn is not None:
                    if i_id not in top_cited:
                        continue

                for j in xrange(i+1,n):
                    j_id = allowed[j]
                    if topn is not None:
                        if j_id not in top_cited:
                            continue

                    pair = sorted([i_id, j_id])
                    pair_key = '|||'.join(pair)
                    cocited[pair_key] += 1
        except TypeError:   # Raised when a paper has no citations.
            pass

    if verbose:
        print "Co-citation matrix generated, building Graph..."

    for pairkey, val in cocited.iteritems():
        if val >= threshold: # and key[0] in include and key[1] in include:
            pair = pairkey.split('|||')
            cocitation_graph.add_edge(pair[0], pair[1], weight=val)

    if verbose:
        print "Done building co-citation graph, adding attributes..."

    # 62657522: Nodes in co-citation graph should have attribute containing
    #  number of citations.
    cts = { k:v for k,v in counts.iteritems() if k in cocitation_graph.nodes() }
    nx.set_node_attributes( cocitation_graph, 'citations', cts )

    return cocitation_graph

def author_coupling(papers, threshold=1, node_attribs=['date'],
                                                     node_id='ayjid', **kwargs):
    """
    Vertices are papers and edges indicates shared authorship.

    ===============    =========================================================
    Element            Description
    ===============    =========================================================
    Node               Papers, represented by node_id.
    Edge               (a,b) in E(G) if a and b share x authors and x >=
                       threshold
    Edge Attributes    overlap: the value of x (above).
    ===============    =========================================================

    Parameters
    ----------
    papers : list
        A list of :class:`.Paper`
    threshold : int
        Minimum number of co-citations required to draw an edge between two
        authors.
    node_id : string
        Field in :class:`.Paper` used to identify nodes.
    node_attribs : list
        List of fields in :class:`.Paper` to include as node attributes in
        graph.

    Returns
    -------
    acoupling : networkx.Graph
        An author-coupling network.

    """
    acoupling = nx.Graph(type='author_coupling')

    for i in xrange(len(papers)):
        #define last name first initial name lists for each paper
        name_list_i = util.concat_list(papers[i]['aulast'],
                                       papers[i]['auinit'],
                                       ' ')

        #create nodes
        node_attrib_dict = util.subdict(papers[i], node_attribs)

        acoupling.add_node(papers[i][node_id], node_attrib_dict)

        for j in xrange(i+1, len(papers)):
            #define last name first initial name lists for each paper
            name_list_j = util.concat_list(papers[j]['aulast'],
                                           papers[j]['auinit'],
                                           ' ')

            #create nodes
            node_attrib_dict = util.subdict(papers[j], node_attribs)
            acoupling.add_node(papers[j][node_id], node_attrib_dict)

            #draw edges as appropriate
            overlap = util.overlap(name_list_i, name_list_j)

            if len(overlap) >= threshold:
                acoupling.add_edge(papers[i][node_id],
                                   papers[j][node_id],
                                   overlap=len(overlap))
    return acoupling

def topic_coupling(papers, threshold=0.7, node_id='ayjid', **kwargs):
    """
    Two papers are coupled if they both contain a shared topic above threshold.

    ===============    =========================================================
    Element            Description
    ===============    =========================================================
    Node               Papers, represented by node_id.
    Edge               (a,b) in E(G) if a and b share >= 1 topics with
                       proportion >= threshold in both a and b.
    Edge Attributes    weight: combined mean proportion of each shared topic.
                       topics: list of shared topics.
    ===============    =========================================================

    Parameters
    ----------
    papers : list
        A list of :class:`.Paper`
    threshold : float
        Minimum representation of a topic in each paper.
    node_id : string
        Field in :class:`.Paper` used to identify nodes.

    Returns
    -------
    tc : networkx.Graph
        A topic-coupling network.
    """
    for i in xrange(len(papers)):
        t_i = papers[i]['topics'][0]    # Topic vector for i.
        for j in xrange(i+1,len(papers)):
            t_j = papers[i]['topics'][0]    # Topic vector for j.

            Z = t_i.shape[0]
            for z in xrange(Z):
                if t_i[z] >= threshold and t_j[z] >= threshold:
                    try:  # Add topic and mean of representation in i and j.
                        edges[(i,j)].append( (z,(t_i[z]+t_j[z])/2) )
                    except KeyError:
                        edges[(i,j)] = [ (z,(t_i[z]+t_j[z])/2) ]

    tc = nx.Graph()

    # Combine means of representations into a single edge weight in {0-1}.
    for e, topics in edges.iteritems():
        weight = sum([ t[1] for t in topics ] ) / t_i.shape[0]
        i_id = papers[e[0]][node_id]
        j_id = papers[e[1]][node_id]
        tc.add_edge(i_id, j_id, weight=weight, topics=[t[0] for t in topics])

    return tc
