from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from login_page import settings
from django.core.mail import send_mail, EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from . tokens import generate_token

# Create your views here.

def home(request):
    return render(request, "authentication/index.html")

def signup(request):
    if request.method == "POST":
        username = request.POST.get('username')
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')

        if User.objects.filter(username=username):
            messages.error(request, "Username already exist! please try some other useranme")
            return redirect('home')


        if User.objects.filter(email=email):
            messages.error(request, "Email already exist")
            return redirect('home')

        if len(username)>10:
            messages.error(request, "Username must be under 10 charector")
            return redirect('home')

        if pass1 != pass2:
            messages.error(request, "password didn't match!")
            return redirect('home')

        if not username.isalnum():
            messages.error(request, "Username must be Alpha-Numeric!")
            return redirect('home')
        
        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.is_active = False

        myuser.save()

        messages.success(request," Your Account has been successfully created. We have sent you a confirmation email, please confirm your email in order to activate your acount")


        #welcome email
        subject = "Welcome to My login system"
        message = "Hello"+ myuser.first_name+ "!! \n"+"Welcome to GFG!! \n Thank you for visiting our website \n we have also send you a confirmation email, please confirm your email address to activate your account. \n\n Thank your\n Harsh\n"
        form_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, form_email, to_list,fail_silently=True)

        #email address confirmation email

        current_site = get_current_site(request)
        email_subject = "Confirm your email at harsh django login"
        message2 = render_to_string("email_confiramtion.html" ,{
            'name': myuser.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token': generate_token.make_token(myuser)
        })
        email = EmailMessage(
        email_subject,
        message2,
        settings.EMAIL_HOST_USER,
        [myuser.email],
        )
        email.fail_silently = True
        email.send()
        
        return redirect('signin')


    return render(request, "Authentication/signup.html")

def signin(request):
    if request.method == "POST":
        username = request.POST['username']
        pass1 = request.POST['pass1']

        user = authenticate(username=username, password=pass1)

        if user is not None:
            login(request, user)
            fname = user.first_name
            return render(request, "authentication/index.html", {'fname': fname})

        else:
            messages.error(request, "Bad creadential")
            return redirect('home')

    return render(request, "authentication/signin.html")

def signout(request):
    logout(request)
    messages.success(request, "Logge out successfully")
    return redirect('home')

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None
    
    if myuser is not None and generate_token.check_token(myuser, token):
        myuser.is_active = True
        myuser.save()
        login(request, myuser)
        messages.success(request, "Your Account has been activated!!")
        return redirect('signin')
    else:
        return render (request, 'activation_failed.html')


#harsh.django.code@gmail.com
#Code@123
#admin
#123