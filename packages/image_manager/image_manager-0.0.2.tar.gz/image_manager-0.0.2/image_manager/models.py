import os.path

from django.db import models
from django.conf import settings

class Image(models.Model):
    file = models.ImageField(upload_to="image_manager/", 
                             height_field="height", 
                             width_field="width")
    alt = models.CharField(max_length=140, null=True, blank=True, 
                           help_text="Recommended for accessibility")

    height = models.PositiveIntegerField(blank=True)
    width = models.PositiveIntegerField(blank=True)
    
    date_uploaded = models.DateTimeField(auto_now_add=True)
    
    # Deprecated
    thumbnail = models.ImageField(upload_to="image_mananager/thumbnails/", editable=False, blank=True, null=True)
        
    def admin_thumbnail(self):
        return '<img style="box-shadow: 1px 1px 2px #333; border:medium solid white;" src="%s" alt="%s" width="160">' % (self.file.url, self.alt)
    admin_thumbnail.allow_tags = True
    admin_thumbnail.short_description = "Thumbnail"
    
    def admin_url(self):
        return '<img src="%s" alt="%s" height="%s" width="%s">' % (self.file.url, 
                                                                   self.alt,
                                                                   self.height,
                                                                   self.width)
    admin_url.short_description = "Embed HTML"
        
    def __unicode__(self):
        return self.file.name
