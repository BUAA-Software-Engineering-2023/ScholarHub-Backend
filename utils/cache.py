from django.core.cache import cache
import json


def set_verification_code_cache(email, code):
    key = f'verification_code_{email}'
    cache.set(key, code, 30 * 60)


def get_verification_code_cache(email):
    key = f'verification_code_{email}'
    code = cache.get(key)
    return code


def delete_verification_code_cache(email):
    key = f'verification_code_{email}'
    cache.delete(key)


def get_openalex_entities_key(
        type: str, search: str, position: str = 'default',
        filter: dict = None, sort: dict = None,
        page: int = 0, size: int = 25
):
    if not position:
        position = 'default'
    if not filter:
        filter = {}
    if not sort:
        sort = {}
    return json.dumps({
        'type': type,
        'search': search,
        'position': position,
        'filter': filter,
        'sort': sort,
        'page': page,
        'size': size
    })


def get_openalex_entities_cache(*args, **kwargs):
    key = get_openalex_entities_key(*args, **kwargs)
    return cache.get(key)


def set_openalex_entities_cache(result: dict, *args, **kwargs):
    key = get_openalex_entities_key(*args, **kwargs)
    return cache.set(key, result)


def get_openalex_single_entity_cache(type, id):
    key = f'openalex_{type}_{id}'
    return cache.get(key)


def set_openalex_single_entity_cache(value, type, id):
    key = f'openalex_{type}_{id}'
    return cache.set(key, value)


def get_openalex_entities_ids_cache(type, search):
    key = f'openalex_ids_{type}_{search}'
    return cache.get(key)


def set_openalex_entities_ids_cache(value, type, search):
    key = f'openalex_ids_{type}_{search}'
    return cache.set(key, value)


def get_openalex_entities_numbers_cache():
    key = 'openalex_entities_numbers'
    return cache.get(key)


def set_openalex_entities_numbers_cache(value):
    key = 'openalex_entities_numbers'
    return cache.set(key, value, 60 * 60 * 24)


def get_openalex_recommendations_cache(history):
    key = f'openalex_history_{history}'
    return cache.get(key)


def set_openalex_recommendations_cache(value, history, ttl=60 * 60 * 24):
    key = f'openalex_history_{history}'
    return cache.set(key, value, ttl)


def get_openalex_autocomplete_cache(type, search):
    key = f'openalex_autocomplete_{type}_{search}'
    return cache.get(key)


def set_openalex_autocomplete_cache(value, type, search):
    key = f'openalex_autocomplete_{type}_{search}'
    return cache.set(key, value)


def get_comment_cache(work_id):
    key = f'comment_{work_id}'
    return cache.get(key)


def set_comment_cache(work_id, result):
    key = f'comment_{work_id}'
    return cache.set(key, result)


def clear_comment_cache(work_id):
    key = f'comment_{work_id}'
    return cache.delete(key)


def get_question_cache():
    key = 'question'
    return cache.get(key)


def set_question_cache(result):
    key = 'question'
    return cache.set(key, result)


def clear_question_cache():
    key = 'question'
    return cache.delete(key)


def get_answer_cache(question_id):
    key = f'answer_{question_id}'
    return cache.get(key)


def set_answer_cache(question_id, result):
    key = f'answer_{question_id}'
    return cache.set(key, result)


def clear_answer_cache(question_id):
    key = f'answer_{question_id}'
    return cache.delete(key)
