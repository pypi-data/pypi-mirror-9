import ckan.plugins.toolkit as toolkit


def get_esd_function_titles(value):
    return _get_titles(value, 'function')


def get_esd_service_titles(value):
    return _get_titles(value, 'service')


def _get_titles(value, obj_type):
    if not value:
        return None

    if ',' in value:
        ids = value.split(',')
    else:
        ids = value.split(' ')

    titles = []
    for id in ids:
        try:
            esd_object = toolkit.get_action('esd_{0}_show'.format(obj_type))(
                {}, {'id': id})
            titles.append(esd_object['title'])
        except toolkit.ObjectNotFound:
            pass

    return ', '.join(titles)
