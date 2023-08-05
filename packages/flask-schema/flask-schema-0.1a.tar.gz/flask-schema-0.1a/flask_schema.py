from flask import request, abort
from jsonschema import _validators
from collections import defaultdict
from werkzeug.utils import cached_property
import re
import json
import jsonschema
import uuid

# ToDo: Check format checkers
# ToDo: URL Prefix (?)
# ToDo: Log missing schema for appro-pro routes


class ValidationError(Exception):

    def __init__(self, errors):
        Exception.__init__(self)
        self.errors = errors

    @property
    def dict(self):
        # ToDo: do some fancy-pants handling here to return client-side errors?
        return [{
            "path": '/'+ '/'.join([str(i) for i in e.absolute_path]),
            "failed": '/'+ '/'.join([str(i) for i in e.absolute_schema_path]),
            "message": e.message
        } for e in self.errors]



def _parse_json(payload):
    return json.loads(payload)


class Router(object):

    def __init__(self, schema):
        self.parent = schema
        self.routes = self.build_routes()
        self._route_cache = {}

    def build_routes(self):
        routes = defaultdict(lambda: defaultdict(lambda: None))
        def _build_routes(schema):
            for link in schema.get('links', []):
                method, href = self.parse_link(link)
                if not method:
                    continue
                routes[method][href] = link
            for key, subschema in schema.get('definitions', {}).items():
                routes.update(**_build_routes(subschema))
            return routes
        return _build_routes(self.parent.schema)

    def _parse_href(self, url):
        s = lambda m: chr(int(m.group(1),16))
        return re.sub("{(.*?)}", "[^/]+",
            re.compile('%([0-9a-fA-F]{2})',re.M).sub(s, url)
        )

    def parse_link(self, link):
        method = link.get('method')
        href = link.get('href')
        if not method or not href:
            return None, None
        return method.upper(), self._parse_href(href)

    def find_link(self, method, path):
        cache = self._route_cache.get(request.endpoint)
        if cache:
            return cache
        method = method.upper()
        for href, link in self.routes.get(method, {}).items():
            if re.match('^%s$' % href, path):
                self._route_cache[request.endpoint] = link
                return link


class Schema(object):

    def __init__(self, schema, app=None):
        self.schema = schema
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.router = Router(self)
        self.parsers = {
            'application/json': _parse_json
        }

        # Set the config
        app.config.setdefault('SCHEMA_STRICT', True)
        app.config.setdefault('SCHEMA_URL_PREFIX', None)

        # Setup format checkers, validators
        self.validator = jsonschema.validators.extend(
            jsonschema.Draft4Validator,
            validators={
                u"$ref" : _validators.ref,
                u"additionalItems" : _validators.additionalItems,
                u"additionalProperties" : _validators.additionalProperties,
                u"allOf" : _validators.allOf_draft4,
                u"anyOf" : _validators.anyOf_draft4,
                u"dependencies" : _validators.dependencies,
                u"enum" : _validators.enum,
                u"format" : _validators.format,
                u"items" : _validators.items,
                u"maxItems" : _validators.maxItems,
                u"maxLength" : _validators.maxLength,
                u"maxProperties" : _validators.maxProperties_draft4,
                u"maximum" : _validators.maximum,
                u"minItems" : _validators.minItems,
                u"minLength" : _validators.minLength,
                u"minProperties" : _validators.minProperties_draft4,
                u"minimum" : _validators.minimum,
                u"multipleOf" : _validators.multipleOf,
                u"not" : _validators.not_draft4,
                u"oneOf" : _validators.oneOf_draft4,
                u"pattern" : _validators.pattern,
                u"patternProperties" : _validators.patternProperties,
                u"properties" : _validators.properties_draft4,
                u"required" : _validators.required_draft4,
                u"type" : _validators.type_draft4,
                u"uniqueItems" : _validators.uniqueItems,
            }
        )
        self.format_checker = jsonschema.FormatChecker()

        @self.format_checker.checks('uuid')
        def check_uuid(value):
            try:
                uuid.UUID(str(value))
                return True
            except ValueError:
                return False

        self.resolver = jsonschema.RefResolver('', self.schema)

        # Implement our validation hook using Flask.before_request
        app.before_request(self._handle_request)

        self.app = app

    def parse(self, content_type):
        def wrapper(func):
            self._parsers[content_type] = func
            return func
        return wrapper

    @property
    def _method(self):
        return request.method.upper()

    def validator_for(self, schema):
        return self.validator(
            schema,
            resolver=self.resolver,
            format_checker=self.format_checker
        )

    def _handle_request(self):
        # We only validate requests that supply data
        if self._method not in ['POST', 'PUT', 'PATCH']:
            return

        link = self._get_request_schema()
        if not link and self.app.config.get('SCHEMA_STRICT'):
            abort(404)

        if not request.headers.get('content-type'):
            abort(400)

        if not request.data:
            abort(400)

        data = self._parse_request_data()
        self._validate_and_parse(link, data)


    def _parse_request_data(self):
        # ToDo: Not sure if I can take the content-type
        ct = request.headers.get('content-type')
        if not ct:
            # Content-Type Header must be set
            abort(400)

        parser = self.parsers.get(ct)
        if not parser:
            # Content-Type not supported
            abort(400)

        if not request.data:
            return {}

        try:
            return parser(request.data)
        except:
            # Unable to parse data. Invalid payload
            abort(400)

    def _get_request_schema(self):
        return self.router.find_link(self._method, request.path)

    def _validate_and_parse(self, link, data):
        validator = self.validator_for(link['schema'])
        errors = list(validator.iter_errors(data))

        validator = self.validator_for(link['schema'])
        errors = list(validator.iter_errors(data))

        if errors:
            if self.custom_handler:
                raise ValidationError(errors)
            else:
                abort(422)
        else:
            properties = link['schema']['properties'].keys()
            data = {k: data[k] for k in properties if k in data}
            request.view_args['params'] = data

    @cached_property
    def custom_handler(self):
        exc_handlers = self.app.error_handlers.get(None, [])
        return any([e == ValidationError for e, f in exc_handlers])
