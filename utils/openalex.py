import random
from typing import Optional

from pyalex import Works, Authors, Sources, Institutions, Concepts, Publishers, Funders
from pyalex.api import QueryError
from requests import HTTPError
import requests

from .cache import *

entities = {
    'work': Works,
    'author': Authors,
    'source': Sources,
    'institution': Institutions,
    'concept': Concepts,
    'publisher': Publishers,
    'funder': Funders
}

entities_fields = {
    'work': ['id', 'display_name', 'publication_year',
             'publication_date', 'language', 'type',
             'abstract_inverted_index', 'authorships',
             'concepts', 'cited_by_count'],
    'author': ['id', 'display_name', 'works_count',
               'cited_by_count', 'x_concepts',
               'last_known_institution', 'summary_stats'],
    'source': ['id', 'display_name', 'country_code', 'type'],
    'institution': ['id', 'display_name', 'country_code', 'type',
                    'image_url', 'international', 'x_concepts'],
    'concept': ['id', 'display_name', 'international'],
    'publisher': ['id', 'display_name', 'alternate_titles',
                  'country_codes', 'image_url'],
    'funder': ['id', 'display_name', 'alternate_titles',
               'country_code', 'description', 'image_url']
}


def get_entities_ids(type: str, search: str):
    result = get_openalex_entities_ids_cache(type, search)
    if result is None:
        try:
            result = entities[type]().search(search).select(['id']).get(per_page=10)
        except QueryError as e:
            return e.args[0], False
        except HTTPError as e:
            if e.response.status_code == 404:
                return '不存在对应id的实体', False
            print(e.args)
            return 'OpenAlex请求出错', False
        except Exception as e:
            print(e.args)
            return '未知错误', False
        for i in range(len(result)):
            result[i] = result[i]['id']
        set_openalex_entities_ids_cache(result, type, search)
    return result, True


def search_entities(type: str, search: str, position: str = 'default', filter: dict = None, sort: dict = None,
                    page: int = 1, size: int = 25):
    if not position:
        position = 'default'
    if not filter:
        filter = {}
    if not sort:
        sort = {}
    result = get_openalex_entities_cache(type, search, position, filter, sort, page, size)
    if result is None:
        temp = filter.copy()
        # 特殊处理filter中的作者名authorships.author.display_name
        if 'authorships.author.display_name' in filter:
            ids, success = get_entities_ids('author', filter['authorships.author.display_name'])
            if not success:
                return ids, success
            filter['authorships.author.id'] = '|'.join(ids)
            del filter['authorships.author.display_name']
        # 特殊处理filter中的机构名authorships.institutions.display_name
        if 'authorships.institutions.display_name' in filter:
            ids, success = get_entities_ids('institution', filter['authorships.institutions.display_name'])
            if not success:
                return ids, success
            filter['authorships.institutions.id'] = '|'.join(ids)
            del filter['authorships.institutions.display_name']
        # 特殊处理filter中的主题名concepts.display_name
        if 'concepts.display_name' in filter:
            ids, success = get_entities_ids('concept', filter['concepts.display_name'])
            if not success:
                return ids, success
            filter['concepts.id'] = '|'.join(ids)
            del filter['concepts.display_name']
        # 特殊处理filter中的机构名last_known_institution.display_name
        if 'last_known_institution.display_name' in filter:
            ids, success = get_entities_ids('institution', filter['last_known_institution.display_name'])
            if not success:
                return ids, success
            filter['last_known_institution.id'] = '|'.join(ids)
            del filter['last_known_institution.display_name']
        # 特殊处理filter中的主题名x_concepts.display_name
        if 'x_concepts.display_name' in filter:
            ids, success = get_entities_ids('concept', filter['x_concepts.display_name'])
            if not success:
                return ids, success
            filter['x_concepts.id'] = '|'.join(ids)
            del filter['x_concepts.display_name']
        # 特殊处理filter中的主题名ancestors.display_name
        if 'ancestors.display_name' in filter:
            ids, success = get_entities_ids('concept', filter['ancestors.display_name'])
            if not success:
                return ids, success
            filter['ancestors.id'] = '|'.join(ids)
            del filter['ancestors.display_name']

        try:
            result, meta = entities[type]().search_filter(**{position: search}) \
                .filter(**filter).sort(**sort).select(entities_fields[type]) \
                .get(return_meta=True, page=page, per_page=size)
        except QueryError as e:
            return e.args[0], False
        except HTTPError as e:
            if e.response.status_code == 404:
                return '不存在对应id的实体', False
            print(e.args)
            return 'OpenAlex请求出错', False
        except Exception as e:
            print(e.args)
            return '未知错误', False
        if type == 'work':
            for r in result:
                r['abstract'] = r['abstract']
                del r['abstract_inverted_index']
        result = {
            'total': meta['count'],
            'page': meta['page'],
            'size': meta['per_page'],
            'result': result
        }
        set_openalex_entities_cache(result, type, search, position, temp, sort, page, size)
    return result, True


def search_entities_by_body(type: str, data: dict):
    """
    根据请求体参数搜索entities
    :param type: entities类别
    :param data: 转为字典的请求体
    :return:
    """
    search = data.get('search', '')
    position = data.get('position', 'default')
    filter = data.get('filter', {})
    sort = data.get('sort', {})
    page = int(data.get('page', 1))
    size = int(data.get('size', 25))

    temp = filter.copy()
    for key, value in temp.items():
        if not value:
            filter.pop(key)
        if isinstance(value, list):
            filter[key] = '|'.join(value)
    temp = sort.copy()
    for key, value in temp.items():
        if not value:
            sort.pop(key)
    result = search_entities(type, search, position, filter, sort, page, size)
    return result


