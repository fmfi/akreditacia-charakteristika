#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, Blueprint
app = Flask(__name__)

from flask import render_template, url_for, redirect
from flask import request, Request
from flask import Response, abort
from flask import g
from werkzeug.exceptions import BadRequest, NotFound
from werkzeug.datastructures import OrderedMultiDict
from werkzeug.routing import BaseConverter
import re
import os
from deform import Form
from deform.exception import ValidationFailure
import json
import os
import os.path
import ldap
from pkg_resources import resource_filename
import colander
import time
import jinja2
from markupsafe import Markup, soft_unicode
import psycopg2
# postgres unicode
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)
from psycopg2.extras import NamedTupleCursor
from itsdangerous import URLSafeSerializer
from functools import wraps

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

form_deform_templates = resource_filename('deform', 'templates')
form_my_templates = resource_filename(__name__, 'templates')
form_template_path = (form_my_templates, form_deform_templates)
Form.set_zpt_renderer(form_template_path)

class FormTokenConverter(BaseConverter):
  def __init__(self, url_map, *items):
    super(FormTokenConverter, self).__init__(url_map)
    self.regex = r'[A-Za-z0-9]{32}'

app.url_map.converters['token'] = FormTokenConverter

class LoginConverter(BaseConverter):
  def __init__(self, url_map, *items):
    super(LoginConverter, self).__init__(url_map)
    self.regex = r'[A-Za-z0-9]+'

app.url_map.converters['login'] = LoginConverter

