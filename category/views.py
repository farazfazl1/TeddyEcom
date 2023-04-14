from django.shortcuts import render


def category(req):
    return render(req, 'pages/home.html')
