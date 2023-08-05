import re
from functools import wraps
from django.conf import settings
from django.utils.module_loading import import_string
from choice_enum import make_enum_class, Option, ChoiceEnumeration
from annotation import ANNOTATION_SETTINGS

multiline_re = re.compile(r'\r?\n(?:[ \t]*\r?\n)+')
url_re = re.compile(r'''
    (ht|f)tps?://                                           # Protocol
    (?:\w+:\w+@)?                                           # Username:Password
    ([-\w]+)(\.[-\w]+)*                                     # domain
    ([\d]{1,5})?                                            # Port
    (                                                       # Directories
        ((/([-\w~!$+|.,=]   |
        %[a-f\d]{2})+)+|/)+ |
        \?                  |
        [#]
    )?  
    (                                                       # Query
        (
            \?([-\w~!$+|.,*:]   |
            %[a-f\d{2}])+=
            ([-\w~!$+|.,*:=]|%[a-f\d]{2})*
        )
        (&
            ([-\w~!$+|.,*:]|%[a-f\d{2}])+
            =([-\w~!$+|.,*:=]|%[a-f\d]{2})*
        )*
    )*
    ([#](?:[-\w~!$+|.,*:=]|%[a-f\d]{2})*)?                  # Anchor
    ''',
    re.VERBOSE
)

FORMAT_MODEL_NAME = 'Format'

#-------------------------------------------------------------------------------
def render_simple(text, **kws):
    text = url_re.sub(r'<a href="\g<0>">\g<0></a>', text)
    lines = []
    for para in multiline_re.split(text):
        lines.append('<p>')
        lines.append('\n    '.join(para.splitlines()))
        lines.append('</p>')
        
    return '\n'.join(lines)


#===========================================================================
class DefaultAnnotationFormat(ChoiceEnumeration): 
    MARKDOWN  = Option('mkdn',  'Markdown', default=True)
    SIMPLE    = Option('smpl',  'Basic')
    RST       = Option('rst',   'reStructured Text')


#===============================================================================
class Configurator(object):
    
    #---------------------------------------------------------------------------
    def __init__(self):
        self.cfg = getattr(settings, 'ANNOTATION', ANNOTATION_SETTINGS)
        self.default = self.cfg.get('default', ANNOTATION_SETTINGS['default'])
        self.models = self.cfg.get('models', [])
    
    #---------------------------------------------------------------------------
    def resolve(self, mod=None):
        if mod and mod in self.models:
            return [(k, self.default[k]) for k in self.models[mod]]
            
        return self.default.items()

    #---------------------------------------------------------------------------
    def load_options(self, mod=None):
        return {
            v['name']: Option(k, v['display'], default=v.get('default', False))
            for k,v in self.resolve(mod)
        }
    
    #---------------------------------------------------------------------------
    @classmethod
    def get(cls):
        if not hasattr(cls, '_configurator'):
            cls._configurator = cls()
        return cls._configurator


#-------------------------------------------------------------------------------
def get_annotation_formats(mod=None):
    cfg = Configurator.get()
    kwargs = cfg.load_options(mod)
    return make_enum_class(FORMAT_MODEL_NAME, **kwargs)


#-------------------------------------------------------------------------------
def class_conf_key(cls):
    return '%s.%s' % (cls.__module__, cls.__name__)


#-------------------------------------------------------------------------------
def format_config_decorator(cls):
    setattr(cls, FORMAT_MODEL_NAME, get_annotation_formats(class_conf_key(cls)))
    return cls


#-------------------------------------------------------------------------------
def render_wrapper(func, kwargs, attr=None):
    kwargs = kwargs or {}
    @wraps(func)
    def inner_render(text):
        rv = func(text, **kwargs)
        if attr:
            if hasattr(rv, attr):
                rv = getattr(rv, attr)
            else:
                rv = rv[attr]
        return unicode(rv)
    return inner_render


#===============================================================================
class AnnotationError(Exception):
    pass


#===============================================================================
class Renderer(object):
    
    #---------------------------------------------------------------------------
    def __init__(self, cls=None):
        conf = getattr(settings, 'ANNOTATION', ANNOTATION_SETTINGS)
        self.default = conf['default']
        self.mod = class_conf_key(cls) if cls else None
        self.settings = conf.get('models', {}).get(self.mod) if cls else None
        self.formats = {}
        
    #---------------------------------------------------------------------------
    def resolve_format(self, format):
        if self.settings:
            if format not in self.settings:
                raise AnnotationError('Unknown format "%s" for %s' % (format, self.mod))

        conf = self.default[format]
        callback = import_string(conf['callback'])
        kwargs = conf.get('kwargs')
        attr = conf.get('attr')
        return callback, kwargs, attr
        
    #---------------------------------------------------------------------------
    def __getitem__(self, format):
        if format not in self.formats:
            cb, kwargs, attr = self.resolve_format(format)
            self.formats[format] = render_wrapper(cb, kwargs, attr)
        return self.formats[format]
    
    #---------------------------------------------------------------------------
    def render(self, format, text):
        handler = self[format]
        return handler(text)
        
