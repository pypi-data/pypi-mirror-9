appname = 'monocle_partners'
context_callback =  "'partners': Partner.objects.all().filter(isShown=True)"
models = [
    'Partner'
]
included_app_reqs = [
    "easy_thumbnails",
]