from wargaming.version import get_version


HTTP_USER_AGENT_HEADER = 'python-wargaming/{0} (https://github.com/svartalf/python-wargaming)'.format(get_version())

DEFAULT_LANGUAGE = 'en'

ALLOWED_LANGUAGES = ('en', 'ru', 'pl', 'de', 'fr', 'es', 'zh-cn', 'tr', 'cs',
                     'th', 'vi', 'ko')
