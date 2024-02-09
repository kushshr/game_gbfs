from __future__ import unicode_literals

import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.views.decorators.csrf import csrf_exempt

from django.shortcuts import render,HttpResponse
from random import randrange
import smtplib, json, uuid
from app.models import *
from game_gbfs.settings import MAILGUN_API_KEY

def value_from_req(request,key,default):
    value = getattr(request, 'GET').get(key)
    if not value:
        value = getattr(request, 'POST').get(key)
    if not value:
        return default
    return value

def create_game(request):
    token = value_from_req(request, 'token', '')
    email = value_from_req(request, 'email', '')

    if not token:
        return HttpResponse(json.dumps({"msg": "Bad request"}))
    if not email:
        return HttpResponse(json.dumps({"msg": "Bad request"}))

    user_auth = UserAuth.objects.filter(token=token).first()
    if not user_auth:
        return HttpResponse(json.dumps({"msg": "User not authenticated"}))

    game_qs = GameQuestions.objects.filter().order_by('?')
    user = user_auth.user
    user_game = UserGames()
    user_game.user = user
    user_game.save()

    qs = []
    print (game_qs)
    for game_q in game_qs:
        user_game_qna = UserGameQnA()
        user_game_qna.user_game = user_game
        user_game_qna.actual_answer = game_q.answer
        user_game_qna.question = game_q
        user_game_qna.option1 = game_q.option1
        user_game_qna.option2 = game_q.option2
        user_game_qna.option3 = game_q.option3
        user_game_qna.option4 = game_q.option4
        user_game_qna.save()
        qs.append({"question_id":game_q.uuid,
            "question": game_q.question_text,
                         "optionA": game_q.option1,
                         "optionB": game_q.option2,
                         "optionC": game_q.option3,
                         "optionD": game_q.option4,
                         })
    response = {"questions": qs,
                "game_id": user_game.uuid}
    return HttpResponse(json.dumps(response))

@csrf_exempt
def evaluate_game(request):
    #Decode user token

    token = value_from_req(request, 'token', '')

    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    print (body)
    content = body
    game_id = value_from_req(request, 'game_id', '')

    if not token:
        return HttpResponse(json.dumps({"msg": "Bad request"}))

    user_auth = UserAuth.objects.filter(token=token).first()
    if not user_auth:
        return HttpResponse(json.dumps({"msg": "User not authenticated"}))

    user_game = UserGames.objects.filter(uuid=game_id).first()
    if not user_game:
        return HttpResponse(json.dumps({"msg":'no game found'}))

    if not user_auth.user == user_game.user:
        return HttpResponse(json.dumps({"msg": "User not authorized"}))

    answers = content
    print (answers)
    count = 0
    result = {}
    summary = []
    for answer in answers:
        game_q = GameQuestions.objects.filter(uuid = answer.get('question_id','')).first()
        question_uuid = game_q.uuid
        user_game_qna = UserGameQnA.objects.filter(question = game_q, user_game = user_game).first()
        if not user_game_qna:
            return HttpResponse(json.dumps({"msg":"no ugqna"}))
        if answer.get('answer','') == user_game_qna.actual_answer:
            count = count + 50
        else:
            count = count - 20
        user_game_qna.user_answer = answer.get('answer','')
        user_game_qna.save()
        summary.append(user_game_qna.embed())

    result['summary'] = summary
    result['count'] = count
    return HttpResponse(json.dumps(result))

@csrf_exempt
def check_otp(request):
    email = value_from_req(request, 'email', '')
    otp = value_from_req(request, 'otp', '')

    u = Users.objects.filter(email=email).first()
    if not u:
       return HttpResponse(json.dumps(default_response(msg = 'no such user')))
    else:
        if str(otp) == u.last_otp:
            #Grant token
            u.last_login_at = datetime.datetime.now()
            u.save()

            user_auth = UserAuth.objects.filter(user=u).order_by('-created_at').first()
            if not user_auth:
                user_auth = UserAuth()
                user_auth.user = u
                token = uuid.uuid4()
                user_auth.created_at = datetime.datetime.now()
                user_auth.token = token
                user_auth.save()

            return HttpResponse(json.dumps({"msg":'yes login'}))
        else:
            return HttpResponse(json.dumps({"msg":'otp wrong'}))

def default_response(status=True,data={},msg='',login=True):
    if status:
        return {'status':status,'response':data,'login':login}
    else:
        return {'status':status,'msg':msg,'login':login}

# Create your views here.
def index(request):
    return render(request,'index.html', locals())

@csrf_exempt
def create_account(request):
    first_name = value_from_req(request,'first_name','')
    last_name = value_from_req(request,'last_name','')
    email = value_from_req(request,'email','')
    user = Users.objects.filter(email=email).first()

    if user:
        return HttpResponse(json.dumps({"msg":"Account exists"}))
    else:
        otp = calculate_otp()
        user = Users()
        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.last_otp = otp
        user.save()

        send_simple_message(user.email, first_name, otp)
        return HttpResponse(json.dumps(default_response(msg='created')))

@csrf_exempt
def login(request):
    email = value_from_req(request,'email','')
    user = Users.objects.filter(email=email).first()
    if user:
        otp = calculate_otp()
        user.last_otp = otp
        user.save()
        send_simple_message(user.email, user.first_name, otp)
        return HttpResponse(json.dumps({'status':200,'response': {},'login':False}))
    else:
        return HttpResponse(json.dumps({'status':404,'response': {},'login':False}))

def calculate_otp():
    return randrange(100000, 999999)

def send_simple_message(recipient, name, otp):
    import requests
    print (MAILGUN_API_KEY)
    x = requests.post(
        "https://api.mailgun.net/v3/sandboxe57e9486bb554d7990bcdb1d4904734d.mailgun.org/messages",
        auth=("api", MAILGUN_API_KEY),
        data={
            "from": "Mailgun Sandbox <postmaster@sandboxe57e9486bb554d7990bcdb1d4904734d.mailgun.org>",
                "to": recipient,
                "subject": "Hello " + name + ",\n" ,
                "text": str(otp)})
    if x.status_code!=200:
        print (x.content)
    print (x.status_code)