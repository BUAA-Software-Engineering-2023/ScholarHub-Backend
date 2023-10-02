from pyalex import Works, Authors, Sources, Institutions, Concepts, Publishers, Funders
from .cache import get_openalex_entities_cache, set_openalex_entities_cache

entities = {
    'work': Works,
    'author': Authors,
    'source': Sources,
    'institution': Institutions,
    'concept': Concepts,
    'publisher': Publishers,
    'funder': Funders
}

def search_entities(type:str, search: str, filter: dict = None, sort: dict = None, page: int = 1, size: int = 25):
    if filter is None:
        filter = {}
    if sort is None:
        sort = {}
    result = get_openalex_entities_cache(type, search, filter, sort, page, size)
    if result is None:
        result, meta = (entities[type]().search(search)
                        .filter(**filter).sort(**sort)
                        .get(return_meta=True, page=page, per_page=size))
        if type == 'work':
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
        set_openalex_entities_cache(result, type, search, filter, sort, page, size)
    return result

def search_entities_by_body(type:str, data:dict):
    """
    根据请求体参数搜索entities
    :param type: entities类别
    :param data: 转为字典的请求体
    :return:
    """
    search = data.get('search', '')
    filter = data.get('filter')
    sort = data.get('sort')
    page = int(data.get('page', 1))
    size = int(data.get('size', 25))
    result = search_entities(type, search, filter, sort, page, size)
    return result

def search_works_by_author_id(id:str):
    try:
        result, meta = Works().filter(author={"id": id}).get(return_meta=True)
        for r in result:
            if r.get('abstract_inverted_index') is not None:
                r['abstract'] = r['abstract']
                del r['abstract_inverted_index']
            else:
                r['abstract'] = ''
    except:
        return None
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


def get_single_entity(type:str, id: str):
    try:
        result = entities[type]()[id]
    except:
        return None
    if type == 'work':
        if result.get('abstract_inverted_index') is not None:
            result['abstract'] = result['abstract']
            del result['abstract_inverted_index']
        else:
            result['abstract'] = ''
    if type == 'author':
        result['works'] = search_works_by_author_id(id)
        result['collaborators'] = calculate_collaborators(result['works'], id)
    return result
