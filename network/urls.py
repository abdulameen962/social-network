
from django.urls import path

from . import views

app_name = "network"
urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("compose/",views.compose,name="compose"),
    path("profile/<str:username>",views.user_profile,name="profile"),
    path("posts/",views.follow_posts,name="posts"),    
    path("follow-users/",views.all_users,name="follow-users"),
    path("chats/",views.chats_view,name="chats"),
    
    #API routes
    path("add-post",views.add_post,name="add_post"),
    path("edit-post/<int:post_id>",views.edit_post,name="edit-post"),
    path("follow-user/<str:username>",views.follow_user,name="follow-user"),
    path("unfollow-user/<str:username>",views.unfollow_user,name="unfollow-user"),
    path("likepost/<int:post_id>",views.like_post,name="likepost"),
    path("unlikepost/<int:post_id>",views.unlike_post,name="unlikepost"),
    path("liked-post/<int:post_id>",views.liked_post,name="likedpost"),
    path("get-page/<str:username>/<str:page_type>/<int:page_num>",views.get_page,name="get-page"),
    path("get-message/<str:username>",views.get_message,name='get_message'),
    path("send-message/<str:username>",views.send_message,name='send_message'),
    
]
