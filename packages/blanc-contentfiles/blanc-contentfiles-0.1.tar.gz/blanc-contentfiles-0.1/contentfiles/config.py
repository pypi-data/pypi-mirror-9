import os


def libcloud_providers(project_name):
    return {
        'default': {
            'type': 'libcloud.storage.types.Provider.S3_EU_WEST',
            'user': os.environ.get('AWS_ACCESS_KEY_ID'),
            'key': os.environ.get('AWS_SECRET_ACCESS_KEY'),
            'bucket': os.environ.get('CONTENTFILES_DEFAULT_BUCKET'),
            'path_name': project_name,
            'secure': False,
        },
        'private': {
            'type': 'libcloud.storage.types.Provider.S3_EU_WEST',
            'user': os.environ.get('AWS_ACCESS_KEY_ID'),
            'key': os.environ.get('AWS_SECRET_ACCESS_KEY'),
            'bucket': os.environ.get('CONTENTFILES_PRIVATE_BUCKET'),
            'path_name': project_name,
            'secure': True,
        },
    }
