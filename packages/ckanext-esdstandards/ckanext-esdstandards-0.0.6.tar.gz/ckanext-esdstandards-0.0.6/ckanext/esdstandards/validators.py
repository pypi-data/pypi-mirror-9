import ckan.plugins.toolkit as toolkit


def esd_function_validator(value, context):
    return _validate('function', value, context)


def esd_service_validator(value, context):
    return _validate('service', value, context)


def _validate(obj_type, value, context):

    if not value:
        return

    if ',' in value:
        values = value.split(',')
    elif ' ' in value:
        values = value.split(' ')
        if not values[0].startswith('http'):
            try:
                int(values[0])
            except ValueError:
                values = [value]
    else:
        values = [value]

    values = [v.strip() for v in values]

    new_values = []
    for esd_uri in values:
        try:
            esd_obj = toolkit.get_action('esd_{0}_show'.format(obj_type))(
                context, {'id': esd_uri})
            new_values.append(esd_obj['uri'])
        except toolkit.ObjectNotFound:
            raise toolkit.Invalid(
                'ESD {0} not known: {1}'.format(obj_type.title(), esd_uri))

    value = ' '.join(new_values)

    return value
