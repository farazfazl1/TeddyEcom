from django.shortcuts import render, redirect
from .forms import RegistrationForm
from .models import Account
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required

# Verification Email

from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage


@login_required(login_url='users:login-user')
def dashboard(req):
    return render(req, 'pages/dashboard.html')


def register_user(req):
    if req.method == 'POST':
        form = RegistrationForm(req.POST)
        if form.is_valid():
            # cleaned data is for django model forms
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            username = email.split("@")[0]

            user = Account.objects.create_user(first_name=first_name,
                                               last_name=last_name,
                                               email=email,
                                               username=username, password=password)
            user.phone_number = phone_number
            user.save()

            # USER ACTIVATION
            current_site = get_current_site(req)
            mail_subject = 'From TeddyEcom: Please activate your account'
            message = render_to_string('emails/account_verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user)
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(
                req, 'Thank you for Registration. We have sent you an email to Verify your Account ✔')
            print(user)
            return redirect('users:register-user')
    else:
        form = RegistrationForm()
    context = {
        'form': form,
    }

    return render(req, 'users/registration.html', context)


def login_user(req):
    if req.method == 'POST':
        email = req.POST['email']
        password = req.POST['password']

        # this method will authenticate the written password and email to db and chekc if they match
        user = auth.authenticate(email=email, password=password)

        if user is not None:
            auth.login(req, user)
            messages.success(req, "You are now logged in ✔")
            return redirect('users:dashboard')
        else:
            messages.error(req, 'Invalid Email/Password ❌')
            return redirect('users:login-user')

    return render(req, 'users/login.html')


@login_required
def logout_user(req):
    auth.logout(req)
    messages.success(req, 'You are logged out 💪🏽')
    return redirect('users:login-user')


def activate(req, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)

    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(req, 'Account successfully Activated 💚')
        return redirect('users:login-user')
    else:
        messages.error(req, 'Invalid Activation Link')
        return redirect('users:register-user')


def forgotPassword(req):
    if req.method == 'POST':
        email = req.POST['email']

        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__iexact=email)

            # RESET PASSWORD EMAIL
            current_site = get_current_site(req)
            mail_subject = 'Reset Your Password'
            message = render_to_string('emails/forgot_password.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user)
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(
                req, f'Password Recovery Link has been sent to {email}')
            return redirect('users:login-user')

        else:
            messages.error('Email does not exist in our System ⚠')
            return redirect('users:forgot-password')
    return render(req, 'users/forgotPassword.html')


def reset_password_validate(req, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        req.session['uid'] = uid
        messages.success(req, 'Please Reset your password')
        return redirect('users:reset-password-page')
    else:
        messages.error(req, 'This link is expired. Try again')
        return redirect('users:forgot-password')


def reset_password_page(req):
    if req.method == 'POST':
        password = req.POST['password']
        confirm_password = req.POST['confirm_password']

        if password == confirm_password:
            uid = req.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(req, 'Your password was successfuly reset ✔')
            return redirect('users:login-user')

        else:
            messages.error(req, 'Passwords do not match')
            return redirect('users:reset-password-page')
    return render(req, 'users/resetPassword.html')
