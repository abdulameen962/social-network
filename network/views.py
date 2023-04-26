from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect,JsonResponse
from django.shortcuts import render
from django.urls import reverse
import json
from django.utils.datastructures import MultiValueDictKeyError
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.core.paginator import Paginator
from django.utils import timezone

# import time

from .models import *


def index(request):
    posts = Post.objects.all()
    #get latest posts
    posts = posts.order_by("-time").all()
    
    pagination = Paginator(posts,10)
    
    return render(request, "network/index.html",{
        "postpage" : pagination.page_range,
        "pagenumber" : pagination.num_pages,
        "page": "home",
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("network:index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        user = request.user
        if user.is_authenticated:
            return HttpResponseRedirect(reverse("network:index"))
        else:
            return render(request, "network/login.html")


@login_required(login_url="network:login")
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("network:index"))


def register(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("network:index"))
    else:
        if request.method == "POST":
            username = request.POST["username"]
            email = request.POST["email"]

            # Ensure password matches confirmation
            password = request.POST["password"]
            confirmation = request.POST["confirmation"]
            if password != confirmation:
                return render(request, "network/register.html", {
                    "message": "Passwords must match."
                })

            # Attempt to create new user
            try:
                user = User.objects.create_user(username, email, password)
                user.save()
            except IntegrityError and username == "Notsignedin":
                return render(request, "network/register.html", {
                    "message": "Username already taken."
                })
            login(request, user)
            return HttpResponseRedirect(reverse("network:index"))
        else:
            return render(request, "network/register.html")
    
@login_required(login_url="network:login")
def compose(request):
    return render(request,"network/add-post.html")


@login_required(login_url="network:login")
def user_profile(request,username):
    user = User.objects.get(username = username)    
    followerlist = ""
    followedlist = ""
    posts = ""
    #check is user has followed anyone or has followers
    try:
        follower = Followers.objects.get(actor = user)
        followerlist = follower.followers.all()
        followlen = followerlist.count()
    except Followers.DoesNotExist:
        followerlist = ""
        followlen = 0
        
    try:
        followed = Followed.objects.get(actor = user)
        followedlist = followed.followeds.all()
        followedlen = followedlist.count()
    except Followed.DoesNotExist:
        followedlist = ""
        followedlen = 0
        
    #check is the user has created any post
    for a in Post.objects.all():
        if user == a.creator:
           posts = Post.objects.filter(creator = user).order_by("-time").all()
        
    pages = Paginator(posts,10)
    follow = False   
    if  followerlist != "":
        for foll in followerlist:
            if request.user == foll:
                follow = True
    else:
        follow = False
    return render(request,"network/profile.html",{
        "requesteduser" : user,
        "followers" : followerlist,
        "following" : followedlist,
        "followerscount" : followlen,
        "followingcount": followedlen,
        "postpages":pages.page_range,
        "follow" : follow,
    })

@login_required(login_url="network:login")
def follow_posts(request):
    user = request.user
    posts = []
    #check if the user to following anyone to get their posts
    for i in Followed.objects.all():
        if user == i.actor:
           followings = i.followeds.all()
           for follow in followings:
               #get posts from the people user is following
               names = Post.objects.filter(creator = follow)
               for ps in names:
                   posts.append(ps)
                   
    pagination = Paginator(posts,10)
            
            
    return render(request,"network/index.html",{
        "postpage":pagination.page_range,
        "pagenumber" : pagination.num_pages,
        "pagenumber" : pagination.num_pages,
        "page":"following"
    })
    

@login_required(login_url="network:login")
def all_users(request):
    return render(request,"network/users.html",{
        "users": User.objects.all()
    })
    

@login_required(login_url="network:login")
def chats_view(request):
    user = request.user
    chats = []
    
    #get the chat group of the user and user has not deleted chats
    try:
        chatbox1 = Chat.objects.filter(recipient1=user,is_recipient1_active=True)
        
        #add the chats to the chats
        chatbox1 = chatbox1.order_by("-timestamp").all()
        for chat in chatbox1:
            #get the last messsage of the chat
            messages = chat.chats
            messages = messages.order_by("-timestamp").all()
            lastmessage = messages.first()
            newchat = {
                "id": chat.id,
                "lastmessage": lastmessage,
            }
            chats.append(newchat)
        
    except Chat.DoesNotExist:
        chatbox1 = ""
        
    #get the chat if the user is is also a second recipient
    try:
        chatbox2 = Chat.objects.filter(recipient2=user,is_recipient2_active=True)
        
        #add the chats to the chats
        chatbox2 = chatbox2.order_by("-timestamp").all()
        for chat in chatbox2:
            #get the last messsage of the chat
            messages = chat.chats
            messages = messages.order_by("-timestamp").all()
            lastmessage = messages.first()
            newchat = {
                "id": chat.id,
                "lastmessage": lastmessage,
            }
            chats.append(newchat)
        
    except Chat.DoesNotExist:
        chatbox2 = ""
    
    return render(request,"network/chats.html",{
        "chats": chats,
    })    
    
        
    
#api routes
@login_required(login_url="network:login")
@csrf_protect
def add_post(request):
    
    #composing a new post must be via POST
    if request.method == "POST":
        #check post details
        data = json.loads(request.body)
        post = data.get("post","")
        
        #check if post is empty
        if post == "":
            return JsonResponse({"error":"Post must not be empty"},status = 400)
        else:
            user = request.user
            newpost = Post(creator=user, post = post,likes=0)
            newpost.save()
            return JsonResponse({"message":"Post added successfully"},status=201)

    else:
        return JsonResponse({"error":"Post method required"},status=400)
    
    
@login_required(login_url="network:login")
@csrf_protect
def edit_post(request,post_id):
    #check if post exists
    try:
        post = Post.objects.get(pk=int(post_id))
        #check if user is the creator of the post
        if request.user == post.creator:
            if request.method == "POST":
                data = json.loads(request.body)
                newpostcontent = data.get("post","")
                #check if post is empty
                if newpostcontent != "":
                    #attempt to edit post
                    try:
                        newpost = Post(id=post.id,creator=post.creator,post=newpostcontent,time=post.time,likes=post.likes)
                        newpost.save()
                        return JsonResponse({"message":"post edited successfully"},status=201)
                    except IntegrityError:
                        return JsonResponse({"message": "couldn't edit,an error occured"},status=400)
                else:
                    return JsonResponse({"message":"post must not be empty"},status = 400)
                
            elif request.method == "GET":
                #attempts to get post
                return JsonResponse(post.serialize(),safe=False)
            
        else:
            return JsonResponse({"message":"Forbidden request,the user didn't create the post"},status=403)
    except Post.DoesNotExist:
        return JsonResponse({"message":"Post doesn't exist"},status=400)
        
    
# @login_required(login_url="network:login")
def follow_user(request,username):
    user = request.user
    if request.method == "PUT":
        if user.is_authenticated:
            #check if user that user wants to follow exists
            try:
                requestedUser = User.objects.get(username=username)
                #check to prevent same user from following themselves
                if user != requestedUser:
                    #check if the user is following anyone
                    try:
                        following = Followed.objects.get(actor = user)
                        #attempt to add the following
                        try:
                            following.followeds.add(requestedUser)
                            #check if the user he wants to follow has followers
                            try:
                                follower = Followers.objects.get(actor = requestedUser)
                                #attempt to add the new follower
                                try:
                                    follower.followers.add(user)
                                    return JsonResponse({"message":f"{requestedUser} has {follower.followers.all().count()} follower(s)"},status=201)
                                except IntegrityError:
                                    following.followeds.remove(requestedUser)
                                    return JsonResponse({"message":"Couldn't be added to followership"},status=400)
                            except Followers.DoesNotExist:
                                #attempts to create the followership
                                try:
                                    newfollow = Followers(actor = requestedUser)
                                    newfollow.save()
                                    newfollow.followers.add(user)
                                    return JsonResponse({"message":f"{requestedUser} has {follower.followers.all().count()} follower(s)"},status=201)
                                except IntegrityError:
                                    following.followeds.remove(requestedUser)
                                    return JsonResponse({"message":"following was added but followers couldnt"},status=400)
                                
                        except IntegrityError:
                            return JsonResponse({"message":"It couldnt be added,the user is following the requested already"},status=400)
                    except Followed.DoesNotExist:
                        # attempt create following
                        try:
                            newfol = Followed(actor=user)
                            newfol.save()
                            newfol.followeds.add(requestedUser)
                            #check if the user he wants to follow has followers
                            try:
                                follower = Followers.objects.get(actor = requestedUser)
                                #attempt to add the new follower
                                try:
                                    follower.followers.add(user)
                                    return JsonResponse({"message":f"{requestedUser} has {follower.followers.all().count()} follower(s)"},status=201)
                                except IntegrityError:
                                    following.followeds.remove(requestedUser)
                                    return JsonResponse({"message":"Couldn't be added to followership"},status=400)
                            except Followers.DoesNotExist:
                                #attempts to create the followership
                                try:
                                    newfollow = Followers(actor = requestedUser)
                                    newfollow.save()
                                    newfollow.followers.add(user)
                                    return JsonResponse({"message":f"{requestedUser} has {follower.followers.all().count()} follower(s)"},status=201)
                                except IntegrityError:
                                    following.followeds.remove(requestedUser)
                                    return JsonResponse({"message":"following was added but followers couldnt"},status=400)
                        except IntegrityError:
                            return JsonResponse({"message" : f"The following couldn't be created {IntegrityError}"}, status = 400)
                else:
                    return JsonResponse({"message":"Same user,cannot follow each other"},status=403)    
            except User.DoesNotExist:
                return JsonResponse({"message":"user that is to be followed doesn't exist"},status=404)
            
        else:
            return JsonResponse({"message":"User is not logged in"},status=403)
        
    else:
        return JsonResponse({"message":"Wrong request method"},status=403)
        
        

# @login_required(login_url="network:login")
def unfollow_user(request,username):
    user = request.user
    if request.method == "PUT":
        #check whether the user that is to be unfollowed exists
        try:
            requestedUser = User.objects.get(username=username)
            #check whether both users have following/followers 
            try:
                following = Followed.objects.get(actor = user)
                follower = Followers.objects.get(actor = requestedUser)
                #check whether both the user and requested user have each other in following and followers respectively
                try:
                    following.followeds.get(username = requestedUser.username)
                    follower.followers.get(username = user.username)
                    #attempt to remove 
                    try:
                        following.followeds.remove(requestedUser)
                        follower.followers.remove(user)
                        return JsonResponse({"message":f"{requestedUser} has {len(follower.followers.all())} follower(s)"},status=201)
                    except IntegrityError:
                        return JsonResponse({"message":"Couldn't unfollow an error occured"},status=403)
                except InterruptedError:
                    return JsonResponse({"message":"User not following requested user and or requested user doesn't have user as a follower"},status=400)
            except Followed.DoesNotExist and Followers.DoesNotExist:
                return JsonResponse({"message":"user isn't following anyone and or requested user doesn't have any followers"},status=400)
        except User.DoesNotExist:
            return JsonResponse({"message":"Requested user doesn't exist"},status=403)
            
    else:
        return JsonResponse({"message":"Wrong method,requires"},status=403)
    
    
# @login_required(login_url="network:login")
def like_post(request,post_id):
    user = request.user
    #check if user is authenticated to return a prompt
    if user.is_authenticated and request.method == "PUT":
        #check if post exists
        try:
            post = Post.objects.get(pk=post_id)
            #check whether has likes and the likes can be traced
            try:
                liker = Liker.objects.get(likedpost = post)
                #check if user has liked the post before
                try:
                    liker.likes.get(username = user.username)
                    return JsonResponse({"message":"user has liked the post before"},status=403)
                except User.DoesNotExist:
                    #attempt to add the liking
                    try:
                        liker.likes.add(user)
                        newlike = Post(pk=post.id,creator=post.creator,post=post.post,time=post.time,likes=len(liker.likes.all()))
                        newlike.save()
                        # time.sleep(500)
                        return JsonResponse({"message":f"Likes: {newlike.likes}"},status=201)
                    except IntegrityError:
                        return JsonResponse({"message":"Post couldn't be liked"},status=400)
            except Liker.DoesNotExist:
                #attempt to create the liking and update the likes
                try:
                    liker = Liker(likedpost = post)
                    liker.save()
                    liker.likes.add(user)
                    newlike = Post(pk=post.id,creator=post.creator,post=post.post,time=post.time,likes=len(liker.likes.all()))
                    newlike.save()
                    # time.sleep(500)
                    return JsonResponse({"message":f"Likes: {newlike.likes}"},status=201)
                except IntegrityError:
                    return JsonResponse({"messasge":"Couldn't save "},status=400)
                
        except Post.DoesNotExist:
            return JsonResponse({"message":"post does not exist"},status=400)
    else:
        return JsonResponse({"message":"user is not signed in/method is wrong"},status=403)


# @login_required(login_url="network:login")
def unlike_post(request,post_id):
    user = request.user
    if user.is_authenticated and request.method == "PUT":
        #check if post exists
        try:
            post = Post.objects.get(pk=post_id)
            #check is user has liked that post to unlike it
            try:
                like = Liker.objects.get(likedpost=post)
                like.likes.get(username=user.username)
                #attempt to unlike post
                try:
                    like.likes.remove(user)
                    newupdate = Post(pk=post.id,post=post.post,creator=post.creator,time=post.time,likes=len(like.likes.all()))
                    newupdate.save()
                    # time.sleep(500)
                    return JsonResponse({"message":f"Likes: {newupdate.likes}"},status=201)
                        
                except IntegrityError:
                    return JsonResponse({"message":"The post couldn't be liked"},status=400)
            except Liker.DoesNotExist and User.DoesNotExist:
                return JsonResponse({"message":"The user has not liked the post before"},status=400)
                
        except Post.DoesNotExist:
            return JsonResponse({"message":"Post does not exist"},status=403)
    else:
        return JsonResponse({"message":"User is not logged in/request method is wrong"},status=403)
    
    
def liked_post(request,post_id):
    user = request.user
    if request.method == "GET":
        if user.is_authenticated:
            #check if post exists
            try:
                post = Post.objects.get(pk=post_id)
                #check if post has been liked
                try:
                    like = Liker.objects.get(likedpost=post)
                    #check if user has liked the post
                    try:
                        like.likes.get(username=user.username)
                        return JsonResponse({"message":True},status=201)
                    except User.DoesNotExist:
                        return JsonResponse({"message":False},status=201)
                except Liker.DoesNotExist:
                    return JsonResponse({"message": False},status=201)
                
            except Post.DoesNotExist:
                return JsonResponse({"message":"post does not exist"},status=403)
            
        else:
            return JsonResponse({"message":"User not logged in"},status=403)
    else:
        return JsonResponse({"message":"wrong requested method"},status=403)
    
    
def get_page(request,username,page_type,page_num):
    if request.method == "GET":
        user = request.user
        #check the type of page being requested
        if page_type == "general":
            #get for general page
            posts = Post.objects.all()
            posts = posts.order_by("-time").all()
        elif page_type == "profile":
            #get for the profile
            if user.is_authenticated:
                user = User.objects.get(username = username)
                #check is the user has created any post
                for a in Post.objects.all():
                    if user == a.creator:
                        posts = Post.objects.filter(creator = user).order_by("-time").all()
            else:
                return JsonResponse({"message":"User isn't signed in"},status=403)
        elif page_type == "following":
            #get for the posts of the followers
            posts = []
            #check if the user to following anyone to get their posts
            if user == User.objects.get(username = username):
                for i in Followed.objects.all():
                    if user == i.actor:
                        followings = i.followeds.all()
                        for follow in followings:
                            #get posts from the people user is following
                            names = Post.objects.filter(creator = follow)
                            for ps in names:
                                posts.append(ps)
                posts.reverse()
            else:
                return JsonResponse({"message":"The user requested isn't you"},status=400)
            
        else:
            return JsonResponse({"message":"wrong page type"},status=403)
        
        #get latest posts
        pagination = Paginator(posts,10)
        #check if page requested exists
        if page_num in pagination.page_range:
            #return the requested page
            posts = pagination.page(page_num)
            return JsonResponse([post.serialize() for post in posts], safe=False,status=201)
        else:
            return JsonResponse({"message":"page doesn't exist"},status=400)
    else:
        return JsonResponse({"message":"Wrong request method"},status=403)
    
    
    
@login_required(login_url="network:login")
def get_message(request,username):
    user = request.user
    try:
        requesteduser = User.objects.get(username=username)
        chatgroup = ""
        try:
            chatgroup = Chat.objects.get(recipient1=user,recipient2= requesteduser)
            
        except Chat.DoesNotExist:
            try:
                chatgroup = Chat.objects.get(recipient1=requesteduser,recipient2= user)
                
            except Chat.DoesNotExist:
                chatgroup = ""
                
                
        if chatgroup != "":
            #try to get the messages
            try:
                messages = chatgroup.chats.all()
                messages = messages.order_by("-timestamp").all()
                messages = Paginator(messages,10)
                messages = messages.page(1)
                
                for message in messages:
                    #mark all messges that the user is a receiver as seen
                    if message.receiver == user:
                       message.is_read = True
                       message.save()
                    
                return JsonResponse([message.serialize() for message in messages],safe=False,status=201)
            except Messages.DoesNotExist:
                #remove the chatgroup
                chatgroup.delete()
                return JsonResponse({"message":"No messages"},status=201)
            
            
        else:
            return JsonResponse({"message":"No messages"},status=201)
                
            
    except User.DoesNotExist or request.method != "GET":
        return JsonResponse({"message":"User not allowed/wrong request method"},status=403)
    
    
@login_required(login_url="network:login")
def send_message(request,username):
    try:
        user = request.user
        requesteduser = User.objects.get(username=username)
        
        data = json.loads(request.body)
        text_message = data.get("text",)
        chatgroup = ""
        
        
        #check if files are present
        try:
            file = data.get("file",)
        except MultiValueDictKeyError or data.get("file",) == "":
            file = ""
            
        #check if images are present
        try:
            image = data.get("image",)
            
        except MultiValueDictKeyError or data.get("image",) == "":
            image = ""
            
        #check if chatgroup exists
        try:
            chatgroup = Chat.objects.get(recipient1 = user,recipient2 = requesteduser)
            
        except Chat.DoesNotExist:
            try:
                chatgroup = Chat.objects.get(recipient1 = requesteduser,recipient2=user)
                
            except Chat.DoesNotExist:
                #create the chatgroup
                try:
                    chatgroup = Chat(recipient1=user,recipient2=requesteduser,timestamp= timezone.now())
                    chatgroup.save()
                    
                except IntegrityError:
                    return JsonResponse({"message":"chatgroup couldn't be created"},status=400)
                
                
        #create the message
        if file == "" and image == "":
            newmessage = Messages(sender=user,receiver=requesteduser,textmessage=text_message,chatgroup=chatgroup)
            newmessage.save()
        elif file == "":
            newmessage = Messages(sender=user,receiver=requesteduser,textmessage=text_message,imagemessage=image,chatgroup=chatgroup)
            newmessage.save()
        elif image == "":
            newmessage = Messages(sender=user,receiver=requesteduser,textmessage=text_message,filemessage=file,chatgroup=chatgroup)
            newmessage.save()
        else:
            newmessage = Messages(sender=user,receiver=requesteduser,textmessage=text_message,imagesmesssage=image,filemessage=file,chatgroup=chatgroup)
            newmessage.save()
            
        return JsonResponse({"message":"successfully saved"},status=201)
                
                
        
    except User.DoesNotExist or request.method != "POST":
        return JsonResponse({"message": "Wrong user/wrong request method"},status=403)