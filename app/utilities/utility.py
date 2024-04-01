import datetime


def camel_str(snake_str):
    capitalized_camel_str = ''.join(x.capitalize() for x in snake_str.lower().split('_'))
    return capitalized_camel_str[0].lower() + capitalized_camel_str[1:]


def camel_dict(d):
    new_d = {}
    for k, v in d.items():
        new_d[camel_str(k)] = v
    return new_d


def json_serial_timestamp(obj):
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))
