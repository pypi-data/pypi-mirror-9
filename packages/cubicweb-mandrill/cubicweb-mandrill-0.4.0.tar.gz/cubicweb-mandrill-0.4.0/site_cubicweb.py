options = (
    ('mandrill-apikey', {
        'type': 'string',
        'default': '',
        'help': 'Mandrill API Key',
        'group': 'mandrill',
        'level': 3
    }),
    ('mandrill-overrides-smtp', {
        'type': 'yn',
        'default': True,
        'help': 'Should the mandrill cube override the '
                'default sendmail functions',
        'group': 'mandrill',
        'level': 3
    }),
)
