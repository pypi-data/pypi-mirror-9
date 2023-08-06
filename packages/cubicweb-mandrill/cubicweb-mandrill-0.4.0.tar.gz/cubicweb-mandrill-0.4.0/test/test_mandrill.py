# copyright 2014 UNLISH (Montpellier, France), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@unlish.com
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""cubicweb-mandrill automatic tests
"""

from cubicweb.devtools import testlib

from cubes.mandrill.sobjects import MandrillMessage, mandrill_api

msg_content = u'''Hello World,

How you doing ?
'''
msg_subject = u"Hello World"


template = {
    #"key": "example_key",
    "name": "Example Template",
    "from_email": "from_email@example.com",
    "from_name": "Example Name",
    "subject": "example subject",
    "code": "<div mc:edit='content'>example code</div>",
    "text": "Example text content",
    "publish": True,
    "labels": [
        "example-label"
    ]
}


class TestMandrillAPI(testlib.CubicWebTC):
    def setUp(self):
        super(TestMandrillAPI, self).setUp()

    @classmethod
    def init_config(cls, config):
        super(TestMandrillAPI, cls).init_config(config)
        config['mandrill-apikey'] = '_wiTDC7d1AX4m6_BeYR2Tg'
        config['mandrill-overrides-smtp'] = True

    def test_send_raw(self):
        from cubicweb.mail import format_mail
        r = self.request()
        msg = format_mail(
            {'email': 'from@example.com'}, ['to@example.com'],
            u'Hello World,\n\nHow you doing ?', u"Hello World",
            config=r.vreg.config)
        self.session.call_service(
            'sendmails', msgs=[(msg, ['to@example.com'])])

        rset = self.execute("Any X WHERE X is Message")
        self.assertEqual(1, rset.rowcount)

    def test_send(self):
        msg = MandrillMessage({
            'subject': msg_subject,
            'text': msg_content,
            'from_email': 'from@example.com',
            'from_name': 'From Example',
            'to': [{
                'email': 'to@example.com',
                'name': 'To Example',
                'type': 'to'
            }],
        })
        self.session.call_service(
            'sendmails', msgs=[(msg, ['to@example.com'])])
        rset = self.execute("Any X WHERE X is Message")
        self.assertEqual(1, rset.rowcount)

    def test_get_mandrill_api(self):
        api1 = mandrill_api(self.session.vreg)
        self.assertIs(api1, mandrill_api(self.session.vreg))

    def test_send_template(self):
        mandrill = mandrill_api(self.session.vreg)
        mandrill.templates.add(**template)
        try:
            msg = MandrillMessage(
                message={
                    'from_email': 'from@example.com',
                    'from_name': 'From Example',
                    'to': [{
                        'email': 'to@example.com',
                        'name': 'To Example',
                        'type': 'to'
                    }],
                },
                template_name='Example Template',
                template_content=[
                    {'name': 'content', 'content': "This is a test"}
                ])
            self.session.call_service(
                'sendmails', msgs=[(msg, ['to@example.com'])])
            rset = self.execute("Any X WHERE X is Message")
            self.assertEqual(1, rset.rowcount)
        finally:
            mandrill.templates.delete(name='Example Template')

if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
