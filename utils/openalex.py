from pyalex import Works
from .cache import get_openalex_entities_cache, set_openalex_entities_cache

def search_works(search:str, filter:dict=None, sort:dict=None):
    if filter is None:
        filter = {}
    if sort is None:
        sort = {}
    result = get_openalex_entities_cache('work', search, filter, sort)
    if result is None:
        result = Works().search(search).filter(**filter).sort(**sort).get()
        set_openalex_entities_cache(result, 'work', search, filter, sort)
    return result