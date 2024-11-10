import imaplib

from django.contrib.auth import login as auth_login
from django.shortcuts import render
from rest_framework_simplejwt.tokens import RefreshToken
from .forms import UserRegister, UserLogin
from .models import User

# Create your views here.



def index(request):
    return render(request, 'main.html')


def sign_up_by_django(request):
    info = {'error': []}
    if request.method == "POST":
        is_corect = True
        form = UserRegister(request.POST)
        if form.is_valid():
            login = form.cleaned_data["login"]
            password = form.cleaned_data["password"]
            repeat_password = form.cleaned_data["repeat_password"]
            mail_pass = form.cleaned_data["mail_pass"]
        username = request.POST.get("login")
        user = User.objects.filter(name__contains=username).count()
        print(user)
        if user > 0:
            is_corect = False
            info['error'].append('Пользователь уже существует')
        if username.find('@gmail.com') >= 0:
            imap_server = "imap.gmail.com"
        elif username.find('@yandex.ru') >= 0:
            imap_server = "imap.yandex.ru"
        elif username.find('@mail.ru') >= 0:
            imap_server = "imap.mail.ru"
        else:
            is_corect = False
            info['error'].append('Почта должна заканчиваться на @gmail.com, @yandex.ru или @mail.ru')
        mail_pass = request.POST.get("mail_pass")
        try:
            imap = imaplib.IMAP4_SSL(imap_server)
            imap.login(username, mail_pass)
        except:
            is_corect = False
            info['error'].append(
                'Неверный пороль IMAP или нет доступа со стороны почты, проверте включена ли у вас настройки на почте')

        password = request.POST.get("password")
        repeat_password = request.POST.get("repeat_password")
        if password != repeat_password:
            is_corect = False
            info['error'].append('Пароли не совпадают')
        if is_corect:
            User.objects.create(name=username, password=password, mail_pass=mail_pass, imap_server=imap_server)
            return render(request, 'main.html', {"form": form, 'info': info, 'text': 'Регестрация прошла'})
    else:
        form = UserRegister()
    return render(request, "registration.html", {"form": form, 'info': info})


def login_up_by_django(request):
    info = {'error': []}
    if request.method == "POST":
        is_corect = True
        form = UserLogin(request.POST)
        if form.is_valid():
            login = form.cleaned_data["login"]
            password = form.cleaned_data["password"]
        login = request.POST.get("login")
        print(login)
        password = request.POST.get("password")
        user_queritiset = User.objects.filter(name__contains=login)
        user = user_queritiset.first()
        print(user)
        if user == 0:
            is_corect = False
            info['error'].append('Пользователя не существует')
        password = request.POST.get("password")
        password = User.objects.filter(password__contains=password).count()
        if password == 0:
            is_corect = False
            info['error'].append('Пароли не совпадают')
        if is_corect:
            # Генерация токена
            refresh = RefreshToken.for_user(user)
            token = str(refresh.access_token)

            user_queritiset.update(auth_token=token)

            auth_login(request, user)
            print(token)
            return render(request, 'import_email.html', {"user": user, 'info': info, 'token': token})
    else:
        form = UserLogin()
    return render(request, "login.html", {"form": form, 'info': info})
