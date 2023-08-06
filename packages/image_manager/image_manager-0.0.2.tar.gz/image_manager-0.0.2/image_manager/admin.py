from django.contrib import admin

from image_manager.models import Image

class ImageAdmin(admin.ModelAdmin):
    #fieldsets = ((None, {"fields": ("file", "alt", ("height", "width",))}),)
    list_display = ("admin_thumbnail", "admin_url", "alt", "width", "height", "date_uploaded")
    readonly_fields = ("width", "height")
    list_filter = ("date_uploaded",)
    search_fields = ("alt", "file")

admin.site.register(Image, ImageAdmin)