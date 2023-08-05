__version_info__ = (0, 2)
__version__ = '.'.join(map(str, __version_info__))


ANNOTATION_SETTINGS = {
    'default': {
        'mkdn': {
            'name': 'MARKDOWN',
            'display': 'Markdown',
            'callback': 'markdown2.markdown',
            'kwargs': {},
            'default': True
        },
        'rst': {
            'name': 'RST',
            'display': 'reStructured Text',
            'callback': 'docutils.core.publish_parts',
            'kwargs': {'writer_name': 'html4css1'},
            'attr': 'html_body'
        },
        'smpl': {
            'name': 'SIMPLE',
            'display': 'Simple',
            'callback': 'annotation.utils.render_simple'
        }
    },
    'models': []
}
