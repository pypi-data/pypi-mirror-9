appname = 'monocle_reviews'
context_callback =  "'reviews': Review.objects.all().filter(isShown=True)"
models = [
    'Review'
]

included_app_reqs = [

]

