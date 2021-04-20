from django.contrib import admin
from .models import Member, Board

# Register your models here.

class MemberAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'user_pw', 'user_created', 'user_updated')

class BoardAdmin(admin.ModelAdmin):
    list_display = ('title', 'writer', 'created_at', 'updated_at', 'image')

admin.site.register(Member, MemberAdmin)
admin.site.register(Board, BoardAdmin)
