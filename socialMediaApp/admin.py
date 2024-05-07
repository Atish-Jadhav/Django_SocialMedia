from django.contrib import admin
from .models import Profile, Post, LikePost, FollowersCount

# Register your models here.
admin.site.register(Profile) #Adds Profile model to Django admininstration page
admin.site.register(Post) #Adds Post model to Django admininstration page
admin.site.register(LikePost) #Adds LikePost model to Django administration page
admin.site.register(FollowersCount) #Adds FollowersCount model to Django administration page