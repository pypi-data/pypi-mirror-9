"""
Asset bundles to use with django-assets
"""
try:
    from django_assets import Bundle, register
except ImportError:
    DJANGO_ASSETS_INSTALLED = False
else:
    DJANGO_ASSETS_INSTALLED = True

    AVALAIBLE_BUNDLES = {
        'bazar_app_css': Bundle(
            "css/bazar_app.css",
            filters='yui_css',
            output='css/bazar_app.min.css'
        ),
        'bazar_app_js': Bundle(
            "js/jquery/jquery.tagsinput.js",
            filters='yui_js',
            output='js/bazar_app.min.js'
        ),
    }

    ENABLED_BUNDLES = (
        'bazar_app_css',
        'bazar_app_js',
    )

    for item in ENABLED_BUNDLES:
        register(item, AVALAIBLE_BUNDLES[item])
