import json
import base64
import hashlib
import string
import urllib
import urllib2

from optparse import OptionParser
from plugins.output import (CheckException,
                            nagios_ok,
                            nagios_critical,
                            nagios_unknown,
                            nagios_message)


FACTS = ('sshdsakey', 'sshecdsakey', 'sshrsakey')


parser = OptionParser(description='Find duplicate SSH host keys in PuppetDB')
parser.add_option(
    '-H', '--host',
    dest='puppetdb_host', type='str', default='puppetdb.cluster',
    help='PuppetDB hostname'
)
parser.add_option(
    '-s', '--ssl',
    dest='puppetdb_ssl', action='store_true',
    help='PuppetDB use SSL/TLS'
)
parser.add_option(
    '-V', '--api-version',
    dest='puppetdb_version', type='int', default=2,
    help='PuppetDB API version'
)


def check(url):
    """Perform duplicate SSH host key checks"""
    facts = query_puppetdb(url)
    if count_hosts(facts) <= 1:
        nagios_unknown('Need at least two nodes in PuppetDB')

    dupes = find_dupes(facts)
    if len(dupes) == 0:
        nagios_ok('No duplicate SSH host keys found')

    msg = ['Found hosts with duplicate SSH host keys']
    for key, hosts in dupes.items():
        msg.append('')
        msg.append(fingerprint(key))
        for host in hosts:
            msg.append('- {0}'.format(host))

    nagios_critical("\n".join(msg))


def query_puppetdb(base_url):
    """Query a list of certain facts from PuppetDB"""
    query = '["or", {0}]'.format(', '.join([
        '["=", "name", "{0}"]'.format(fact)
        for fact in FACTS
    ]))
    query_string = urllib.urlencode({'query': query})
    url = '{0}/facts?{1}'.format(
        base_url,
        query_string,
    )

    res = urllib2.urlopen(url)
    return json.load(res)


def count_hosts(facts):
    """Count the number of unique hosts"""
    hosts = set([fact['certname'] for fact in facts])
    return len(hosts)


def find_dupes(facts):
    """Find hosts with duplicate SSH host keys from PuppetDB output"""
    hosts_by_key = {}
    for fact in facts:
        hosts_by_key.setdefault(
            fact['value'],
            set(),
        ).add(fact['certname'])

    return {
        k: v
        for k, v in hosts_by_key.items()
        if len(v) > 1
    }


def fingerprint(key):
    """Convert an SSH RSA/DSA public key to a fingerprint string"""
    key = base64.b64decode(key.encode('ascii'))
    fp_plain = hashlib.md5(key).hexdigest()
    return ':'.join(a+b for a,b in zip(fp_plain[::2], fp_plain[1::2]))


def main():
    try:
        opts, args = parser.parse_args()
        url = '{0}://{1}/v{2}'.format(
            'https' if opts.puppetdb_ssl else 'http',
            opts.puppetdb_host,
            opts.puppetdb_version,
        )
        check(url)

    except CheckException as e:
        nagios_message(e.message, e.severity)
    except Exception as e:
        # Catching all other exceptions
        nagios_message("Exception: %s" % e, 3)


if __name__ == '__main__':
    main()
