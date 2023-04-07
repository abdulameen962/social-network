from django.contrib import admin

from .models import *

class PostAdmin(admin.ModelAdmin):
    list_display = ("id","creator","post","time","likes")
    
class FollowAdmin(admin.ModelAdmin):
    list_display = ("id","actor")
    filter_horizontal = ("followers",)
    
class FollowedAdmin(admin.ModelAdmin):
    list_display = ("id","actor")
    filter_horizontal = ("followeds",)
    
class ChatAdmin(admin.ModelAdmin):
    list_display = ("id","recipient1","recipient2","is_recipient1_active","is_recipient2_active","timestamp")
    
class MessagesAdmin(admin.ModelAdmin):
    list_display =  ("id","sender","receiver","textmessage","imagemessage","filemessage","timestamp","is_read","chatgroup")
    
# Register your models here.
admin.site.register(Post,PostAdmin)
admin.site.register(User)
admin.site.register(Followers,FollowAdmin)
admin.site.register(Followed,FollowedAdmin)
admin.site.register(Liker)
admin.site.register(Chat,ChatAdmin)
admin.site.register(Messages,MessagesAdmin)
