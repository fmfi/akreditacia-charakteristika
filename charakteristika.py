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
from pkg_resources import resource_string

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

def render_rtf_form(data, metadata):
  def p(s):
    if s is colander.null or s is None:
      return u''
    return soft_unicode(s)
  
  char = {}
  char['DISPLAY_NAME'] = u', '.join(p(data[x]) for x in ['priezvisko', 'meno', 'titul_pred', 'titul_za'] if x is not colander.null)
  
  for field in ['rok_narodenia', 'veduci_bakalarske', 'veduci_diplomove', 'veduci_dizertacne', 'funkcie', 'dopln_program', 'dopln_dalsie', 'pracovisko', 'email']:
    char[field.upper()] = data[field]
  
  for field in ['vzd_druhy', 'vzd_treti', 'vzd_docent', 'vzd_profesor', 'vzd_doktor_vied']:
    char['{}_SKOLA'.format(field.upper())] = data[field]['nazov_skoly']
    char['{}_ROK'.format(field.upper())] = data[field]['rok']
  for field in ['vzd_druhy', 'vzd_treti', 'vzd_doktor_vied']:
    char['{}_ODBOR'.format(field.upper())] = data[field]['odbor_program']
  
  char['VZD_DALSIE_SKOLA'] = u'\n\n'.join(p(x['nazov_skoly']) for x in data['vzd_dalsie'])
  char['VZD_DALSIE_ROK'] = u'\n\n'.join(p(x['rok']) for x in data['vzd_dalsie'])
  char['VZD_DALSIE_ODBOR'] = u'\n\n'.join(p(x['odbor_program']) for x in data['vzd_dalsie'])
  
  char['AKT_PEDAG_CINN'] = u'\n'.join(u'{}, {}, {}'.format(p(x['nazov_predmetu']), p(x['stupen_studia']), p(x['typ_cinnosti'])) for x in data['akt_pedag_cinnost'])
  char['PREDCH_PEDAG_CINN'] = u'\n'.join(u', '.join(p(x[f]) for f in ['nazov_predmetu', 'stupen_studia', 'akademicky_rok', 'typ_cinnosti', 'skola'] if x[f]) for x in data['predch_pedag_cinnost'])
  char['TVORIVA_CINN'] = u'\n'.join(p(x['nazov_projektu']) + (u' (vedúci projektu)' if x['veduci_projektu'] else u'') for x in data['tvoriva_cinnost'])
  
  for field in ['vystup_wos_scopus', 'vystup_a', 'vystup_b', 'vystup_citacie', 'vystup_projekty']:
    char['{}_CELKOVO'.format(field.upper())] = data[field]['celkovo']
    char['{}_6R'.format(field.upper())] = data[field]['za_poslednych_6_rokov']
  char['VYSTUP_PREDNASKY_CELKOVO'] = u'{}/{}'.format(p(data['vystup_prednasky_medzinarodne']['celkovo']), p(data['vystup_prednasky_narodne']['celkovo']))
  char['VYSTUP_PREDNASKY_6R'] = u'{}/{}'.format(p(data['vystup_prednasky_medzinarodne']['za_poslednych_6_rokov']), p(data['vystup_prednasky_narodne']['za_poslednych_6_rokov']))
  
  for field in ['najv_prace_celkom', 'najv_prace_za_poslednych_6_rokov', 'najv_projekty_za_poslednych_6_rokov']:
    for idx in range(5):
      dest = '{}_{}'.format(field.replace('za_poslednych_6_rokov', '6R').upper(), idx)
      if idx < len(data[field]):
        char[dest] = p(data[field][idx]['popis'])
        if data[field][idx]['nazov_zamestnavatela']:
          char[dest] += u' ({})'.format(p(data[field][idx]['nazov_zamestnavatela']))
      else:
        char[dest] = u''
  
  for idx in range(5):
    dest = 'VYSTUPY_S_OHLASMI_{}'.format(idx)
    if idx < len(data['vystupy_s_ohlasmi']):
      char[dest] = p(data['vystupy_s_ohlasmi'][idx]['popis'])
      if data['vystupy_s_ohlasmi'][idx]['nazov_zamestnavatela']:
          char[dest] += u' ({})'.format(p(data['vystupy_s_ohlasmi'][idx]['nazov_zamestnavatela']))
      char[dest] += u'\n\nOhlasy:\n{}'.format(p(data['vystupy_s_ohlasmi'][idx]['ohlas']))
    else:
      char[dest] = u''
  
  tdata = {'CHAR_{}'.format(key): value for key, value in char.iteritems()}
  rtf_template = resource_string(__name__, 'templates/form.rtf')
  return render_rtf(rtf_template, tdata)

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

def escape_rtf(val):
  if val == colander.null or val == None:
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

def render_rtf(rtf_template, substitutions):
  replacements = []
  for key, value in substitutions.iteritems():
    replacements.append((key, escape_rtf(value)))
  return multiple_replace(rtf_template, *replacements)

# http://stackoverflow.com/a/15221068
def multiple_replacer(*key_values):
    replace_dict = dict(key_values)
    replacement_function = lambda match: replace_dict[match.group(0)]
    pattern = re.compile("|".join([re.escape(k) for k, v in key_values]), re.M)
    return lambda string: pattern.sub(replacement_function, string)

def multiple_replace(string, *key_values):
    return multiple_replacer(*key_values)(string)

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