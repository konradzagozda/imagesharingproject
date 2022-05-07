from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth.admin import UserAdmin
from .models import User, ThumbnailSize, Tier, OriginalImage, ThumbnailImage


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("Tier", {"fields": ("tier",)}),)


admin.site.register(ThumbnailSize, ModelAdmin)
admin.site.register(Tier, ModelAdmin)
admin.site.register(OriginalImage, ModelAdmin)
