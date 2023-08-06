"""
Gathers (looks up) metadata for citations based on type.


Usage:
    lookup -h | --help
    lookup [--metadata-cache=<path>] [--max-cache-size=<val>]

Options:
    -h --help                Print this documentation
    --metadata-cache=<path>  The location of a file containing cached metadata
                             [default: ./cache.tsv]
    --max-cache-size=<val>   The maximum number of entries to keep in the cache
                             [default: 2000000]
"""
'''
import sys
from functools import lru_cache

import docopt

from ..sources import doi, pubmed

ALL_SOURCES = {
    'doi': doi.lookup,
    'pmid': pubmed.lookup,
    'pcmid': pubmed.lookup
}


def main(argv=sys.argv):
    args = docopt.docopt(__doc__, argv=argv)
    

def run(cites, sources, max_cache_size=2000000, metadata_cache):
    
    for cite, metadata in lookup(cites, sources, max_cache_size, metadata_cache):
        
        print("\t".join(encode(v) for v in cite + [json.dumps(metadata)]))
        

def lookup(cites, sources, max_cache_size, metadata_cache):
    
    def get_metadata(identifier):
        
        if identifier not in metadata_cache:
            metadata = sources[identifier.type].lookup(identifier)
            metadata_cache[identifier] = metadata
        
        return metadata_cache[identifier]
    
    for cite in cites:
        type, id = cite[4:6]
        identifier = Identifier(type, id)
        
        metadata = get_metadata(identifier)
        return cite, metadata


class MetadataCache(OrderedDict):
    
    def __init__(self, *args, **kwargs):
        self.maxsize = kwargs.pop("maxsize", None)
        OrderedDict.__init__(self, *args, **kwargs)
        self._check_size_limit()
    
    def __setitem__(self, key, value):
        OrderedDict.__setitem__(self, key, value)
        self._check_size_limit()
    
    def update(self, other):
        raise NotImplementedError()
    
    def _check_size_limit(self):
        if self.maxsize is not None:
            while len(self) > self.maxsize:
                self.popitem(last=False)
            
    
    def load(self, f):
        
        for line in f:
            type, id, metadata = line.rstrip().split("\t")
            type, id, metadata = str(type), str(id), json.loads(metadata)
            
            identifier = Identifier(type, id)
            self[identifier] = metadata
            
    
    
    def dump(self, f):
        
        for identifier, metadata in self.items():
            
            line = "\t".join([identifier.type,
                              identifier.id,
                              json.dumps(metadata)])
            f.write(line + "\n")
'''
