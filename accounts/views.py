from django.shortcuts import render, redirect
from .models import Account
from django.http import JsonResponse
from django.contrib import messages
import bcrypt
import uuid
import os

def login_user(request):
    try:
        user = request.session['user']
        return redirect('home')
    except:
        pass
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password'].encode('utf-8')
        try:
            user_check = Account.objects.get(email=email)
            userPassword = user_check.password.encode('utf-8')
            if bcrypt.checkpw(password, userPassword):
                request.session['user'] = {'email': user_check.email, 'first_name': user_check.first_name, 'last_name': user_check.last_name, 'token': user_check.token}
                messages.success(request, 'Logged in Successfully');
                return redirect('/files?path=home')
            else:
                messages.error(request, "Please check email and password before logging in!!!")
                return redirect('login_user')
        except:
            messages.error(request, "Please check email and password before logging in!!!")
            return redirect('login_user')
    context = {
        'title': "Login",
    }
    return render(request, 'accounts/login.html', context)

def logout(request):
    try:
        del request.session['user']
        messages.success(request, "Logged out successfully")
        return redirect('login_user')
    except:
        return redirect('login_user')