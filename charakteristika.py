#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, Blueprint
app = Flask(__name__)

from flask import render_template, url_for, redirect
from flask import request, Request
from flask import Response
from werkzeug.exceptions import BadRequest
from werkzeug.datastructures import OrderedMultiDict
from werkzeug.routing import BaseConverter
import re
import os
from deform import Form
from deform.exception import ValidationFailure
import json
import os
import os.path

class MyRequest(Request):
  parameter_storage_class = OrderedMultiDict

app.request_class = MyRequest

from schema import Charakteristika

if 'CHARAKTERISTIKA_DEBUG' in os.environ:
  app.debug = True

from local_settings import active_config
config = active_config(app)
app.secret_key = config.secret

deform_bp = Blueprint('deform', 'deform', static_folder='static', url_prefix='/deform')
app.register_blueprint(deform_bp)

class FormTokenConverter(BaseConverter):
  def __init__(self, url_map, *items):
    super(FormTokenConverter, self).__init__(url_map)
    self.regex = r'[A-Za-z0-9]{32}'

app.url_map.converters['token'] = FormTokenConverter

@app.route('/', methods=['POST', 'GET'])
def index():
  user = request.remote_user
  if not user:
    return render_template('login.html')
  return show_form('user-{}'.format(user))

@app.route('/login')
def login():
  return redirect(url_for('index'))

@app.route('/<token:token>', methods=['POST', 'GET'])
def using_token(token):
  return show_form('token-{}'.format(token), {'token':token})

def save_form(data, filename):
  filepath = os.path.join(config.document_dir, '{}.json'.format(filename))
  tmpfilepath = os.path.join(config.document_dir, '{}.json.part'.format(filename))
  try:
    with open(tmpfilepath, 'w+') as f:
      json.dump(data, f)
      f.flush()
      os.fsync(f.fileno())
    os.rename(tmpfilepath, filepath)
  except:
    try:
      os.unlink(tmpfilepath)
    except:
      pass

def load_form(filename):
  filepath = os.path.join(config.document_dir, '{}.json'.format(filename))
  try:
    with open(filepath, 'r') as f:
      return json.load(f)
  except IOError, e:
    if e.errno == 2: # neexistuje
      return None
    else:
      raise

def show_form(filename, metadata={}):
  loaded = load_form(filename)
  if loaded == None:
    data = {}
  else:
    data = loaded['form']
  form = Form(Charakteristika(), buttons=('submit',), appstruct=data)
  if request.method == 'POST':
    controls = request.form.items(multi=True)
    try:
      data = form.validate(controls)
    except ValidationFailure, e:
      return render_template('form.html', form=form, data=data)
    save_form({'metadata': metadata, 'form': data}, filename)
  return render_template('form.html', form=form, data=data)

if __name__ == '__main__':
  import sys

  if len(sys.argv) == 2 and sys.argv[1] == 'cherry':
    from cherrypy import wsgiserver
    d = wsgiserver.WSGIPathInfoDispatcher({'/': app})
    server = wsgiserver.CherryPyWSGIServer(('127.0.0.1', 5000), d)
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()
  else:
    app.run() # werkzeug