def restrict(api=False, roles=None):
  if roles == None:
    roles = []
  roles = set(roles)
  def decorator(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
      if not g.user:
        if api:
          abort(401)
        else:
          goto = None
          if request.method in ['HEAD', 'GET']:
            if request.url.startswith(request.url_root):
              goto = request.url[len(request.url_root):]
              serializer = URLSafeSerializer(config.secret)
              goto = serializer.dumps(goto)
          return redirect(url_for('index', next=goto))
      if roles and not roles.intersection(g.roles):
        if api:
          abort(403)
        else:
          return render_template('unauthorized.html'), 403
      return f(*args, **kwargs)
    return wrapper
  return decorator

@app.before_request
def before_request():
  g.db = psycopg2.connect(config.conn_str, cursor_factory=NamedTupleCursor)
  
  username = request.remote_user
  if app.debug and 'REMOTE_USER' in os.environ:
    username = os.environ['REMOTE_USER']
  
  g.user = username
  g.roles = set()
  if g.user:
    with g.db.cursor() as cur:
      cur.execute('SELECT op.je_admin, op.je_garant FROM osoba o, ilsp_opravnenia op WHERE o.id = op.osoba AND o.login = %s', (username,))
      row = cur.fetchone()
      if row is not None:
        if row.je_garant:
          g.roles.add('garant')
        if row.je_admin:
          g.roles.add('admin')

def login_get_next_url():
  if 'next' not in request.args:
    return None
  try:
    serializer = URLSafeSerializer(config.secret)
    goto = serializer.loads(request.args['next'])
    goto = request.url_root + goto
    return goto
  except:
    return None

@app.route('/', methods=['POST', 'GET'])
def index():
  if not g.user:
    goto = login_get_next_url()
    goto_enc = None
    if goto is not None:
      goto_enc = request.args['next']
    return render_template('login.html', next=goto_enc, next_url=goto)
  return show_form('user-{}'.format(g.user), user=g.user)

@app.route('/vsetky')
@restrict(roles=['admin', 'garant'])
def vsetky():
  documents = [x for x in os.listdir(config.document_dir) if x.endswith('.json')]
  loaded_documents = []
  for filename in documents:
    tokmatch = re.match(r'^token-(.*)\.json$', filename)
    loginmatch = re.match(r'^user-(.*)\.json$', filename)
    if not (tokmatch or loginmatch):
      continue
    doc = load_form(filename[:-5])
    doc['filename'] = filename
    doc['formatovane_meno'] = u' '.join(unicode(doc['cstruct'][x]) for x in ['titul_pred', 'meno', 'priezvisko'] if doc['cstruct'][x] is not colander.null)
    if doc['cstruct']['titul_za'] is not colander.null:
      doc['formatovane_meno'] = u', '.join([doc['formatovane_meno'], doc['cstruct']['titul_za']])
    if not doc['formatovane_meno'].strip():
      doc['formatovane_meno'] = tokmatch.group(1) if tokmatch else loginmatch.group(1)
    try:
      Charakteristika().deserialize(doc['cstruct'])
    except colander.Invalid:
      doc['valid'] = False
    else:
      doc['valid'] = True
    doc['spravne_vyplnene'] = doc['valid'] and doc.get('form', {}).get('konecna_podoba', False)
    
    if doc['valid']:
      if tokmatch:
        doc['url'] = url_for('rtf_using_token', token=tokmatch.group(1))
      elif loginmatch:
        doc['url'] = url_for('rtf_using_login', login=loginmatch.group(1))
    else:
      doc['url'] = None
    loaded_documents.append(doc)
  return render_template('vsetky.html', documents=loaded_documents)

@app.route('/rtf')
@restrict()
def rtf_index():
  if not g.user:
    return 'Authorization required', 403
  return rtf_download('user-{}'.format(g.user))

@app.route('/login')
def login():
  goto = login_get_next_url()
  if not goto:
    return redirect(url_for('index'))
  return redirect(goto)

@app.route('/logout')
def logout():
  logout_link = 'https://login.uniba.sk/logout.cgi?{}'.format(url_for('index', _external=True))
  response = app.make_response(redirect(logout_link))
  if 'COSIGN_SERVICE' in request.environ:
    response.set_cookie(request.environ['COSIGN_SERVICE'], value='',
                        expires=1, path='/', secure=True)
  return response

@app.route('/<token:token>', methods=['POST', 'GET'])
def using_token(token):
  return show_form('token-{}'.format(token), {'token':token}, token=token)

@app.route('/<token:token>.rtf')
def rtf_using_token(token):
  return rtf_download('token-{}'.format(token))

@app.route('/<login:login>.rtf')
@restrict(roles=['admin', 'garant'])
def rtf_using_login(login):
  return rtf_download('user-{}'.format(login))

class MyJsonEncoder(json.JSONEncoder):
  def default(self, obj):
    if obj == colander.null:
      return {'__colander': 'null'}
    return super(CstructJsonEncoder, self).default(obj)

def object_hook(obj):
  if '__colander' in obj and obj['__colander'] == 'null':
    return colander.null
  return obj

def save_form(data, filename):
  filepath = os.path.join(config.document_dir, '{}.json'.format(filename))
  tmpfilepath = os.path.join(config.document_dir, '{}.json.part'.format(filename))
  try:
    with open(tmpfilepath, 'w+') as f:
      json.dump(data, f, cls=MyJsonEncoder)
      f.flush()
      os.fsync(f.fileno())
    os.rename(tmpfilepath, filepath)
  except:
    try:
      os.unlink(tmpfilepath)
    except:
      pass
    raise

def load_form(filename):
  filepath = os.path.join(config.document_dir, '{}.json'.format(filename))
  try:
    with open(filepath, 'r') as f:
      return json.load(f, object_hook=object_hook)
  except IOError, e:
    if e.errno == 2: # neexistuje
      return None
    else:
      raise

def form_messages(form):
  if not form.error:
    return None
  
  def title(exc):
    if exc.positional:
      return u'{}.'.format(exc.pos + 1)
    if exc.node.title == None or exc.node.title == u'':
      return None
    return exc.node.title
  
  errors = []
  for path in form.error.paths():
    titlepath = []
    messages = []
    for exc in path:
      if exc.msg:
        messages.extend(exc.messages())
      tit = title(exc)
      if tit != None:
        titlepath.append(tit)
    errors.append((Markup(u' – ').join(titlepath), messages))
  return errors

def show_form(filename, metadata_default={}, **kwargs):
  now = time.time()
  loaded = load_form(filename)
  exists = False
  if loaded == None:
    data = {}
    metadata = {'created': now}
    metadata.update(metadata_default)
    if g.user:
      ldap_result = query_ldap(g.user)
      if ldap_result:
        data = {
          'titul_pred': ldap_result[0],
          'meno': ldap_result[1],
          'priezvisko': ldap_result[2],
          'titul_za': ldap_result[3],
        }
  else:
    data = loaded['form']
    metadata = loaded['metadata']
    exists = True
  form = Form(Charakteristika(), buttons=('submit',), appstruct=data)
  saved = False
  if request.method == 'POST':
    controls = request.form.items(multi=True)
    try:
      data = form.validate(controls)
    except ValidationFailure, e:
      pass
    metadata['updated'] = now
    save_form({'metadata': metadata, 'form': data, 'cstruct': form.cstruct}, filename)
    saved = True
  else:
    if loaded and 'cstruct' in loaded:
      form.cstruct = loaded['cstruct']
      try:
        data = form.schema.deserialize(form.cstruct)
      except colander.Invalid as e:
        form.widget.handle_error(form, e)
  return render_template('form.html', form=form, data=data, messages=form_messages(form), saved=saved, exists=exists, **kwargs)

class RTFEnvironment(jinja2.Environment):
  def __init__(self, **kwargs):
    super(RTFEnvironment, self).__init__('[[%', '%]]', '[[#', '#]]', '[[!', '!]]', **kwargs)
    def escape_rtf(val):
      if val == colander.null:
        val = u''
      val = soft_unicode(val)
      r = ''
      prevc = None
      for c in val:
        if (c == '\n' and prevc != '\r') or (c == '\r' and prevc != '\n'):
          r += '\line '
        elif (c == '\n' and prevc == '\r') or (c == '\r' and prevc == '\n'):
          pass
        elif c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ':
          r += c
        else:
          r += '\u{}?'.format(ord(c))
        prevc = c
      return r
    self.filters['rtf'] = escape_rtf

def render_rtf_form(data, metadata):
  rtf_env = RTFEnvironment(loader=jinja2.PackageLoader(__name__, 'templates'))
  template = rtf_env.get_template('form.rtf')
  display_name = u', '.join([data['priezvisko'], data['meno'], data['titul_pred'], data['titul_za']])
  return template.render(data=data, display_name=display_name)

def rtf_download(filename):
  loaded = load_form(filename)
  if loaded == None:
    raise NotFound('Form does not exist')
  metadata = loaded['metadata']
  data = loaded['form']
  form = Form(Charakteristika(), buttons=('submit',), appstruct=data)
  if 'cstruct' in loaded:
    form.cstruct = loaded['cstruct']
    try:
      data = form.schema.deserialize(form.cstruct)
    except colander.Invalid:
      return render_template('rtf-invalid.html'), 404
  response =  Response(render_rtf_form(data=data, metadata=metadata), mimetype='application/rtf')
  response.headers['Content-Disposition'] = 'attachment; filename=vpchar.rtf'
  return response

def ldap_escape(s):
  """Escape LDAP filter value
     @see http://www.ietf.org/rfc/rfc2254.txt
  """
  r = ''
  for c in s:
    if c in ('*', '(', ')', '\\', "\0"):
      r += '\\' + hex(ord(c))[2:].zfill(2)
    else:
      r += c
  return r

def query_ldap(user):
  l = ldap.initialize('ldaps://jas2.uniba.sk,ldaps://jas1.uniba.sk')
  l.protocol_version = 3
  l.simple_bind_s()
  result = l.search_s('dc=uniba,dc=sk', ldap.SCOPE_SUBTREE, filterstr='(uid={})'.format(ldap_escape(user)))
  if len(result) == 0:
    return None
  elif len(result) > 1:
    raise ValueError('Multiple results for username {}'.format(user))
  def field(name):
    return result[0][1][name][0].decode('UTF-8')
  display_name = field('displayName')
  given_name = field('givenNameU8')
  surname = field('snU8')
  tituly_pred = display_name[:display_name.index(given_name)].strip()
  tituly_za = display_name[display_name.index(surname)+len(surname):].lstrip(',').strip()
  return tituly_pred, given_name, surname, tituly_za

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
  elif len(sys.argv) == 3 and sys.argv[1] == 'ldap':
    print repr(query_ldap(sys.argv[2]))
  else:
    app.run() # werkzeug