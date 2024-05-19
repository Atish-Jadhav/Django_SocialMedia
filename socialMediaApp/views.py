from itertools import chain
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth #Importing User Model and auth to authenticate User
from .models import Profile, Post, LikePost, FollowersCount
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib.auth import authenticate,login,logout
from django.http import HttpResponseServerError
from django.db.models import OuterRef, Subquery, Q
import random

# Create your views here.

@never_cache 
@login_required(login_url='signin')
def index(request):
    user_object = User.objects.get(username = request.user.username) #Got the object of currently logged in user
    user_profile = Profile.objects.get(user=user_object) #Used it here to get it's profile

    # posts = Post.objects.all() #Not useful when want to show only the posts of users the currently logged in-user is following.

    user_following_list = [] #The list of users the currently logged in user is following.
    feed = []

    user_following = FollowersCount.objects.filter(follower=request.user.username) #Generating a list of records where currently logged in user is mentioned in follower field.
    print("How many people following? : ", len(user_following))

    for users in user_following:
        user_following_list.append(users.user) #Appending the name of 'user' the currently logged in user is following from the records generated in user_following

    print('User following List = ', user_following_list)

    for usernames in user_following_list:
        feed_lists = Post.objects.filter(user=usernames) #Getting the posts of only those users whose user field in Post is equal to usernames in user_following_list. User_following_list contains only the name of users the currently logged in user follows.
        feed.append(feed_lists)
            
    print('Feed = ', feed)

    # We're taking all the lists stored in feed, combining them into one big list, and storing that big list in feed_list
    feed_list = list(chain(*feed))
    print('Feed_List = ', feed_list)

    # Users profile picture who posted
    usersUsers = []
    for i in range(len(user_following)):
        users_User_list = User.objects.filter(username=user_following[i])
        usersUsers.append(users_User_list)

    print('Users who posted :', usersUsers)
    usersUsers = list(chain(*usersUsers))
    print('Users who posted :', usersUsers)

    usersProfiles = Profile.objects.filter(user__in = usersUsers)
    for pics in usersProfiles:
        print('Urls of profile pics of users who posted : ', pics.profileimg.url)
    # Users profile picture who posted - end

    print('Users Profiles :', usersProfiles)

    #User Suggestions
    all_Users = User.objects.all()
    user_following_all = [] #List of users the current logged-in user is already following

    for user in user_following:
        user_list = User.objects.get(username = user.user)
        user_following_all.append(user_list)
    
    print('User_following_all list :', user_following_all)
    
    new_suggestions_list = [x for x in list(all_Users) if (x not in list(user_following_all))]
    print('new_suggestion_list list :', new_suggestions_list)

    # Need to remove current user from new_suugestions_list as it filters out users who are not following current logged-in user.
    # And as user can't follow himself, the user's own id will be included in new_suggestions_list. We don't want to suggest someone their own id.
    current_user = User.objects.filter(username = request.user.username)
    final_suggestions_list = [x for x in list(new_suggestions_list) if (x not in list(current_user))]
    random.shuffle(final_suggestions_list)

    print('final_suggestions_list list :', final_suggestions_list)

    username_profile = []
    username_profile_list = []

    for users in final_suggestions_list:
        username_profile.append(users.id)

    print('Username_Profile list :', username_profile)

    for ids in username_profile:
        profile_lists = Profile.objects.filter(id_user = ids) 
        username_profile_list.append(profile_lists)

    print('Username_Profile_list list :', username_profile_list)

    suggestions_username_profile_list = list(chain(*username_profile_list))
    print('suggestions_username_profile_list list :', suggestions_username_profile_list)

    print('User :', request.user.username, 'Is Authenticated :', request.user.is_authenticated)
    return render(request, "index.html", { 'user_profile' : user_profile, 'posts' : feed_list, 'usersProfiles' : usersProfiles, 'suggestions_username_profile_list' : suggestions_username_profile_list[:4] }) #[:4] getting only four records

def signup(request):
    if(request.method == 'POST'):
        nm = request.POST['username']
        email = request.POST['email']
        p = request.POST['password']
        cp = request.POST['cpassword']
        print('Username :', nm, 'Email :', email, 'Password :', p, 'Confirm Password :', cp)

        if p == cp :
            if User.objects.filter(email=email).exists():
                messages.info(request, "Email already exists")
                return redirect('/signup')
            elif User.objects.filter(username=nm).exists():
                messages.info(request, "Username already exists")
                return redirect('/signup')
            else:
                user = User.objects.create_user(username=nm, email=email, password=p)
                user.save()

                # Log user in and redirect to settings.page
                user_login = auth.authenticate(username = nm, password = p)
                auth.login(request, user_login)

                # Create a profile object for the new user
                user_model = User.objects.get(username=nm) #For the user field in Profile class in models.py
                new_profile = Profile.objects.create(user=user_model, id_user = user_model.id) #Storing the values in fields user and id_user of Profile.
                new_profile.save()
                return redirect('/settings')
        else :
            messages.info(request, "Password Not Matching")
            return redirect('/signup')

    return render(request, 'signup.html')

