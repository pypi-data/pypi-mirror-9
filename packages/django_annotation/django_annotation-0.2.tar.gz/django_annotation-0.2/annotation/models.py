from django.db import models
from django.utils.safestring import mark_safe
from .utils import format_config_decorator, get_annotation_formats, Renderer


#===============================================================================
class AnnotationBase(models.Model):

    Format = get_annotation_formats()

    format = models.CharField(choices=Format.CHOICES, default=Format.DEFAULT, max_length=4)
    text = models.TextField(blank=True)
    html = models.TextField(blank=True)

    #===========================================================================
    class Meta:
        abstract = True

    #---------------------------------------------------------------------------
    @property
    def rendered(self):
        return self.html or self.text

    #---------------------------------------------------------------------------
    @classmethod
    def _render(cls, format, text):
        if not hasattr(cls, '_renderer'):
            cls._renderer = Renderer(cls)
            
        return cls._renderer.render(format, text)
    
    #---------------------------------------------------------------------------
    def render_html(self):
        self.html = self._render(self.format, self.text)
    
    #---------------------------------------------------------------------------
    def safe_html(self):
        return mark_safe(self.rendered)
    
    #---------------------------------------------------------------------------
    def save(self, *args, **kws):
        render = kws.pop('render', True)
        if render:
            self.render_html()
        super(AnnotationBase, self).save(*args, **kws)

