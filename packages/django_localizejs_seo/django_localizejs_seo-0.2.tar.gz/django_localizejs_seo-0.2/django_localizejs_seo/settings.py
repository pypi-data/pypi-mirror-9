from django.conf import settings as django_settings

ENABLED = getattr(django_settings, 'LOCALIZE_SEO_ENABLED', not django_settings.DEBUG)

IGNORE_URLS = frozenset(getattr(django_settings, 'LOCALIZE_SEO_IGNORE_URLS', ['/sitemap.xml']))

IGNORE_EXTENSIONS = frozenset(getattr(django_settings, 'LOCALIZE_SEO_IGNORE_EXTENSIONS', (
    ".js",
    ".css",
    ".xml",
    ".less",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".pdf",
    ".doc",
    ".txt",
    ".ico",
    ".rss",
    ".zip",
    ".mp3",
    ".rar",
    ".exe",
    ".wmv",
    ".doc",
    ".avi",
    ".ppt",
    ".mpg",
    ".mpeg",
    ".tif",
    ".wav",
    ".mov",
    ".psd",
    ".ai",
    ".xls",
    ".mp4",
    ".m4a",
    ".swf",
    ".dat",
    ".dmg",
    ".iso",
    ".flv",
    ".m4v",
    ".torrent",
)))

USER_AGENTS = frozenset(getattr(django_settings, 'LOCALIZE_SEO_USER_AGENTS', (
    "bot",
    "crawler",
    "baiduspider",
    "80legs",
    "mediapartners-google",
    "adsbot-google"
)))

PRERENDER_URL = getattr(django_settings, 'LOCALIZE_SEO_PRERENDER_URL', "https://prerender-cdn.localizejs.com/api/prerender/get")
