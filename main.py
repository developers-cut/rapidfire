#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


import datetime
import os
import urllib

import jinja2
import webapp2

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.api import mail

from google.appengine.ext.webapp.mail_handlers import InboundMailHandler


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class Account(ndb.Model):
    subscribed = ndb.BooleanProperty()
    user = ndb.UserProperty()

class Feedback(ndb.Model):
    author = ndb.UserProperty()
    content = ndb.StringProperty(indexed=False)
    archived = ndb.BooleanProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)


class MainHandler(webapp2.RequestHandler):
    def get(self):
        feedbacks = Feedback.query().order(-Feedback.date)
        user = users.get_current_user()

        q = Account.query(Account.user == user)
        account = q.get()

        if not account:
            account = Account(user=user, subscribed=False)
            account.put()

        template_values = {
            'feedbacks': feedbacks,
            'account': account,
            'user': user
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))


class FeedbackHandler(webapp2.RequestHandler):
    def post(self):
        feedback = Feedback(author=users.get_current_user(),
                            content=self.request.get('content'),
                            archived=False)
        feedback_key = feedback.put();

        template_values = {
            'feedback': feedback
        }

        template = JINJA_ENVIRONMENT.get_template('feedback.html')
        self.response.write(template.render(template_values))

        user = users.get_current_user()
        subscribers = Account.query(Account.subscribed == True).fetch()
        emails = []
        for subscriber in subscribers:
            if user.email() != subscriber.user.email():
                emails.append(subscriber.user.email())

        if emails:
            mail.send_mail(user.email(), emails, 'New feedback',
                           feedback.content)

    def delete(self):
        feedback_key = ndb.Key(urlsafe=self.request.get('key'))
        feedback_key.delete()

    def put(self):
        feedback_key = ndb.Key(urlsafe=self.request.get('key'))
        feedback = feedback_key.get()
        feedback.content = self.request.get('content')
        feedback.date = datetime.datetime.now()
        feedback.put();

        user = users.get_current_user()
        subscribers = Account.query(Account.subscribed == True).fetch()
        emails = []
        for subscriber in subscribers:
            if user.email() != subscriber.user.email():
                emails.append(subscriber.user.email())

        if emails:
            mail.send_mail(user.email(), emails, 'Edit in feedback',
                           feedback.content)


class SubscribeHandler(webapp2.RequestHandler):
    def put(self):
        user = users.get_current_user()

        q = Account.query(Account.user == user)
        account = q.get()
        account.subscribed = not account.subscribed
        account.put()


class LogSenderHandler(InboundMailHandler):
    def receive(self, mail_message):
        clean_email = main_message.sender[mail_message.sender.find('<')+1:
                                          mail_message.sender.find('>')]
        user = Account.query(Account.user.email() == clean_email,
                             Account.subscribed == True).get()
        if user:
            feedback = Feedback(author=user,
                                content=get_clean_body(mail_message),
                                archived=False)
            feedback_key = feedback.put();


# https://github.com/dustingetz/foodlog/blob/master/logfood/handle_incoming_email.py
def get_clean_body(email):
    bodies = email.bodies(content_type='text/plain')

    allBodies = ""; numBodies=0
    for body in bodies:
        allBodies = allBodies + body[1].decode()
        numBodies += 1
        if isinstance(allBodies, unicode):
            allBodies = allBodies.encode('utf-8')

    if numBodies > 1: logging.warn("recvd mail with %s bodies: %s" % (numBodies, email))
    return allBodies

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/feedback', FeedbackHandler),
    ('/subscribe', SubscribeHandler),
    LogSenderHandler.mapping()
], debug=True)
