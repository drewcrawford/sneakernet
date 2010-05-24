#!/usr/bin/env python
from google.appengine.ext import db
class Team(db.Model):
    name = db.StringProperty(required = True)
    invites = db.IntegerProperty(default=0)
class Invite(db.Model):
    team = db.ReferenceProperty(reference_class=Team,required=True)
    email = db.EmailProperty(required=True)
def get_team_for_team_leader(user):
    if not user.team_leader_flag:
        raise Exception("You're not a team leader!")
    return user.team
def invite_person(user,email):
    if user.team.invites<=0:
        raise Exception("All invites are used, sorry...")
    user.team.invites -= 1
    user.team.put()
    i = Invite(team=user.team,email=email)
    i.put()
    from mail import send_mail
    from magic import BASE_URL
    send_mail(to=email,subject="Welcome to the sneakernet!",msg="""
              Dear lucky user,
              
              You are cordially invited to the sneakernet.
              
              To accept this invitation, use the link below:
              %s
              
              Thanks,
              
              %s
              """ % (BASE_URL + "accept_invite?code="+str(i.key()),user.name))
    
    