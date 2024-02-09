**Usage**
1. Create a file .env in game_gbfs directoy.  
2. Fill in the variables from .env.sample in .env.
3. Install requirements.
4. Runserver! 

```
  touch /path/to/game_gbfs.env
  pip install -r /path/to/requirements.txt
  python manage.py runserver
```

**User journey**

1. A user is created with their first_name, last_name and email. An OTP is sent to the user's email.
2. The user recieves the otp and after successfull verification, a token is returned.
3. The user creates a game and receives questions and options.
4. The user answers the questions and receives the result as well as the correct answers to their questions. 
