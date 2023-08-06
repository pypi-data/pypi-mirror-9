from sqlalchemy import or_

import ckan.plugins.toolkit as toolkit

import ckan.lib.dictization as d

from ckanext.esdstandards.model import ESDService, ESDFunction


@toolkit.side_effect_free
def esd_function_show(context, data_dict):

    toolkit.check_access('esd_function_show', context, data_dict)

    return _find(context, data_dict, ESDFunction)


@toolkit.side_effect_free
def esd_service_show(context, data_dict):

    toolkit.check_access('esd_service_show', context, data_dict)

    return _find(context, data_dict, ESDService)


@toolkit.side_effect_free
def esd_function_autocomplete(context, data_dict):

    toolkit.check_access('esd_function_autocomplete', context, data_dict)

    return _autocomplete(context, data_dict, ESDFunction)


@toolkit.side_effect_free
def esd_service_autocomplete(context, data_dict):

    toolkit.check_access('esd_service_autocomplete', context, data_dict)

    return _autocomplete(context, data_dict, ESDService)


def _find(context, data_dict, esd_class):
    model = context['model']

    id = unicode(toolkit.get_or_bust(data_dict, 'id'))

    result = model.Session.query(esd_class) \
                          .filter(or_(esd_class.esd_id==id,
                                      esd_class.title==id,
                                      esd_class.uri==id)) \
                          .all()

    if result:
        return d.table_dictize(result[0], context)
    else:
        raise toolkit.ObjectNotFound


def _autocomplete(context, data_dict, esd_class):
    model = context['model']

    q = toolkit.get_or_bust(data_dict, 'q')
    limit = data_dict.get('limit')

    results = model.Session.query(esd_class) \
                           .filter(esd_class.title.ilike('{0}%'.format(q))) \
                           .order_by(esd_class.title)
    if limit:
        results = results.limit(limit)
    return [d.table_dictize(result, context) for result in results]


@toolkit.auth_allow_anonymous_access
def esd_auth(context, data_dict):
    return {'success': True}
