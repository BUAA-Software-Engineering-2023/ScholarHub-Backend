from django.core.cache import cache
import json

def set_verification_code_cache(email, code):
    key = f'verification_code_{email}'
    cache.set(key, code, 30*60)

def get_verification_code_cache(email):
    key = f'verification_code_{email}'
    code = cache.get(key)
    cache.delete(key)
    return code

def get_openalex_entities_key(type:str, search:str, filter:dict=None, sort:dict=None):
    if filter is None:
        filter = {}
    if sort is None:
        sort = {}
    for key, value in filter.items():
        if not value:
            filter.pop(key)
    for key, value in sort.items():
        if not value:
            sort.pop(key)
    return json.dumps({
        'type': type,
        'search': search,
        'filter': filter,
        'sort': sort
    })

def get_openalex_entities_cache(type:str, search:str, filter:dict=None, sort:dict=None):
    key = get_openalex_entities_key(type, search, filter, sort)
    return cache.get(key)

def set_openalex_entities_cache(result:dict, type:str, search:str, filter:dict=None, sort:dict=None):
    key = get_openalex_entities_key(type, search, filter, sort)
    return cache.set(key, result)