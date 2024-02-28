import hashlib
import unicodedata

import requests
from rdflib.namespace import SKOS
from requests import RequestException
from skosmos_client import SkosmosClient

from django.conf import settings
from django.core.cache import cache
from django.utils.functional import lazy
from django.utils.translation import get_language

CACHE_TIME = 86400  # 1 day

skosmos = SkosmosClient(api_base=settings.SKOSMOS_API)


def unaccent(text):
    return str(
        unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('utf-8')
    )


def autosuggest(data, query, language=None):
    if not language:
        language = get_language() or 'en'

    query = unaccent(query.lower())

    result = list(
        filter(
            lambda d: query
            in unaccent(d['label'].get(language, d['label'].get('en', '')).lower()),
            data,
        )
    )

    return result


def get_json_data(uri, vocid=None):
    payload = {'uri': uri, 'format': 'application/ld+json'}

    if vocid is not None:
        url = settings.SKOSMOS_API + vocid + '/data'
    else:
        url = settings.SKOSMOS_API + 'data'

    req = requests.get(url, params=payload, timeout=settings.REQUESTS_TIMEOUT)
    req.raise_for_status()

    return req.json()


def get_search_data(uri):
    payload = {
        'query': '*',
        'parent': uri,
        'fields': 'prefLabel',
        'lang': 'en',
        'maxhits': 1000,
        'unique': 'true',
    }

    req = requests.get(
        settings.SKOSMOS_API + 'search',
        params=payload,
        timeout=settings.REQUESTS_TIMEOUT,
    )
    req.raise_for_status()
    return req.json()['results']


def fetch_data(uri, vocid=None, fetch_children=False, source_name=None):
    language = get_language() or 'en'

    cache_key = hashlib.md5(  # nosec
        '-'.join(
            [uri, vocid or '', str(fetch_children), source_name or '', language]
        ).encode('utf-8')
    ).hexdigest()

    data = cache.get(cache_key, [])

    if not data:
        d = get_json_data(uri, vocid)

        for i in d['graph']:
            if i.get('type') == 'skos:Concept' and i['uri'] != uri:
                md = {'source': i['uri']}
                if isinstance(i['prefLabel'], list):
                    md['label'] = {d['lang']: d['value'] for d in i['prefLabel']}
                else:
                    md['label'] = {i['prefLabel']['lang']: i['prefLabel']['value']}
                if source_name:
                    md['source_name'] = source_name
                data.append(md)

                if fetch_children:
                    cd = get_search_data(i['uri'])
                    for ci in cd:
                        cmd = {'source': ci['uri'], 'label': ci['prefLabels']}
                        if source_name:
                            cmd['source_name'] = source_name
                        data.append(cmd)

        if data:
            data = sorted(
                data,
                key=lambda x: x.get('label', {})
                .get(language, x.get('label', {}).get('en', 'zzz'))
                .lower(),
            )
            cache.set(cache_key, data, CACHE_TIME)

    return data


def get_base_keywords():
    return fetch_data(
        'http://base.uni-ak.ac.at/recherche/keywords/collection_base',
        source_name='base',
    )


def get_disciplines():
    cache_key = 'get_disciplines'

    data = cache.get(cache_key, [])

    if not data:
        data = list(
            filter(
                lambda x: len(x['source'].split('/')[-1]) % 3 == 0,
                fetch_data(
                    'http://base.uni-ak.ac.at/portfolio/disciplines/oefos',
                    fetch_children=True,
                    source_name='voc',
                ),
            )
        )

        if data:
            cache.set(cache_key, data, CACHE_TIME)

    return data


def get_roles():
    return fetch_data(
        'http://base.uni-ak.ac.at/portfolio/vocabulary/role',
        source_name='roles',
    )


def get_skills():
    return [
        *get_base_keywords(),
        *get_disciplines(),
        *get_roles(),
    ]


def get_altlabel(concept, project=settings.VOC_ID, graph=settings.VOC_GRAPH, lang=None):
    if lang:
        language = lang
    else:
        language = get_language() or 'en'
    cache_key = f'get_altlabel_{language}_{concept}'

    label = cache.get(cache_key)
    if not label:
        try:
            g = skosmos.data(f'{graph}{concept}')
            for _uri, l in g.subject_objects(SKOS.altLabel):
                if l.language == language:
                    label = l
                    break
        except RequestException:
            pass

        if label:
            cache.set(cache_key, label, CACHE_TIME)

    return label or get_preflabel(concept, project, graph)


def get_altlabel_collection(
    collection, project=settings.TAX_ID, graph=settings.TAX_GRAPH, lang=None
):
    return (
        get_altlabel(collection, project, graph, lang)
        .replace('Sammlung', '')
        .replace('Collection', '')
        .replace('JART', '')
        .strip()
    )


def get_preflabel(
    concept, project=settings.VOC_ID, graph=settings.VOC_GRAPH, lang=None
):
    if lang:
        language = lang
    else:
        language = get_language() or 'en'
    cache_key = f'get_preflabel_{language}_{concept}'

    label = cache.get(cache_key)
    if not label:
        c = skosmos.get_concept(project, f'{graph}{concept}')
        try:
            label = c.label(language)
        except KeyError:
            try:
                label = c.label('de' if language == 'en' else 'en')
            except KeyError:
                pass
        except RequestException:
            pass

        if label:
            cache.set(cache_key, label, CACHE_TIME)

    return label or ''


get_altlabel_lazy = lazy(get_altlabel, str)
get_preflabel_lazy = lazy(get_preflabel, str)
