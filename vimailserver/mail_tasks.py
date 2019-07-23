import logging
from email.message import EmailMessage
from typing import Dict
import smtplib
from vidb.models import *

from celery_config import celery, mailuser, mailsvr, mailpwd

def build_reminder_mail(name: str, index_id: str, counts: Dict[str, Dict[str, int]]) -> EmailMessage:
    msg = EmailMessage()

    # set the plain text body
    text = """
        Hello {name}!

        This is a friendly reminder from VIINC. Here is a report on your interaction 
        with our data entry process. The more questions you answer and the more 
        frequently you update your answers the better your Vitality Index will 
        represent your current state of health and well-being.

        Total Questions answered: {tanswered}/{ttotal}

        Medical: {manswered}/{mtotal}
        Nutrition: {nanswered}/{ntotal}
        Exercise: {eanswered}/{etotal}
        Perception: {panswered}/{ptotal}
        Social: {sanswered}/{stotal}

        Thank you and please come back to http://www.vitalityindex.com often.
    

        Be Healthy | Be Happy | Be Your Best
    """.format(name=name,
               tanswered=counts[index_id]['answered'], ttotal=counts[index_id]['total'],
               manswered=counts['MEDICAL']['answered'], mtotal=counts['MEDICAL']['total'],
               nanswered=counts['NUTRITION']['answered'], ntotal=counts['NUTRITION']['total'],
               eanswered=counts['EXERCISE']['answered'], etotal=counts['EXERCISE']['total'],
               panswered=counts['PERCEPTION']['answered'], ptotal=counts['PERCEPTION']['total'],
               sanswered=counts['SOCIAL']['answered'], stotal=counts['SOCIAL']['total'])
    msg.set_content(text)
    html = """
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Hello</title>
        </head>
        <body>
        <h1>Hello {name}!</h1>
        <p>This is a friendly reminder from VIINC. Here is a report on your interaction with our data entry
            process. The more questions you answer and the more frequently you update your answers the better
            your Vitality Index will represent your current state of health and well-being.
        </p>
        <table>
            <tr><td>Total Questions answered:</td><td>{tanswered}/{ttotal}</td></tr>
            <tr></tr>
            <tr><td>Medical:</td><td>{manswered}/{mtotal}</td></tr>
            <tr><td>Nutrition:</td><td>{nanswered}/{ntotal}</td></tr>
            <tr><td>Exercise:</td><td>{eanswered}/{etotal}</td></tr>
            <tr><td>Perception:</td><td>{panswered}/{ptotal}</td></tr>
            <tr><td>Social:</td><td>{sanswered}/{stotal}</td></tr>

        </table>
        <p>Thank you and please come back to our <a href="http://www.vitalityindex.com">website</a> often.
        </p>
        <h2>Be Healthy | Be Happy | Be Your Best</h2>
        </body>
        </html>
    """.format(name=name,
               tanswered=counts[index_id]['answered'], ttotal=counts[index_id]['total'],
               manswered=counts['MEDICAL']['answered'], mtotal=counts['MEDICAL']['total'],
               nanswered=counts['NUTRITION']['answered'], ntotal=counts['NUTRITION']['total'],
               eanswered=counts['EXERCISE']['answered'], etotal=counts['EXERCISE']['total'],
               panswered=counts['PERCEPTION']['answered'], ptotal=counts['PERCEPTION']['total'],
               sanswered=counts['SOCIAL']['answered'], stotal=counts['SOCIAL']['total'])
    msg.add_alternative(html, subtype='html')
    return msg


