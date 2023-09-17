from Meta import HTMLMeta


def home(req):
    
    context = {}
    # META
    meta = HTMLMeta(
        title='',
        type='Website',
        desc='',
        keyw=[],
        url='https://SITE.ir',
        img_url='https://SITE.ir/banner.png',
        img_size='1391*348'
    )
    context['meta'] = meta.get_meta()
    context['meta']['schemas'] = [
        meta.get_schema('Site','SITENAME','https://SITE.ir/logo.png'),
    ]
    # Meta
    return render(req,'temp.html',context)