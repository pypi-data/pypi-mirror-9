import base64
import json

from cubicweb.entities import AnyEntity
from cubicweb import Binary


class Message(AnyEntity):
    __regid__ = 'Message'

    def load_mandrill_content(self, content):
        self.cw_set(
            ts=content['ts'],
            from_email=content['from_email'],
            from_name=content['from_name'],
            subject=content['subject'],
            to_email=content['to']['email'],
            to_name=content['to'].get('name'),
            stags=json.dumps(content['tags']),
            headers=json.dumps(content['headers']),
            text=content['text'],
            html=content['html'])

        for attachment in content['attachments']:
            self._cw.create_entity(
                'File',
                data=Binary(base64.decode(attachment['content'])),
                name_name=attachment['name'],
                name_format=attachment['type'],
                reverse_attachment=self)

    def load_mandrill_info(self, info):
        self.cw_set(
            state=info['state'],
            template=info['template'])

        for d in info['opens_detail']:
            # XXX make somethings less brutal
            try:
                self._cw.create_entity(
                    'MessageOpen',
                    reverse_open=self.eid,
                    ts=d['ts'],
                    ip=d['ip'],
                    location=d['location'],
                    ua=d['ua'])
            except:
                # already logged ?
                pass

        for d in info['clicks_detail']:
            # XXX make somethings less brutal
            try:
                self._cw.create_entity(
                    'MessageClick',
                    reverse_clic=self.eid,
                    ts=d['ts'],
                    url=d['url'],
                    ip=d['ip'],
                    location=d['location'],
                    ua=d['ua'])
            except:
                # already logged ?
                pass