def build_welcome_mail(name: str) -> EmailMessage:
    msg = EmailMessage()

    # set the plain text body
    text = """
        Welcome!

        Congratulations {name} and welcome to VIINC and the path to a happier you!
        HAPPINESS - we all strive for it. But it seems we are pretty bad at achieving it. In fact
        what is it? Many of the things we intuitively think bring happiness in fact do not. It’s one
        of those things we think we know what it is but have a hard time describing and an even
        harder time living.

        Our mission is to help you change that. It is an ambitious goal but we are passionate
        about it. We are also science and technology driven and luckily great strides have been
        made in both fields. We are leveraging tools and insights from various scientific
        disciplines and combine them in a holistic and highly individualized approach. Happiness
        after all is an intensely holistic emotion that depends on physical and mental factors -
        and it is also intensely personal.

        Despite the advances in science and technology there is still a lot that is not yet known
        or well understood and part of our mission is to advance the science of happiness and
        share our insights with our community of users. Happiness has been directly linked to
        health and longevity and vice versa. Helping you improve, no matter how much or little,
        holds the promise of significantly impacting your life and the happiness and health of
        society as a whole.

        But where to start? You have taken a critical first step by registering on our website and
        answering the first 20 questions. The data we collect through these questions serves to
        establish a holistic and highly personalized base line for your Vitality Index (VI) Score.
        The Vitality Index provides a snapshot of your current state of happiness, health and
        well-being. It breaks it down into five dimensions. Combined these dimensions
        provide the basis for holistic health and with that the foundation for happiness and well-
        being.

        You can also see how you stack up to others. Enjoy the insight!

        Now, here is where we need YOUR help. We are a young company and we are just
        getting started with an ambitious vision to help people live happier, healthier and more
        fulfilled lives. We have great ideas how to put novel science and technology to work for
        all of us. In doing so, we are keenly interested in your feedback to guide our future
        development efforts. So please help us by filling out a short questionnaire.

        http://www.123formbuilder.com/form-4093826/user-survey

        Thank you and please come back to our https://www.vitalityindex.com often
        to answer more questions and update ones you have already answered. The more questions 
        you answer and the more frequently you update your answers the better the Vitality Index 
        will reflect your current state of well-being.

        Be Healthy | Be Happy | Be Your Best
    """.format(name=name)
    msg.set_content(text)
    html = """
        <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>Welcome</title>
            </head>
            <body>
            <h1>Welcome!</h1>
            <p>Congratulations {name} and welcome to VIINC and the path to a happier you!
                HAPPINESS - we all strive for it. But it seems we are pretty bad at achieving it. In fact
                what is it? Many of the things we intuitively think bring happiness in fact do not. It’s one
                of those things we think we know what it is but have a hard time describing and an even
                harder time living.
            </p>
            <p>Our mission is to help you change that. It is an ambitious goal but we are passionate
                about it. We are also science and technology driven and luckily great strides have been
                made in both fields. We are leveraging tools and insights from various scientific
                disciplines and combine them in a holistic and highly individualized approach. Happiness
                after all is an intensely holistic emotion that depends on physical and mental factors -
                and it is also intensely personal.
            </p>
            <p>Despite the advances in science and technology there is still a lot that is not yet known
                or well understood and part of our mission is to advance the science of happiness and
                share our insights with our community of users. Happiness has been directly linked to
                health and longevity and vice versa. Helping you improve, no matter how much or little,
                holds the promise of significantly impacting your life and the happiness and health of
                society as a whole.
            </p>
            <p>But where to start? You have taken a critical first step by registering on our website and
                answering the first 20 questions. The data we collect through these questions serves to
                establish a holistic and highly personalized base line for your Vitality Index (VI) Score.
                The Vitality Index provides a snapshot of your current state of happiness, health and
                well-being. It breaks it down into five dimensions. Combined these dimensions
                provide the basis for holistic health and with that the foundation for happiness and well-
                being.
            </p>
            <p>You can also see how you stack up to others. Enjoy the insight!
            </p>
            <p>Now, here is where we need YOUR help. We are a young company and we are just
                getting started with an ambitious vision to help people live happier, healthier and more
                fulfilled lives. We have great ideas how to put novel science and technology to work for
                all of us. In doing so, we are keenly interested in your feedback to guide our future
                development efforts. So please help us by filling out a short questionnaire.
                <br><br>
                <a href="http://www.123formbuilder.com/form-4093826/user-survey">User Survey</a>
            </p>
            <p>Thank you and please come back to our <a href="https://www.vitalityindex.com">website</a> often
                to answer more questions and update ones you
                have already answered. The more questions you answer and the more frequently you update your answers
                the better the Vitality Index will reflect your current state of well-being.
            </p>
            <h2>Be Healthy | Be Happy | Be Your Best</h2>
            </body>
        </html>
    """.format(name=name)
    msg.add_alternative(html, subtype='html')
    return msg


def build_reset_mail(url: str, token) -> EmailMessage:
    msg = EmailMessage()

    # set the plain text body
    text = """
    You have made a request to reset your password at vitalityindex.com. Cut and paste this link into your browser
    to be taken to a password reset page. This link will only be valid for 30 minutes.
    {url}
    """.format(url=url).format(token=token)
    msg.set_content(text)

    # set an alternative html body
    html = """
    <html>
    <body lang="en-US" dir="ltr">
    <p>
        You have made a request to reset your password at vitalityindex.com. Click on this link to
        be taken to a password reset page. This link will only be valid for 30 minutes.
    </p>
    <p>
        <a href="{url}">Password Reset</a></p>
    </p>
    </body>
    </html>
    """.format(url=url).format(token=token)
    msg.add_alternative(html, subtype='html')
    return msg


def sendmail(email, msg):
    # me == the sender's email address
    # you == the recipient's email address
    me = mailuser
    you = email

    # the message is ready now
    print("sending email to %s" % (email, ))
    # print(msg.as_string())
    try:
        logging.debug("connecting to %s as %s" % (mailsvr, mailuser))
        server = smtplib.SMTP(mailsvr, 587)
        server.starttls()
        server.login(mailuser, mailpwd)
    except smtplib.SMTPException as me:
        logging.error("error connecting to SMTP server")
        raise me
    try:
        server.sendmail(me, you, msg.as_string())
        server.quit()
    except smtplib.SMTPException as me:
        logging.error("error sending email")
        raise me


@celery.task(name='mail_tasks.send_welcome')
@db_session
def send_welcome(user_id: int):

    user = User[user_id]
    # me == the sender's email address
    # you == the recipient's email address
    me = mailuser
    you = user.email

    msg = build_welcome_mail(user.first_name)

    # generic email headers
    msg['Subject'] = 'Vitality Index welcome'
    msg['From'] = me
    msg['To'] = you

    sendmail(you, msg)
    user.last_notification = datetime.utcnow()


@celery.task(name='mail_tasks.send_reminder')
@db_session
def send_reminder(user_id: int, index_id: str, counts: Dict[str, Dict[str, int]]):

    user = User[user_id]

    # me == the sender's email address
    # you == the recipient's email address
    me = mailuser
    you = user.email

    msg = build_reminder_mail(user.first_name, index_id, counts)

    # generic email headers
    msg['Subject'] = 'Vitality Index update'
    msg['From'] = me
    msg['To'] = you

    sendmail(you, msg)
    user.last_notification = datetime.utcnow()


@celery.task(name='mail_tasks.send_password_reset')
def send_password_reset(email: str, url: str, token):

    # me == the sender's email address
    # you == the recipient's email address
    me = mailuser
    you = email

    msg = build_reset_mail(url, token)

    # generic email headers
    msg['Subject'] = 'Vitality Index password reset'
    msg['From'] = me
    msg['To'] = you

    sendmail(you, msg)
    