import re

import mandrill

from logilab.common.decorators import monkeypatch

from cubicweb.entity import Entity

from cubicweb.server import Service
from cubicweb.server.hook import SendMailOp
from cubicweb.server.session import Session, InternalManager
from cubicweb.sobjects import notification


class MandrillMessage(object):
    """A special envelope for messages that must be sent by mandrill.
    """
    def __init__(self, message, template_name=None, template_content=None):
        self.message = message
        self.template_name = template_name
        self.template_content = template_content


def mandrill_api(vreg):
    api = getattr(vreg, '_mandrill_api', None)
    if not api:
        apikey = vreg.config.get('mandrill-apikey')
        if apikey:
            api = mandrill.Mandrill(apikey)
            vreg._mandrill_api = api
    return api


# XXX config.sendmails should be changed by a 'sendmails' service like this one
# For now we'll monkey patch the config.sendmails callers to use the service
# instead.
class SendMails(Service):
    __regid__ = 'sendmails'

    def _handle_send_result(self, result):
        """Handler for the 'messages.send*' functions of the mandrill API.

        The result of this functions is a list a messages (especially their
        ids).

        It is the perfect moment to insert the entities in the database, so we
        can return them instead of the raw mandrill result.
        """
        messages = []

        for m in result:
            messages.append(self._cw.create_entity(
                'Message',
                _id=m['_id'],
                state=m['status'],
                to_email=m['email'],
                state_msg=m.get('reject_reason')))

        return messages

    def __init__(self, *args, **kwargs):
        super(SendMails, self).__init__(*args, **kwargs)

        self.async = kwargs.pop('async', False)

        self.api = mandrill_api(self._cw.vreg)
        self.overrides_smtp = self._cw.vreg.config.get(
            'mandrill-overrides-smtp') if self.api else False

    def call(self, msgs):
        """Provides a mandrill version of config.sendmails"""
        if not self.overrides_smtp:
            self.info("Skip mandrill and use plain old smtp")
            return self._cw.vreg.config.sendmails(msgs)

        self.info("Sending with mandrill")
        messages = []
        # XXX try to merge the messages
        # ie: if same template, same content and global_merge_vars
        # -> merge the merge_vars and recipients and do only one call
        # to mandrill api.
        for msg, recipients in msgs:
            try:
                if isinstance(msg, MandrillMessage):
                    if msg.template_name:
                        ret = self.api.messages.send_template(
                            async=self.async,
                            message=msg.message,
                            template_name=msg.template_name,
                            template_content=msg.template_content)
                    else:
                        ret = self.api.messages.send(
                            async=self.async,
                            message=msg.message)
                else:
                    ret = self.api.messages.send_raw(
                        async=self.async,
                        raw_message=msg.as_string(True),
                        from_email=self._cw.vreg.config['sender-addr'],
                        from_name=self._cw.vreg.config['sender-name'],
                        to=recipients)
                messages.extend(self._handle_send_result(ret))
            except Exception as ex:
                self.exception("Error sending mail to %s (%s)",
                               recipients, ex)
        self.debug(messages)
        self.info("Messages sent")

    # update policy
    # every N minutes,
    # - search and update infos on messages that had events (click, open)
    # - fetch and update content on message that recently switch to a
    # non-pending status that supposes the existence of a content (sent, spam)


@monkeypatch(SendMailOp)
def postcommit_event(self):
    self.session.call_service('sendmails', msgs=self.to_send)


@monkeypatch(notification.NotificationView)
def render_and_send(self, **kwargs):
    self._cw.call_service(
        'sendmails', msgs=self.render_emails(**kwargs))


from cubicweb.server.session import Session
import pkg_resources


class FileContentLoader(object):
    def __init__(self, name, modname=None):
        self.name = name
        if not modname:
            modname = self.__module__
        self.modname = modname

    def get(self, lang=None):
        resname = None
        if lang:
            name_wlang = '%s.%s' % (self.name, lang)
            if pkg_resources.resource_exists(self.modname, name_wlang):
                resname = name_wlang
        if not resname:
            if pkg_resources.resource_exists(self.modname, self.name):
                resname = self.name
        if resname:
            return pkg_resources.resource_string(self.modname, resname)


