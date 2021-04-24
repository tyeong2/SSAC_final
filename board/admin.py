from django.contrib import admin
from .models import Member, Board, UserCar

# Register your models here.

class MemberAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'user_nickname', 'user_pw', 'user_created', 'user_updated')

class BoardAdmin(admin.ModelAdmin):
    list_display = ('title', 'writer', 'created_at', 'updated_at', 'image_path', 'hit')

class UserCarAdmin(admin.ModelAdmin):
    list_display = ('member', 'type', 'brand', 'img_path', 'saved_at')

admin.site.register(Member, MemberAdmin)
admin.site.register(Board, BoardAdmin)
admin.site.register(UserCar, UserCarAdmin)
