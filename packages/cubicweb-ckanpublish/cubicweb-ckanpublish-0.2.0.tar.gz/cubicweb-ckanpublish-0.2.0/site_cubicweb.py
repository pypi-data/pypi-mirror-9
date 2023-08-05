from logilab.common.configuration import REQUIRED

options = (
    ('ckan-baseurl',
     {'type' : 'string',
      'default': REQUIRED,
      'help': u'base url of the CKAN instance to push data to',
      'group': 'ckan', 'level': 0,
      }),
    ('ckan-api-key',
     {'type' : 'string',
      'default': REQUIRED,
      'help': u'an API key for the CKAN instance',
      'group': 'ckan', 'level': 0,
      }),
    ('ckan-organization',
     {'type' : 'string',
      'help': u'the organization under which dataset will be created',
      'group': 'ckan', 'level': 0,
      }),
)

