from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required

from django.contrib import messages
from django.conf import settings
from .models import Profile
from .forms import CreateUserForm

import smtplib
import requests

import random


def index(request):
    if request.method == "POST":
        pass
    return render(request, 'account/index1.html')


def registerPage(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        # checking form
        if form.is_valid():
            # sending  otp to email
            email = form.cleaned_data.get("email")
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login("email", "pwd")
            try:
                otp = ''.join([str(random.randint(0, 9)) for i in range(4)])
                print(otp)
                msg = 'Hello,Your OTP is ' + str(otp)
            except Exception as a:
                print(a)

            server.sendmail("from_email", email, msg)
            server.close()
            user = form.save()
            print(user)
            user = Profile.objects.filter(user=user).first()
            print(user, "devuda")
            user.otp = otp
            user.email = email
            user.save()
            print(user.email)

            request.session['email'] = email
            return redirect('emailverification')

    context = {'form': form}
    return render(request, 'account/register.html', context)

# verifying email with otp
def emailverification(request):
    email = request.session['email']
    context = {'email': email}
    if request.method == "POST":
        otp = request.POST.get('otp')
        profile = Profile.objects.filter(email=email).first()
        # print(profile.id)
        if otp == profile.otp:
            user = User.objects.get(id=profile.user_id)
            print(user)
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            request.session['email'] = email

            return redirect('verify_mobile')
            # return redirect('useremailhome')
            # return render(request, 'home.html')
        else:
            context = {'message': 'Wrong OTP', 'class': 'danger'}
            return render(request, 'account/login_otp.html', context)

    return render(request, 'account/emailverification.html')




def loginpage(request):
    if request.method == "POST":
        email = request.POST.get('email')
        user1 = User.objects.filter(email=email).first()
        print(user1)

        password = request.POST.get('password')

        user = authenticate(request, username=user1, password=password)
        print(user)

        if user is not None:
            login(request, user)
            request.session['email'] = email
            return redirect('useremailhome')
        else:
            messages.info(request, "Username or Password is incorrect")
    return render(request, 'account/login.html')

# sending otp to mobile
def send_otp_fast(mobile, otp):
    url = "https://www.fast2sms.com/dev/bulk"
    authkey = settings.AUTH_KEY

    querystring = {
        "authorization": f"{authkey}",
        "sender_id": "FSTSMS", "message": f"your otp is{otp}",
        "language": "english", "route": "p", "numbers": f"{mobile}"}

    headers = {
        'cache-control': "no-cache"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    print(response.text)


# login with otp
def login_mobile(request):
    if request.method == "POST":
        mobile = request.POST.get('mobile')

        user = Profile.objects.filter(mobile=mobile).first()

        if user is None:
            context = {'message': 'User not found', 'class': 'danger'}
            return render(request, 'account/login_mobile.html', context)

        otp = str(random.randint(1000, 9999))
        print(otp)
        # overriding current opt with previous otp
        user.otp = otp
        user.save()
        send_otp_fast(mobile, otp)
        request.session['mobile'] = mobile
        return redirect('login_otp')
    return render(request, 'account/login_mobile.html')


def login_otp(request):
    mobile = request.session['mobile']
    context = {'mobile': mobile}
    if request.method == "POST":
        otp = request.POST.get('otp')
        profile = Profile.objects.filter(mobile=mobile).first()
        # print(profile.id)
        if otp == profile.otp:
            user = User.objects.get(id=profile.user_id)
            print(user)
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')

            return redirect('userhome')
            # return render(request, 'home.html')
        else:
            context = {'message': 'Wrong OTP', 'class': 'danger', 'mobile': mobile}
            return render(request, 'account/login_otp.html', context)
    return render(request, "account/login_otp.html", context)



def logoutpage(request):
    logout(request)
    return redirect('login')


def verify_mobile(request):
    user = request.user
    print(user)
    profile = Profile.objects.filter(user=user).first()
    print(profile)
    mobile = profile.mobile
    print(mobile)
    if mobile:
        request.session['mobile'] = mobile
        return redirect('userhome')
    # print(profile)
    if request.method == "POST":
        mobile = request.POST.get('mobile')
        check_profile = Profile.objects.filter(mobile=mobile).first()
        if check_profile:
            context = {'message': 'That number already registered', 'class': 'danger'}
            return render(request, 'account/registermobile.html', context)

        otp = str(random.randint(1000, 9999))
        print(otp)
        profile.mobile = mobile
        profile.otp = otp
        send_otp_fast(mobile, otp)
        profile.save()
        request.session['mobile'] = mobile
        return redirect('login_otp')

    return render(request, 'account/registermobile.html')


@login_required(login_url='login')
def userhome(request):
    try:
        user = request.user
        mobile = request.session['mobile']
        name = Profile.objects.filter(mobile=mobile).first()
        print(name)
        context = {'name': name}
        return render(request, 'account/userhome.html', context)
    except Exception as ex:
        return redirect('login')



@login_required(login_url='login')
def useremailhome(request):
    try:
        email = request.session['email']
        name = Profile.objects.filter(email=email).first()
        print(name)
        context = {'name': name}
        return render(request, 'account/userhome.html', context)
    except Exception as ex:
        return redirect('login')


