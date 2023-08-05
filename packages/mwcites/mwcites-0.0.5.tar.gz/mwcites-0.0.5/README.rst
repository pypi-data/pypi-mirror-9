Extract academic citaitons from Wikipedia
=========================================
This project contains a utility for extracting academic citation identifiers.

``pip install mwcites``

Usage
-----
There's really only one utility in this package called ``extract_cites``.

::

    $ extract_cites enwiki-20150112-pages-meta-history*.xml*.bz2 > citations.tsv


Documentation
-------------
Documentation is provided ``$ mwcites extract -h``.

::

    Extracts academic citations from articles from the history of Wikipedia
    articles by processing a pages-meta-history XML dump and matching regular
    expressions to revision content.

    Currently supported identifies include:

     * PubMed
     * DOI
     
    Outputs a TSV file with the following fields:

     * page_id: The identifier of the Wikipedia article (int), e.g. 1325125
     * page_title: The title of the Wikipedia article (utf-8), e.g. Club cell
     * rev_id: The Wikipedia revision where the citation was first added (int),
               e.g. 282470030
     * timestamp: The timestamp of the revision where the citation was first added.
                  (ISO 8601 datetime), e.g. 2009-04-08T01:52:20Z
     * type: The type of identifier, e.g. pmid
     * id: The id of the cited scholarly article (utf-8),
           e.g 10.1183/09031936.00213411

    Usage:
        mwcites extract -h | --help
        mwcites extract <dump_file>...

    Options:
        -h --help        Shows this documentation
