# coding: utf-8
import sqlalchemy as sa
from basemodels import BaseMixin
class M(BaseMixin):
    name = sa.Column(sa.String(255),nullable=False)
    
from flask import Flask
app = Flask(__name__)
app.test_request_context().push()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