class MandrillNotificationMixin(object):
    template_name = None

    template_subject = None
    template_content = []

    def user_context(self, user, emailaddr, name, global_context):
        return {'username': name}

    def render_content(self, content, context):
        if isinstance(content, basestring):
            return self._cw._(content) % context
        return content.get(self._cw.lang) or content.get(None)

    def cell_call(self, row, col=0, context=None, **kwargs):
        assert not row or not col, (
            "MandrillNotificationMixin only operates on cell (0, 0)")
        # Only render if some content exists on the view
        # otherwise the new template_content will suffice.
        if self.content:
            self.w(self._cw._(self.content) % context)

    def subject(self, context=None, **kwargs):
        return self._cw._(self.template_subject)

    def render_contents(self, context, **kwargs):
        """Returns both the message subject and all its contents in a
        dictionnary"""
        self.w = None
        # Always call render to ensure compatibility with the default
        # notification views
        subject = self.subject(context=context, **kwargs)
        if not self.template_content:
            return subject, [
                ('content', self.render(context=context, **kwargs))]
        else:
            # XXX New behavior -> use the templates
            contents = [
                (key, self.render_content(value, context))
                for key, value in self.template_content]
            return subject, contents

    def sender(self, global_context, **kwargs):
        if self.user_data.get('email'):
            return (
                self.user_data['email'],
                self.user_data.get(
                    'name', self._cw.vreg.config['sender-name']))
        else:
            return (
                self._cw.vreg.config['sender-addr'],
                self._cw.vreg.config['sender-name'])

    clean_html_re = re.compile(r'<[^>]*>')

    def clean_html(self, s):
        return self.clean_html_re.sub(s, '')

    def render_text_version(self, contents):
        return '\n'.join(
            self.clean_html(content) for name, content in contents)

    def render_emails(self, **kwargs):
        """generate and send emails for this view (one per recipient)"""
        self._kwargs = kwargs
        # group recipients by language
        recipients = {}
        for something in self.recipients():
            # XXX handle getting a CWUser with an email which is not the
            # principal
            if isinstance(something, Entity):
                emailaddr = something.cw_adapt_to('IEmailable').get_email()
                name = something.dc_title()
                lang = something.property_value('ui.language')
                user = something
            else:
                if len(something) == 2:
                    emailaddr, lang = something
                    name = None
                elif len(something) == 3:
                    emailaddr, name, lang = something
                else:
                    raise ValueError(
                        "Recipient should be a tuple (email, name, lang) "
                        "of a user entity")
                user = None
            if emailaddr is not None:
                recipients.setdefault(lang, []).append((user, emailaddr, name))

        if not recipients:
            self.info(
                'skipping %s notification, no recipients', self.__regid__)
            return

        if self.cw_rset is not None:
            entity = self.cw_rset.get_entity(
                self.cw_row or 0, self.cw_col or 0)
            # if the view is using timestamp in message ids, no way to
            # reference previous email
            if not self.msgid_timestamp:
                refs = [
                    self.construct_message_id(eid)
                    for eid in entity.cw_adapt_to(
                        'INotifiable').notification_references(self)]
            else:
                refs = ()
            msgid = self.construct_message_id(entity.eid)
        else:
            refs = ()
            msgid = None

        req = self._cw
        self.user_data = req.user_data()

        # XXX readapt for cw 3.19
        for lang, recipients in recipients.items():
            # Set up the global context
            self._cw = Session(InternalManager(lang=lang), self._cw.repo)
            try:
                global_context = self.context(**kwargs)
                subject, contents = self.render_contents(
                    global_context, **kwargs)
                from_email, from_name = self.sender(global_context, **kwargs)
            except notification.SkipEmail:
                continue
            except Exception as ex:
                self.exception(str(ex))
                continue
            finally:
                self._cw = req

            context = {}
            to = []
            # now gather the user specific contexts
            for user, emailaddr, name in recipients:
                if user is None:
                    user = InternalManager(lang=lang)
                self._cw = Session(user, self._cw.repo)
                try:
                    self._cw.set_cnxset()
                    context[emailaddr] = self.user_context(
                        user, emailaddr, name, global_context)
                    to.append({
                        'email': emailaddr,
                        'type': 'to'})
                    if name:
                        to[-1]['name'] = name
                except notification.SkipEmail:
                    self._cw.rollback()
                    continue
                except:
                    self._cw.rollback()
                    raise
                else:
                    self._cw.commit()
                finally:
                    self._cw.close()
                    self._cw = req

            message = {
                'subject': subject,
                #'msgid': msgid,  XXX use headers ?
                #'references': refs,  XXX use headers ?
                'from_email': from_email,
                'from_name': from_name,
                'to': to,
                'global_merge_vars': [
                    {'name': key, 'content': value}
                    for key, value in global_context.items()
                ],
                'merge_vars': [{
                    'rcpt': emailaddr,
                    'vars': [
                        {'name': key, 'content': value}
                        for key, value in context[emailaddr].items()
                    ]
                } for emailaddr in context]
            }

            # if isinstance(something, Entity):
                    # message['to']['name'] = something.dc_title()
            msg = MandrillMessage(
                message=message,
                template_name=self.template_name,
                template_content=[
                    {'name': name, 'content': content}
                    for name, content in contents])
                #msg = format_mail(self.user_data, [emailaddr], content,
                #subject,
                #config=self._cw.vreg.config, msgid=msgid, references=refs)
            yield msg, context.keys()


class MandrillNotificationView(
        MandrillNotificationMixin, notification.NotificationView):
    """A cw-compatible notification view"""
