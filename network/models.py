from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass
    def serialize(self):
        return{
            "id": self.id,
            "username": self.username,
        }

class Post(models.Model):
    creator = models.ForeignKey(User,on_delete=models.PROTECT,related_name="usercreator")
    post = models.TextField(max_length=4000)
    time = models.DateTimeField(auto_now=False, auto_now_add=True)
    likes = models.IntegerField(default=0)
    
    def serialize(self):
        return{
            "id": self.id,
            "creator":self.creator.username,
            "post": self.post,
            "time":self.time.strftime("%I:%M %p, %B %d, %Y"),
            "likes":self.likes
        }
        
    def __str__(self):
        return f"{self.id} {self.creator} created {self.post} by {self.time} and got {self.likes} like(s)"


class Liker(models.Model):
    likedpost = models.ForeignKey(Post,on_delete=models.CASCADE,related_name="postliked")
    likes = models.ManyToManyField(User,blank=True,related_name="userlikes")
    
    def serialize(self):
        return{
            "id":self.id,
            "likedpost": self.likedpost,
            "likes": self.likes.all()
        }
        
    def __str__(self):
        return f"{self.id} {self.likedpost} was liked by {self.likes.all()}"
    

#users followers
class Followers(models.Model):
    actor = models.ForeignKey(User,on_delete=models.PROTECT,related_name="followed")
    followers = models.ManyToManyField(User, related_name="user_followers")
    
    def serialize(self):
        return{
            "id": self.id,
            "actor": self.actor,
            "followers": self.followers.all()
        }
        
    def is_valid_follower(self):
        return self.actor != self.followers
    
    def __str__(self):
        return f"{self.id} {self.actor} has {len(self.followers.all())} follower(s)"
        
#people the user is following
class Followed(models.Model):
    actor = models.ForeignKey(User,on_delete=models.PROTECT,related_name="follower")
    followeds = models.ManyToManyField(User,related_name="followings")
    
    def serialize(self):
        return{
            "id": self.id,
            "actor": self.actor,
            "followeds": self.followeds.all()
        }
        
    def is_valid_follower(self):
        return self.actor != self.followeds
    
    def __str__(self):
        return f"{self.id} {self.actor} follows {self.followeds.all()}"
    
    
class Chat(models.Model):
    recipient1 = models.ForeignKey(User,related_name="receiver1",on_delete=models.PROTECT)
    recipient2 = models.ForeignKey(User,related_name="receiver2",on_delete=models.PROTECT)   
    is_recipient1_active = models.BooleanField(default=True)
    is_recipient2_active = models.BooleanField(default=True) 
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=False,null=True,blank=True)
    
    def serialize(self):
        return{
            "id": self.id,
            "recipient1": self.recipient1.serialize(),
            "recipient2": self.recipient2.serialize(),
            "is_recipient1_active": self.is_recipient1_active,
            "is_recipient2_active": self.is_recipient2_active,
            "messages": [message.serialize() for message in self.chats.all()],
        } 
    
    def __str__(self):
        return f"The chats have {self.recipient1} and {self.recipient2} and it is {self.is_recipient1_active} for the first user and {self.is_recipient2_active} for the second user and the messages are {self.chats.all()}"
    
    
class Messages(models.Model):
    sender = models.ForeignKey(User,related_name="messagesender",on_delete=models.PROTECT)
    receiver = models.ForeignKey(User,on_delete=models.PROTECT,related_name="messagereceiver")
    textmessage  = models.TextField(default=None)
    imagemessage = models.ImageField(upload_to="chats/images",default=None,null=True)
    filemessage = models.FileField(upload_to="chats/files", default=None,null=True)
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)
    is_read = models.BooleanField(default=False)
    chatgroup = models.ForeignKey(Chat,on_delete=models.PROTECT,related_name="chats")
    
    def serialize(self):
        return{
            "id" : self.id,
            "sender": self.sender.serialize(),
            "receiver": self.receiver.serialize(),
            "text": self.textmessage,
            "image": self.imagemessage.url if self.imagemessage != "" else  "",
            "file": self.filemessage.url if self.filemessage != "" else  "",
            "timestamp": self.timestamp,
        }
    
    
    def __str__(self):
        return f"{self.sender} sent a message to {self.receiver} which included text of {self.textmessage},image of {self.imagemessage},file of {self.filemessage} sent on {self.timestamp}"
    
        
    
    