def search_works_by_author_id(id, page=None, size=25, return_meta=True):
    if page is None:
        page = 1
        return_meta = False
    meta = None
    try:
        if return_meta:
            result, meta = Works().filter(author={"id": id}) \
                .select(entities_fields['work']) \
                .get(return_meta=True, page=page, per_page=size)
        else:
            result = Works().filter(author={"id": id}) \
                .select(entities_fields['work']) \
                .get(return_meta=False, page=page, per_page=size)
    except Exception as e:
        print(e.args)
        return None
    for r in result:
        r['abstract'] = r['abstract']
        del r['abstract_inverted_index']
    if return_meta:
        return {
            'total': meta['count'],
            'page': meta['page'],
            'size': meta['per_page'],
            'result': result
        }
    return result


def calculate_collaborators(works: list, id: str):
    """
    根据指定作者的所有论文计算所有合作者信息
    :param works: 作者的所有论文
    :param id: 作者的id
    :return: 作者的所有合作者
    """
    collaborators = {}
    for work in works:
        for author in work['authorships']:
            author = author['author']
            if author['id'] == id:
                continue
            if author['id'] not in collaborators.keys():
                author['cooperation_times'] = 0
                author['collaborative_works'] = []
                collaborators[author['id']] = author
            collaborators[author['id']]['cooperation_times'] += 1
            collaborators[author['id']]['collaborative_works'].append({
                'id': work['id'],
                'display_name': work['display_name']
            })
    collaborators = sorted(collaborators.values(),
                           key=lambda x: x['cooperation_times'],
                           reverse=True)
    return collaborators


def get_single_entity(type: str, id: str):
    result = get_openalex_single_entity_cache(type, id)
    if result is None:
        try:
            result = entities[type]()[id]
        except QueryError as e:
            return e.args[0], False
        except HTTPError as e:
            if e.response.status_code == 404:
                return '不存在对应id的实体', False
            print(e.args)
            return 'OpenAlex请求出错', False
        except Exception as e:
            print(e.args)
            return '未知错误', False
        if type == 'work':
            result['abstract'] = result['abstract']
            del result['abstract_inverted_index']

            result['referenced_works'] = Works(
                {'select': ['id', 'display_name', 'publication_year',
                            'authorships', 'type']}
            )[result['referenced_works'][0:20]]
            result['related_works'] = Works(
                {'select': ['id', 'display_name', 'publication_year',
                            'authorships', 'type']}
            )[result['related_works'][0:20]]

        if type == 'author':
            result['works'] = search_works_by_author_id(id)
            result['collaborators'] = calculate_collaborators(result['works'], id)

        set_openalex_single_entity_cache(result, type, id)

    return result, True


def get_histories_details(works, user_id):
    result = get_openalex_histories_details_cache(user_id)
    if result is None:
        try:
            histories_details = Works({'select': ['id', 'display_name', 'publication_year',
                                                  'authorships', 'type', 'concepts', 'cited_by_count']})[works]
        except QueryError as e:
            return e.args[0], False
        except HTTPError as e:
            if e.response.status_code == 404:
                return '不存在对应id的实体', False
            print(e.args)
            return 'OpenAlex请求出错', False
        except Exception as e:
            print(e.args)
            return '未知错误', False
        result = {history_detail['id']: {key: value for key, value in history_detail.items() if key != 'id'} for
                  history_detail in histories_details}
        set_openalex_histories_details_cache(result, user_id)
    return result


def get_entities_numbers():
    result = get_openalex_entities_numbers_cache()
    if not result:
        result = {}
        for type in entities.keys():
            result[f'{type}_count'] = entities[type]().count()
        set_openalex_entities_numbers_cache(result)
    return result


def get_recommendations(history: list):
    """
    根据浏览历史获取推荐，主要逻辑是获取最近浏览的10篇论文的相关论文，
    随机选取10篇作为推荐
    :param history: 浏览历史
    :return:
    """
    if not history:
        # 没有历史记录不进行推荐
        return None
    # 保留副本
    origin = history.copy()
    # 根据最近浏览的10篇推荐
    history = history[:10]
    # 按id排序
    history = sorted(history, key=lambda x: x)
    result = get_openalex_recommendations_cache(history)
    if not result:
        # 获取相关论文的id
        related_works = Works({'select': ['related_works']})[history]

        total = set()
        for related_work in related_works:
            total.update(related_work['related_works'])
        # 排除浏览过的论文
        total = total - set(origin)

        # 获取引用量最高的10篇
        related_works = Works({'select': [
            'id', 'display_name', 'publication_year',
            'authorships', 'concepts', 'cited_by_count'
        ], 'sort': {'cited_by_count': 'desc'}})[list(total)]
        result = list(set(related_works))[:10]

        # 获取最新的10篇
        related_works = Works({'select': [
            'id', 'display_name', 'publication_year',
            'authorships', 'concepts', 'cited_by_count'
        ], 'sort': {'publication_date': 'desc'}})[list(total)]
        result += list(set(related_works))[:10]

        # 随机选取10篇
        result = random.choices(result, k=10)
        # 加入缓存
        set_openalex_recommendations_cache(result, history)
    return result


def autocomplete(type: str, search: str):
    result = get_openalex_autocomplete_cache(type, search)
    if not result:
        url = f'https://api.openalex.org/autocomplete/{type}s?q={search}'
        try:
            result = requests.get(url)
        except HTTPError:
            return []
        if result.status_code != 200:
            return []
        result = result.json()['results']
        set_openalex_autocomplete_cache(result, type, search)
    return result