def signin(request):
    if(request.method == 'POST'):
        nm = request.POST['username']
        p = request.POST['password']
        print('Username :', nm, 'Password :', p)
        user = auth.authenticate(username = nm, password = p)
        if user is not None :
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Check username or password')
            return redirect('/signin')
    else:
        return render(request, 'signin.html')


@login_required(login_url='signin')
def signout(request):
    auth.logout(request)
    return redirect('/signin')

@login_required(login_url='signin')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)

    if(request.method == 'POST'):
        # If the user didn't submit any image
        if(request.FILES.get('image') == None):
            image = user_profile.profileimg
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
        
        elif(request.FILES.get('image') != None):
            image = request.FILES.get('image')
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
        
        return redirect('/settings')

    return render(request, 'setting.html', { 'user_profile' : user_profile })

@login_required(login_url='signin')
def upload(request):
    if(request.method == 'POST'):
        user = request.user.username
        image = request.FILES.get('image_upload') #image_upload taken from input type in index.html
        caption = request.POST['caption']

        print(user, image, caption)

        new_post = Post.objects.create(user=user, image=image, caption=caption)
        new_post.save()

        return redirect ('/')
    else:
        return redirect('/')


@login_required(login_url='signin')
def like_post(request):
    username = request.user.username
    # post_id = request.GET.get('post_id') assigns the value of the 'post_id' query parameter to the variable post_id, or None if the parameter is not present in the URL
    post_id = request.GET.get('post_id')
    post = Post.objects.get(id = post_id) #Getting the post whose id is equal to our post_id
    # Checking if the post is already liked by the currently logged in user
    like_filter = LikePost.objects.filter(post_id=post_id, username=username).first() 
    if(like_filter == None):
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        new_like.save()
        post.no_of_likes = post.no_of_likes + 1
        post.save()
        return redirect('/')
    else:
        like_filter.delete()
        post.no_of_likes = post.no_of_likes - 1
        post.save()
        return redirect('/')
    
@login_required(login_url='signin')
def profile(request, id):
    user_object = User.objects.get(username = id)
    user_profile = Profile.objects.get(user = user_object)
    user_posts = Post.objects.filter(user = id) #id is the username of currently viewing user
    user_post_length = len(user_posts)

    follower = request.user.username
    user = id
    print(follower, 'viewing ', user)

    if FollowersCount.objects.filter(follower=follower, user=user).first():
        button_text = 'Unfollow'
    else:
        button_text = 'Follow'
    
    # id is the user we are viewing through profile/id/
    user_followers = len(FollowersCount.objects.filter(user=id))
    user_following = len(FollowersCount.objects.filter(follower=id))

    context = {
        'user_object' : user_object,
        'user_profile' : user_profile,
        'user_posts' : user_posts,
        'user_post_length' : user_post_length,
        'button_text': button_text,
        'followers': user_followers,
        'following': user_following,
    }
    return render(request, 'profile.html', context)

@login_required(login_url='signin')
def follow(request):
    if request.method == 'POST':
        follower = request.POST['follower']
        following = request.POST['user']
        print(follower, ' is following ', following)

        # If user already following, then unfollow the profile
        if FollowersCount.objects.filter(follower=follower, user=following).first():
            delete_follower= FollowersCount.objects.get(follower=follower, user=following)
            delete_follower.delete()
            return redirect('/profile/' + following) #return to the page of user who you were viewing
        else:
            # If not following, then follow the user
            new_follower= FollowersCount.objects.create(follower=follower, user=following)
            new_follower.save()
            return redirect('/profile/' + following)
    else:
        return redirect('/')
    
@login_required(login_url='signin')
def search(request):
    user_object = User.objects.get(username=request.user.username) #To show current logged-in user in search page in right-hand side corner.
    user_profile = Profile.objects.get(user=user_object)

    if request.method == 'POST':
        username = request.POST['username'] #line 40 in index.html
        username_object = User.objects.filter(username__icontains = username) #If in search, you type ed, the database will be searched for all users and filtered with ed in them.

        print(username_object)

        username_profile = []
        username_profile_list = []

        for users in username_object:
            username_profile.append(users.id) #Append the ids of users containing the search term.

        print(username_profile)

        for ids in username_profile:
            profile_lists = Profile.objects.filter(id_user = ids)
            username_profile_list.append(profile_lists)

        print(username_profile_list)

        # We're taking all the lists stored in username_profile_list, combining them into one big list, and storing that big list again in username_profile_list
        username_profile_list = list(chain(*username_profile_list))    
        print(username_profile_list)

    return render(request, 'search.html', { 'user_object' : user_object, 'user_profile' : user_profile, 'username_profile_list' : username_profile_list })