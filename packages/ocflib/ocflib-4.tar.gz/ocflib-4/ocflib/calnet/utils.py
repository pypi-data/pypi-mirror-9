import ldap
try:
    from xml.etree import ElementTree
except ImportError:
    from elementtree import ElementTree

from urllib.parse import urlencode
from urllib.request import urlopen
from urllib.parse import urljoin

import ocflib.constants


def verify_ticket(ticket, service):
    """Verifies CAS 2.0+ XML-based authentication ticket.

    Returns CalNet UID on success and None on failure.
    """
    params = {'ticket': ticket, 'service': service}
    url = (urljoin(ocflib.constants.CAS_URL, 'serviceValidate') + '?' +
           urlencode(params))
    try:
        page = urlopen(url)
        response = page.read()
        tree = ElementTree.fromstring(response)
        if tree[0].tag.endswith('authenticationSuccess'):
            return tree[0][0].text
        else:
            return None
    except:
        return None


def _get_calnet_names(uid):
    """Returns CalNet LDAP entries relating to names"""
    l = ldap.initialize(ocflib.constants.UCB_LDAP)
    l.simple_bind_s("", "")
    search_filter = "(uid=%s)" % uid
    attrs = ["givenName", "sn", "displayname"]
    ldap_entries = l.search_st(ocflib.constants.UCB_LDAP_BASE,
                               ldap.SCOPE_SUBTREE, search_filter, attrs)
    if len(ldap_entries):
        return ldap_entries[0][1]
    else:
        return None


def name_by_calnet_uid(uid):
    """Returns the name of CalNet person, searched by CalNet UID.

    Returns None on faliure.
    """
    names = _get_calnet_names(uid)

    # the name we want to input into our system is "givenName sn"
    # displayName is not necessarily equal to what's printed on Cal 1 Cards
    get_longest_string = lambda strs: max(strs, key=len)

    if "givenName" in names and "sn" in names:
        given_name = get_longest_string(names["givenName"])
        sn = get_longest_string(names["sn"])
        if given_name and sn:
            return "%s %s" % (given_name, sn)
    elif "displayName" in names:
        display_name = get_longest_string(names["displayName"])
        if display_name:
            return display_name
    return None
