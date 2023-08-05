from django.contrib.staticfiles.storage import staticfiles_storage


def static(path):
    return staticfiles_storage.url(path)