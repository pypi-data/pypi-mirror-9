# -*- coding: utf-8 -*-

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import os
import logging
from whoosh import index
from whoosh.fields import *
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh.analysis import StandardAnalyzer, CharsetFilter
from whoosh.support.charset import accent_map
from . import extractor


logger = logging.getLogger(__name__)


class DocumentIndexer(object):
    
    def __init__(self, dir='index/'):
        self.dir = dir
        self.init_indexer()
        # Accent folding
        self.analyzer = StandardAnalyzer() | CharsetFilter(accent_map)
    
    def schema(self):
        return Schema(
            id=ID(unique=True, stored=True),
            filename=TEXT(stored=True),
            size=NUMERIC(stored=True),
            type=TEXT(stored=True),
            content=TEXT(stored=False, analyzer=self.analyzer),
        )

    def init_indexer(self):
        if index.exists_in(self.dir):
            logger.info("Opening existing index storage in %s", self.dir)
            self.ix = index.open_dir(self.dir)
        else:
            logger.info("Creating new index storage in %s", self.dir)
            if not os.path.exists(self.dir):
                os.mkdir(self.dir)
            self.ix = index.create_in(self.dir, self.schema())
        logger.info("Indexer initialized: %s", self.ix)
    
    def index_documents(self, documents):
        logger.info("Indexing %d document(s)...", len(documents))
        with self.ix.writer() as writer:
            for i, document in enumerate(documents, 1):
                logger.debug("[%d/%d] Indexing '%s'", i,
                    len(documents), document['id'])
                writer.update_document(**document)
            logger.info("Commiting changes...")
        logger.info("Committed.")

    def index_document(self, **document):
        self.index_documents([document])

    def index_str_document(self, id, content, filename, size, type):
        self.index_document(id=id, filename=filename, size=size, type=type,
            content=content)

    def index_bin_document(self, id, bindata, filename, size=None, type=None):
        content = extractor.get_content(bindata, filename)
        self.index_str_document(id, content, filename, size, type)

    def optimize(self):
        logger.info("Optimizing index...")
        self.ix.optimize()

    def find(self, term):
        logger.debug("Opening index..")
        ix = index.open_dir(self.dir)
        logger.debug("Opening searcher...")
        with ix.searcher() as searcher:
            logger.debug("Parsing query '%s'", term)
            query = QueryParser("content", ix.schema).parse(term)
            logger.info("Searching for: %s", query)
            results = searcher.search(query, limit=500)
            logger.info("Results: %s", results)
            #return [result['path'] for result in results]
            return map(dict, results)

