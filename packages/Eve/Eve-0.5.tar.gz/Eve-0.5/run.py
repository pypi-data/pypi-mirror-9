# -*- coding: utf-8 -*-

from eve import Eve
from eve.io.mongo import Validator
from cerberus import errors
from eve.auth import BasicAuth, TokenAuth, HMACAuth
from hashlib import sha1
import hmac
from flask import request, make_response
from redis import Redis
from werkzeug.routing import BaseConverter
from uuid import UUID

redis = Redis()

class UUIDValidator(Validator):
    """
    Extends the base mongo validator adding support for the uuid data-type
    """
    def _validate_type_uuid(self, field, value):
        try:
            UUID(value)
        except ValueError:
            self._error(field, "value '%s' cannot be converted to a UUID" %
                        value)



class UUIDConverter(BaseConverter):
    """
    UUID converter for the Werkzeug routing system.
    """

    def __init__(self, url_map):
        super(UUIDConverter, self).__init__(url_map)

    def to_python(self, value):
        return UUID(value)

    def to_url(self, value):
        return str(value)

# you can have multiple custom converters. Each converter has a key,
# which will be later used to designate endpoint urls, and a specialized
# BaseConverter subclass. In this case the url converter dictionary has
# only one item: our UUID converter.
url_converters = {'uuid': UUIDConverter}

from eve.io.base import BaseJSONEncoder


class UUIDEncoder(BaseJSONEncoder):
    """ JSONEconder subclass used by the json render function.
    This is different from BaseJSONEoncoder since it also addresses
    encoding of UUID
    """

    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        else:
            # delegate rendering to base class method (the base class
            # will properly render ObjectIds, datetimes, etc.)
            return super(UUIDEncoder, self).default(obj)

class HMACAuth(HMACAuth):
    def check_auth(self, userid, hmac_hash, headers, data, allowed_roles,
                   resource, method):
        # use Eve's own db driver; no additional connections/resources are
        # used
        return True
        accounts = app.data.driver.db['accounts']
        user = accounts.find_one({'userid': userid})
        if user:
            secret_key = user['secret_key']
        # in this implementation we only hash request data, ignoring the
        # headers.
        return user and \
            hmac.new(str(secret_key), str(data), sha1).hexdigest() == \
                hmac_hash


class TAuth(TokenAuth):
    def check_auth(self, token, allowed_roles, resource, method):
        return token == 'token'

class Auth(BasicAuth):
    def check_auth(self, username, password, allowed_roles, resource, method):
        #print "username", username
        import ipdb; ipdb.set_trace()  # XXX BREAKPOINT
        #self.request_auth_value = username
        self.set_request_auth_value(username)
        return username == 'token'
        #return username == 'admin' and password == 'secret'


class Validator(Validator):
    def _validate_empty(self, empty, field, value):
        super(Validator, self)._validate_empty(empty, field, value)
        if isinstance(value, list) and len(value) == 0 and not empty:
            self._error(field,errors.ERROR_EMPTY_NOT_ALLOWED)

def before_insert(name, items):
    print "hello"

def getting_contatti(request, lookup):
    print "lookup a", lookup
    #lookup["_id"] = "52c27a8338345b482a60c3a4"
    lookup["username"] = {'$exists': False}

def pre_post(resource, request, lookup):
    print resource, request
    print lookup
    #lookup["ciao"] = "ciao"
    #del(documents[0]['etag'])

def getting(resource, request, lookup):
    print ("getting %s" % resource)
    #del(documents[0]['etag'])

def gotit(resource, request, response=None):

    print ('get', resource)
    print (request)

def fetched_contacts(res, items):
    import pdb; pdb.set_trace()  # XXX BREAKPOINT
    print res
    print items

def fetched_contact(res, response):
    print res
    print response['name']

def resource_gotit(request, response):
    print ('get_contacts')
    print (request.data)
    print (response.data)

def resource_post(resource, request, response):
    print "howdy"
    print response.get_data()
    pass
    #print resource
    ##print (request.authorization)
    #print request.get_data()
    #print response.get_data()

def posting(documents):
    #print ("posting to ", resource)
    #documents[0]["token"] = "mytoken"
    #from flask import request
    #print "usr", request.authorization.username
    #print documents
    for d in documents:
        d["azzo"] = "azzooo"

def posting_r(documents):
    print ("posting to resource contacts")

def fetching(resource, document):
    document['number'] = 1

def fetching_item(resource, document):
    document['number'] = 1

def edit_request(resource, r):
    r.max_results = 1

app = Eve(validator=Validator, redis=redis)

#@app.errorhandler(401)
#def handle_sqlalchemy_assertion_error(err):
#    return make_response("hello", 401)

#app = Eve(json_encoder=UUIDEncoder, validator=UUIDValidator)

#@app.route('/test')
#def hello_world():
#    return 'Hello World'
#app.config['DOMAIN']['contacts']['auth_username_field'] = 'name'
#app.on_get_contacts += resource_gotit
#app.on_get += gotit
#app.on_pre_GET += getting
#app.on_pre_GET_contacts += getting_contatti
#app.on_pre_POST += pre_post
#app.on_posting += posting
#app.on_posting_contacts += posting_r
#app.on_fetched_resource += fetched_contacts
#app.on_fetched_item += fetched_contact
#app.on_insert_contacts += posting
#app.on_insert += before_insert
#app.on_getting_contacts += getting_contatti
#app.on_post_DELETE += resource_post
#app.on_post_GET += gotit
#app.on_parsed_request += edit_request

if __name__ == '__main__':
    #app.events.on_getting += pre
    #app.on_GET += gotit
    #app.on_post_POST += resource_post
    app.run(debug=True)
