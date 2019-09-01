"""
Primary app code. Listens to email and processes submissions
"""
import logging
from flask import request
from app import create_app, db
from vidb.models import User, Token, Question, Answer, Result, ResultComponent, ResultSubComponent, \
    Index, IndexComponent, IndexSubComponent


app = create_app()


@app.before_request
def before_request():
    # log actual full url of each call
    # saves having to correlate with uwsgi server logs
    logging.info("handling request to %s", request.url)


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Token': Token,
            'Question': Question, 'Answer': Answer,
            'Result': Result, 'ResultComponent': ResultComponent, 'ResultSubComponent': ResultSubComponent,
            'Index': Index, 'IndexComponent': IndexComponent, 'IndexSubComponent': IndexSubComponent
            }
