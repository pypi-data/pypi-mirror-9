"""
Default Bazar settings to import/define in your project settings
"""
gettext = lambda s: s

ENTITY_KINDS = (
    ('customer', gettext('Customer')),
    ('supplier', gettext('Supplier')),
    ('internal', gettext('Internal')),
    ('administration', gettext('Administration')),
)
DEFAULT_ENTITY_KIND = 'customer'

BAZAR_ENTITY_INDEX_PAGINATE = 20
BAZAR_NOTE_INDEX_PAGINATE = 20

#
# Optionnal text markup settings
#

# Field helper for text in forms
BAZAR_MARKUP_FIELD_HELPER_PATH = None # Default, just a CharField
#BAZAR_MARKUP_FIELD_HELPER_PATH = "bazar.markup.get_text_field" # Use DjangoCodeMirror

# Template to init some Javascript for text in forms
BAZAR_MARKUP_FIELD_JS_TEMPLATE = None # Default, no JS template
#BAZAR_MARKUP_FIELD_JS_TEMPLATE = "bazar/markup/_text_field_djangocodemirror_js.html" # Use DjangoCodeMirror

# Validator helper for Post.text in forms
BAZAR_MARKUP_VALIDATOR_HELPER_PATH = None # Default, no markup validation
#BAZAR_MARKUP_VALIDATOR_HELPER_PATH = "bazar.markup.clean_restructuredtext" # Validation for RST syntax (with Rstview)

# Text markup renderer template
BAZAR_MARKUP_RENDER_TEMPLATE = None # Default, just a CharField
#BAZAR_MARKUP_RENDER_TEMPLATE = "bazar/markup/_text_markup_render.html" # Use Rstview renderer
