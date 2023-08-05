from django.conf import settings
from djlibcloud.storage import LibCloudStorage, LibCloudPrivateStorage
import os.path


CONTENTFILES_SSL = getattr(settings, 'CONTENTFILES_SSL', False)


class ContentFilesMixin(object):
    def __init__(self, *args, **kwargs):
        super(ContentFilesMixin, self).__init__(*args, **kwargs)
        self.path_name = self.provider['path_name']

    def _clean_name(self, name):
        clean_name = super(ContentFilesMixin, self)._clean_name(name)
        clean_name = os.path.join(self.path_name, clean_name)
        return clean_name

    def _save(self, name, content):
        full_name = os.path.join(self.path_name, name)
        super(ContentFilesMixin, self)._save(full_name, content)
        return name


class MediaStorage(ContentFilesMixin, LibCloudStorage):
    def url(self, name):
        protocol = 'https' if CONTENTFILES_SSL else 'http'
        return '%s://%s.contentfiles.net/media/%s' % (protocol, self.path_name, name)


class PrivateStorage(ContentFilesMixin, LibCloudPrivateStorage):
    def __init__(self, provider_name='private', *args, **kwargs):
        return super(PrivateStorage, self).__init__(provider_name, *args, **kwargs)

    def url(self, name):
        protocol = 'https' if CONTENTFILES_SSL else 'http'
        return '%s://%s/%s/%s/%s' % (
            protocol, self.driver.connection.host, self.bucket, self.path_name, name)
