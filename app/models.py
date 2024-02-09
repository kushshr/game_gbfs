import django
from django.db import models
from shortuuidfield import ShortUUIDField
import datetime

class TransportOperator(models.Model):
    uuid = ShortUUIDField(unique=True)
    name = models.CharField(max_length=30)
    display_name = models.CharField(max_length=30)

class Users(models.Model):
    uuid = ShortUUIDField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.CharField(max_length=30,unique=True)
    last_otp = models.CharField(max_length=8)
    last_login_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default = datetime.datetime.now())
    updated_at = models.DateTimeField(default = datetime.datetime.now())

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        super(Users, self).save(*args, **kwargs)

class UserAuth(models.Model):
    user = models.ForeignKey(Users,null=False, on_delete=models.CASCADE)
    token = models.CharField(max_length=256)
    created_at = models.DateTimeField(default = datetime.datetime.now())


class GameQuestions(models.Model):
    uuid = ShortUUIDField(unique=True)
    created_at = models.DateTimeField(default = datetime.datetime.now(), null= True)
    question_text = models.CharField(max_length=512, default = '')
    option1 = models.CharField(max_length=256, default = '')
    option2 = models.CharField(max_length=256, default = '')
    option3 = models.CharField(max_length=256, default = '')
    option4 = models.CharField(max_length=256, default = '')
    answer = models.CharField(max_length=256, default = '')

class UserGames(models.Model):
    uuid = ShortUUIDField(unique=True)
    user = models.ForeignKey(Users,null=False, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default = datetime.datetime.now())
    finished_at = models.DateTimeField(default = datetime.datetime.now())

class UserGameQnA(models.Model):
    uuid = ShortUUIDField(unique=True)
    user_game = models.ForeignKey(UserGames,null=False, on_delete=models.CASCADE)
    question = models.ForeignKey(GameQuestions,null=False, on_delete=models.CASCADE)
    actual_answer = models.CharField(max_length=256)
    user_answer = models.CharField(max_length=256)
    option1 = models.CharField(max_length=256)
    option2 = models.CharField(max_length=256)
    option3 = models.CharField(max_length=256)
    option4 = models.CharField(max_length=256)
    created_at = models.DateTimeField(default = datetime.datetime.now())
    updated_at = models.DateTimeField(default = datetime.datetime.now())

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        super(UserGameQnA, self).save(*args, **kwargs)

    def embed(self):
        return {
            'uuid':self.uuid,
            'user_game_id':self.user_game.uuid,
            'question_id':self.question_id,
            'actual_answer':self.actual_answer,
            'user_answer':self.user_answer,
            'option1':self.option1,
            'option2':self.option2,
            'option3':self.option3,
            'option4':self.option4
        }



