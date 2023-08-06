#DATABASES = {'default': DATABASES['sqlite']}

#INSTALLED_APPS += ('storages','django_pdb',)
#MIDDLEWARE_CLASSES += ('django_pdb.middleware.PdbMiddleware',)

#AWS_ACCESS_KEY_ID = 'AKIAJSWBP2Y3VOSVNGBQ'
#AWS_SECRET_ACCESS_KEY = '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'
#CELERITY_STATICFILES_BUCKET = 'goldwater-static'
#CELERITY_MEDIAFILES_BUCKET = 'goldwater-media'
#AWS_S3_URL_PROTOCOL = ''
#DEFAULT_FILE_STORAGE = 'goldwater.storage.CelerityMediaFilesStorage'
#STATICFILES_STORAGE = 'goldwater.storage.CelerityStaticFilesStorage'
#STATIC_URL = '{s3_protocol}//{s3_bucket}.s3.amazonaws.com/'.format(
#    s3_protocol=AWS_S3_URL_PROTOCOL,
#    s3_bucket=CELERITY_STATICFILES_BUCKET)
HAYSTACK_CONNECTIONS = {
        'default': {
                    'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
                    'URL': 'https://bofur-us-east-1.searchly.com:80/',
                    'INDEX_NAME': 'goldwater',
                    'TIMEOUT': 60 * 5,
                    'INCLUDE_SPELLING': True,
                    'BATCH_SIZE': 100,
                    'KWARGS': {
                                    'http_auth': 'site:49970ebb2fda35c0ed81e481a07477ef'
                                }
                },
}
