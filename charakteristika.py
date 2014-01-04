#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, Blueprint
app = Flask(__name__)

from flask import render_template, url_for
from flask import request, Request
from flask import Response
from werkzeug.exceptions import BadRequest
from werkzeug.datastructures import OrderedMultiDict
import re
import os
from deform import Form
from deform.exception import ValidationFailure

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

#def convert_deform_resources(resources):
#  return {typ: [url_for('deform.static', filename=x.lstrip('deform:static/')) for x in resources[typ]] for typ in resources}

@app.route('/', methods=['POST', 'GET'])
def index():
  form = Form(Charakteristika(), buttons=('submit',))
  data = None
  if request.method == 'POST':
    controls = request.form.items(multi=True)
    try:
      data = form.validate(controls)
    except ValidationFailure, e:
      pass
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