# coding: utf-8

# TLL: Thin LDAP Layer.
# Written by Dimas Moreira Junior.

# Lower level LDAP API
import ldap

# Debug options
DEBUG = False
ldap.set_option(ldap.OPT_DEBUG_LEVEL, 0)

# Constants used in the ldap module
SCOPES = {
    'base': 0,
    'one': 1,
    'sub': 2,
}

def modlist_encode(obj, coding='utf-8'):
    # Encodes unicode to utf-8
    for attr, val in obj.iteritems():
        if isinstance(val, unicode):
            obj[attr] = val.encode(coding)
        elif isinstance(val, list):
            obj[attr] = [v.encode(coding) if isinstance(v, unicode) else v for v in val]    
    return obj

def modlist_add(obj):
    '''Returns a python-ldap (modlist) 'add' representation of obj.'''
    # Encodes unicode to utf-8
    modlist_encode(obj)
    # Create a add tuple for each attribute, ignoring dn
    return [(attr, obj[attr]) for attr in obj if not attr == 'dn']

def modlist_modify(obj):
    '''Returns a python-ldap (modlist) 'modify' representation of obj.'''
    # Encodes unicode to utf-8
    modlist_encode(obj)
    # Modification mode
    mode = ldap.MOD_REPLACE
    # Create a modification tuple for each attribute, ignoring the dn
    return [(mode, attr, obj[attr]) for attr in obj if not attr == 'dn']

def fix_filterstr(filterstr):
    '''Add parenthesis to filterstr, in case it needs to.'''
    if filterstr[0] == '(' and filterstr[-1] == ')': return filterstr
    return '(' + filterstr + ')'

def inject_dn(obj, dn):
    '''Inject a dn key in the obj dictionary and returns it.'''
    obj['dn'] = dn
    return obj

def get_dn(obj_or_dn):
    '''Allows methods to receive a dn string or a dictionary with a dn key.'''
    return str(obj_or_dn) if isinstance(obj_or_dn, basestring) else obj_or_dn['dn']

def debug(msg):
    if DEBUG:
        print msg

class Connection(object):
    '''Instances of this class represent an LDAP connection.'''

    def __init__(self, host='127.0.0.1', port=389,
                 bind_dn='', bind_pw='', base=''):
        self.host = host
        self.port = port
        self.bind_dn = bind_dn
        self.bind_pw = bind_pw
        self._base = base
        # Connects and stores a reference to the connection
        self.connection = ldap.open(self.host, self.port)
        self.connection.simple_bind_s(self.bind_dn, self.bind_pw)
        # TODO: check if this is necessary when bind_dn empty
        self.FORCE_SINGLE_VALUE = []

    def __str__(self): return self.url(self._base, show_user=False)

    def __repr__(self): return 'Connection(%s)' % repr(str(self))

    def __del__(self): self.connection.unbind_s()

    def base(self):
        '''Returns the object specified as the connection's base.'''
        # TODO: verify if base is defined, otherwise rise exception
        return self.search('(%s)' % self._base, scope=BASE)[0]

    def modrdn(self, old_obj_or_dn, new_rdn):
        # TODO: accept obj_or_dn
        '''Modifies the RDN of an object, efectively moving it in the DIT.'''
        dn = get_dn(old_obj_or_dn)
        self.connection.modrdn_s(old_dn, new_rdn)

    def passwd(self, obj_or_dn, new_pwd):
        '''Send a request to modify a password.'''
        dn = get_dn(obj_or_dn)
        self.connection.passwd_s(dn, None, new_pwd)
        debug('LDAP PASSWD %s ***' % dn)

    def search(self, filterstr='(objectclass=*)', base='', scope='one',
               attrlist=[]):
        '''Send an LDAPSEARCH request to the host of this connection, wrapping
        the results in Objects, before returnning them.'''
        if not base: base = self._base
        filterstr = fix_filterstr(filterstr)
        url = self.url(base)
        debug('LDAP SEARCH ldap://%s:%s/%s?%s?%s?%s' % (
            self.host, self.port, base, ','.join(attrlist), scope, filterstr))
        results = self.connection.search_s(base, SCOPES[scope], filterstr, attrlist)
        return self.wrap(results)

    def modify(self, obj):
        '''Send an LDAPMODIFY request to the host of this connection, after it
        converts the obj dictionary into a modlist structure used in the
        LDAP protocol. The object must have a minimum number of attributes
        as defined by a schema in the LDAP server. Only atributes present
        in obj are modified in the server, other atributes remain unchanged.'''
        modlist = modlist_modify(obj)
        debug('LDAP MODIFY %s' % self.url(obj['dn']))
        debug('            %s' % modlist)
        return self.connection.modify_s(obj['dn'], modlist)

    def add(self, obj):
        '''Send an LDAPADD request to the host of this connection, after it
        converts the obj dictionary into a modlist structure compatible with
        the LDAP protocol. The object must have a minimum number of attributes
        as defined by a schema in the LDAP server.'''
        modlist = modlist_add(obj)
        debug('LDAP ADD %s' % self.url(obj['dn']))
        debug('         %s' % modlist)
        return self.connection.add_s(obj['dn'], modlist)

    def delete(self, obj_or_dn):
        '''Send an LDAPDELETE request to the host of this connection. It
        accepts a dictionary with a dn key or a dn string.'''
        dn = get_dn(obj_or_dn)
        debug('LDAP DELETE %s' % self.url(dn))
        return self.connection.delete_s(dn)

    def url(self, obj_or_dn, show_user=False):
        '''Returns a string representation of this connection, cocatenated with
        a specified dn. The user may be optionally shown.'''
        dn = get_dn(obj_or_dn)
        user = '%s@' % self.bind_dn if show_user and self.bind_dn else ''
        return 'ldap://%s%s:%s/%s' % (user, self.host, self.port, dn)
        # TODO: make dn optional, show the base if not specified. sames as str

    def single_value(self, obj):
        '''Unpack single objects in lists for the attributes specified in
           FORCE_SINGLE_VALUE.'''
        result = {}
        # TODO: Performance - loop throug the shorter list, either
        # FORCE_SINGLE_VALUE or obj.keys()
        for attr, val in obj.iteritems():
            result[attr] = val[0] if attr in self.FORCE_SINGLE_VALUE else val
        return result

    def wrap(self, results):
        '''For each result in the search results, inject the result dn
           and, for the attributes specified in FORCE_SINGLE_VALUE,
           replace the returned list by the single value it contains.'''
        # Inject dn in dictionaries
        results = [inject_dn(obj, dn) for dn, obj in results]
        # Force single value
        results = [self.single_value(obj) for obj in results]
        # TODO: add ability to tll to return an empty list for properties
        # not in FORCE_SINGLE_VALUE
        # Return the transformed list of dictionaries.
        return results
