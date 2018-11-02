import json
from base64 import b64encode, b64decode
from collections.abc import Mapping, Iterable

JSON_ENCODER_LAMBDAS = {
    bytes: lambda o: "~b%s" % str(b64encode(o), encoding="utf-8"),
}


def _entity_json_encoder(o):
    """JSON encoder function. Usage: json.dumps(entity, default=_entity_json_encoder)"""
    value_type = type(o)
    json_encoder = JSON_ENCODER_LAMBDAS.get(value_type)
    if json_encoder is None:
        if isinstance(o, Mapping):
            return dict(o)
        elif not isinstance(o, str) and isinstance(o, Iterable):
            return list(o)
        else:
            raise TypeError(repr(o) + " is not JSON serializable")
    else:
        return json_encoder(o)


def entities_to_json(entities, sort_keys=False, indent=None, cls=None):
    """Returns a JSON serialized string from the given entities. This method is able
    to properly serialize non-native JSON types supported in entity bytes."""
    return json.dumps(entities, default=_entity_json_encoder,
                      sort_keys=sort_keys, indent=indent, cls=cls, ensure_ascii=False)
