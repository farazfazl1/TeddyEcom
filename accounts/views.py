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
    """
    This function is responsible for registering a new user with the system. If the user submits a valid registration
    form, a new user account will be created, the user will receive an email to verify their account, and the user will be
    redirected to the login page. If the user submits an invalid registration form, an error message will be displayed.

    The function first checks if the request method is POST. If so, it creates a new instance of the RegistrationForm
    class using the data submitted by the user. It then checks if the form data is valid. If the form is valid, it creates
    a new user object using the data from the form, and sends an email to the user to verify their account. If the form
    is not valid, it simply displays the registration form with the errors highlighted.

    Once a user has been successfully registered, they will be redirected to the login page.
    """
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

            # create a new user object using the data from the form
            user = Account.objects.create_user(first_name=first_name,
                                               last_name=last_name,
                                               email=email,
                                               username=username, password=password)
            user.phone_number = phone_number
            user.save()

            # send an email to the user to verify their account
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

            # display success message and redirect to login page
            messages.success(
                req, 'Thank you for Registration. We have sent you an email to Verify your Account ✔')
            print(user)
            return redirect('users:register-user')
    else:
        form = RegistrationForm()
    context = {
        'form': form,
    }

    # display registration form
    return render(req, 'users/registration.html', context)


def login_user(req):
    if req.method == 'POST':
        # Retrieve the email and password submitted in the login form
        email = req.POST['email']
        password = req.POST['password']

        # Check if the email and password match a user in the database using Django's built-in authentication system
        user = auth.authenticate(email=email, password=password)

        if user is not None:
            # If the user is found, log them in using Django's built-in login method
            auth.login(req, user)
            # Display a success message using Django's built-in messages framework
            messages.success(req, "You are now logged in ✔")
            # Redirect the user to their dashboard page
            return redirect('users:dashboard')
        else:
            # If the user is not found or the password is incorrect, display an error message and redirect back to the login page
            messages.error(req, 'Invalid Email/Password ❌')
            return redirect('users:login-user')

    # If the user is not submitting the login form, display the login form using the template
    return render(req, 'users/login.html')

# this decorator will check if the user is authenticated before accessing the view


@login_required
def logout_user(req):
    # logs out the user
    auth.logout(req)
    # displays a success message
    messages.success(req, 'You are logged out 💪🏽')
    # redirects to the login page
    return redirect('users:login-user')


def activate(req, uidb64, token):
    try:
        # decodes the user id from base64
        uid = urlsafe_base64_decode(uidb64).decode()
        # retrieves the user with the given id
        user = Account._default_manager.get(pk=uid)

    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        # if an error occurs while decoding the id or no user is found, set user to None
        user = None
    # checks if user is not None and the given token is valid
    if user is not None and default_token_generator.check_token(user, token):
        # activates the user account
        user.is_active = True
        user.save()
        # displays a success message
        messages.success(req, 'Account successfully Activated 💚')
        # redirects to the login page
        return redirect('users:login-user')
    else:
        # if either user is None or the token is invalid, displays an error message
        messages.error(req, 'Invalid Activation Link')
        # redirects to the register page
        return redirect('users:register-user')


def forgotPassword(req):
    if req.method == 'POST':
        email = req.POST['email']

        # Check if the email exists in the database
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__iexact=email)

        # Generate password reset email with a unique token
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

            # Show success message and redirect to login page
            messages.success(
                req, f'Password recovery link has been sent to {email}')
            return redirect('users:login-user')

        else:
            # Show error message and redirect back to forgot password page
            messages.error(req, 'Email does not exist in our system')
            return redirect('users:forgot-password')

    # Render the forgot password form
    return render(req, 'users/forgotPassword.html')


# validate reset password link
def reset_password_validate(req, uidb64, token):
    try:
        # decode uidb64 and retrieve user account associated with uid
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    # check if user account exists and the token is valid
    if user is not None and default_token_generator.check_token(user, token):
        # store uid in session to be used to reset the password
        req.session['uid'] = uid
        messages.success(req, 'Please reset your password')
        return redirect('users:reset-password-page')
    else:
        messages.error(req, 'This link is expired. Please try again.')
        return redirect('users:forgot-password')


# render reset password page
def reset_password_page(req):
    if req.method == 'POST':
        password = req.POST['password']
        confirm_password = req.POST['confirm_password']

        if password == confirm_password:
            # retrieve uid from session and retrieve user account
            uid = req.session.get('uid')
            user = Account.objects.get(pk=uid)
            # set the new password and save the user account
            user.set_password(password)
            user.save()
            messages.success(req, 'Your password was successfully reset ✔')
            return redirect('users:login-user')

        else:
            messages.error(req, 'Passwords do not match')
            return redirect('users:reset-password-page')

    return render(req, 'users/resetPassword.html')
#contributed April 26th
