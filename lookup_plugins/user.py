import cgi
import urllib2
from ansible.plugins import lookup
from ansible.module_utils import _text
from ansible import errors


URL = 'http://gp-lb.internal.ericsson.com/gp_pf/export?srchCID={uid}&actionType=peoSearch'


class LookupModule(lookup.LookupBase):

    def run(self, terms, variables=None, **kwargs):
        r = urllib2.urlopen(URL.format(uid=terms[0]))
        _, params = cgi.parse_header(r.headers.get('Content-Type', ''))
        encoding = params.get('charset', 'utf-8')
        content = r.read().decode(encoding).rstrip()
        if not len(content) > 0:
            raise errors.AnsibleError('User lookup was empty')

        contents = content.split('\n')

        if len(contents) != 2:
            raise errors.AnsibleError('No data for user \'{}\''.format(terms[0]))
        fields = contents[0].split(';')
        values = contents[1].split(';')
        if len(fields) != len(values):
            raise errors.AnsibleError('Garbled data')

        result = {}
        for i, field in enumerate(fields):
            if len(field) > 0:
                result[_text.to_text(field)] = _text.to_text(values[i])
        return [result]
