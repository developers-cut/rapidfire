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
        user = users.get_current_user()
        feedback = new_feedback(user, self.request.get('content'))
        template_values = {
            'feedback': feedback
        }

        template = JINJA_ENVIRONMENT.get_template('feedback.html')
        self.response.write(template.render(template_values))

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
        email_subscribers(user.email(), 'Edit in feedback', feedback.content)


class SubscribeHandler(webapp2.RequestHandler):
    def put(self):
        user = users.get_current_user()

        q = Account.query(Account.user == user)
        account = q.get()
        account.subscribed = not account.subscribed
        account.put()


class LogSenderHandler(InboundMailHandler):
    def receive(self, mail_message):
        clean_email = mail_message.sender[mail_message.sender.find('<')+1:
                                          mail_message.sender.find('>')]
        account = Account.query(Account.user == users.User(email=clean_email),
                                Account.subscribed == True).get()
        if account:
            new_feedback(account.user, get_clean_body(mail_message))


def email_subscribers(from_email, subject, content):
    subscribers = Account.query(Account.subscribed == True).fetch()
    emails = []
    for subscriber in subscribers:
        if from_email != subscriber.user.email():
            emails.append(subscriber.user.email())

    if emails:
        mail.send_mail(from_email, emails, subject, content)


def new_feedback(user, content):
    feedback = Feedback(author=user, content=content, archived=False)
    feedback.put();
    email_subscribers(user.email(), 'New feedback', feedback.content)
    return feedback


# From:
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
