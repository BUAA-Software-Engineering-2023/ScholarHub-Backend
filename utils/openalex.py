from pyalex import Works
from .cache import get_openalex_entities_cache, set_openalex_entities_cache

def search_works(search:str, filter:dict=None, sort:dict=None, page:int=1, size:int=25):
    if filter is None:
        filter = {}
    if sort is None:
        sort = {}
    result = get_openalex_entities_cache('work', search, filter, sort, page, size)
    if result is None:
        result,meta = Works().search(search).filter(**filter).sort(**sort).get(return_meta=True, page=page, per_page=size)
        for r in result:
            if r.get('abstract_inverted_index') is not None:
                r['abstract'] = r['abstract']
                del r['abstract_inverted_index']
            else:
                r['abstract'] = ''
        result = {
            'total': meta['count'],
            'page': meta['page'],
            'size': meta['per_page'],
            'result': result
        }
        set_openalex_entities_cache(result, 'work', search, filter, sort, page, size)
    return result
