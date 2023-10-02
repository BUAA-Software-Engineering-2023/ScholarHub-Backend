from django.core.cache import cache
import json


def set_verification_code_cache(email, code):
    key = f'verification_code_{email}'
    cache.set(key, code, 30 * 60)


def get_verification_code_cache(email):
    key = f'verification_code_{email}'
    code = cache.get(key)
    cache.delete(key)
    return code


def get_openalex_entities_key(
        type: str, search: str, filter: dict = None,
        sort: dict = None, page: int = 0, size: int = 25
):
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
