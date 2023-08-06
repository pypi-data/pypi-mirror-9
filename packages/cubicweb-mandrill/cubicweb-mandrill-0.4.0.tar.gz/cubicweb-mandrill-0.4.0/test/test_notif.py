
from cubicweb.devtools import testlib
from cubes.mandrill.sobjects import (
    MandrillNotificationView, FileContentLoader)


class TestNotificationView(testlib.CubicWebTC):
    def test_template_notification_single_recipient(self):
        class Notif(MandrillNotificationView):
            template_name = 'one'
            template_content = [
                ('head', '<h1>hi *|user_displayname|*</h1>'),
                ('body', '<p>Some text</p>')
            ]

            def recipients(self):
                return [('to@example.com', 'fr')]

        with self.admin_access.repo_cnx() as cnx:
            view = Notif(cnx, rset=cnx.execute('CWUser X'))
            messages = list(view.render_emails())

        self.assertEqual(1, len(messages))

    def test_template_notification_multiple_recipient(self):
        class Notif(MandrillNotificationView):
            template_name = 'one'
            template_content = [
                ('head', '<h1>hi *|user_displayname|*</h1>'),
                ('body', '<p>Some text</p>')
            ]

            def recipients(self):
                return [
                    ('to1@example.com', 'fr'),
                    ('to2@example.com', 'en'),
                    ('to3@example.com', 'fr'),
                    ('to4@example.com', 'en')]

            def context(self, **kw):
                return kw

        with self.admin_access.repo_cnx() as cnx:
            view = Notif(cnx, rset=cnx.execute('CWUser X'))
            messages = list(view.render_emails(somearg='test'))

        self.assertEqual(2, len(messages))
        (rcpt1, msg1), (rcpt2, msg2) = messages
        self.assertEqual(['to1@example.com', 'to3@example.com'], rcpt1)
        self.assertEqual(['to2@example.com', 'to4@example.com'], rcpt2)

        self.assertEqual(
            [{'name': 'somearg', 'content': 'test'}],
            msg1.message['global_merge_vars'])

    def test_dict_content(self):
        class Notif(MandrillNotificationView):
            template_name = 'test'
            template_content = [
                ('head', {
                    None: u"default_head",
                    'fr': u"fr_head"})
            ]

            def recipients(self):
                return [
                    ('to@example.com', 'fr'),
                    ('to@example.com', 'en')]

        with self.admin_access.repo_cnx() as cnx:
            view = Notif(cnx, rset=cnx.execute('CWUser X'))
            messages = list(view.render_emails(somearg='test'))

        (rcpt1, msg1), (rcpt2, msg2) = messages

        self.assertEqual(u"fr_head", msg1.template_content[0]['content'])
        self.assertEqual(u"default_head", msg2.template_content[0]['content'])

    def test_filecontentloader(self):
        fcl = FileContentLoader(
            'testdata/greetings.html', modname='cubes.mandrill')
        self.assertEqual(
            u'<h2>Bonjour *|user_displayname|*</h2>\n', fcl.get('fr'))
        self.assertEqual(
            u'<h2>Hi *|user_displayname|*</h2>\n', fcl.get(None))
        self.assertEqual(
            u'<h2>Hi *|user_displayname|*</h2>\n', fcl.get('en'))

    def test_fcl_content(self):
        class Notif(MandrillNotificationView):
            template_name = 'test'
            template_content = [
                ('head', FileContentLoader(
                    'testdata/greetings.html', modname='cubes.mandrill'))
            ]

            def recipients(self):
                return [
                    ('to@example.com', 'fr'),
                    ('to@example.com', 'de')]

        with self.admin_access.repo_cnx() as cnx:
            view = Notif(cnx, rset=cnx.execute('CWUser X'))
            messages = list(view.render_emails(somearg='test'))

        (rcpt1, msg1), (rcpt2, msg2) = messages

        self.assertEqual(
            u'<h2>Bonjour *|user_displayname|*</h2>\n',
            msg1.template_content[0]['content'])
        self.assertEqual(
            u'<h2>Hi *|user_displayname|*</h2>\n',
            msg2.template_content[0]['content'])
