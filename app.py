"""
Primary app code. Listens to email and processes submissions
"""
import logging
from flask import request
from app import create_app
from vidb.models import db, User, Token, Question, Answer, Result, ResultComponent, ResultSubComponent, \
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


if __name__ == '__main__':
    app.run(host=app.config['WWWHOST'],
            port=app.config['WWWPORT'])