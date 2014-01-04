#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os

from flask import Flask
app = Flask(__name__)

from flask import render_template
from flask import request
from flask import Response

from werkzeug.exceptions import BadRequest

from flask_wtf import Form
from wtforms import TextField, TextAreaField, IntegerField, FormField, FieldList, RadioField

class VzdelanieForm(Form):
  nazov_skoly = TextField(u'Názov vysokej školy alebo inštitúcie')
  rok = IntegerField(u'Rok')
  odbor_program = TextField(u'Odbor a program')

class PedagogickaCinnostForm(Form):
  nazov_predmetu = TextField(u'Názov predmetu')
  stupen_studia = TextField(u'Stupeň štúdia')
  typ_cinnosti = TextField(u'Typ vzdelávacej činnosti')

class PredchadzajucaPredagogickaCinnostForm(PedagogickaCinnostForm):
  akademicky_rok = TextField(u'Akademický rok')
  skola = TextField(u'Názov vysokej školy')

class TvorivaCinnostForm(Form):
  nazov_projektu = TextField(u'Názov projektu')
  veduci_projektu = RadioField(u'Vedúci projektu', choices=(('true', u'Áno'), ('false', u'Nie')))

class CharakteristikaForm(Form):
  titul_pred = TextField(u'Tituly pred menom')
  priezvisko = TextField(u'Priezvisko')
  meno = TextField(u'Meno')
  titul_za = TextField(u'Tituly za menom')
  rok_narodenia = IntegerField(u'Rok narodenia')
  pracovisko = TextAreaField(u'Názov a adresa pracoviska')
  email = TextField(u'E-mail')
  vzd_druhy = FormField(VzdelanieForm)
  vzd_treti = FormField(VzdelanieForm)
  vzd_docent = FormField(VzdelanieForm)
  vzd_profesor = FormField(VzdelanieForm)
  vzd_doktor_vied = FormField(VzdelanieForm)
  vzd_dalsie = FormField(VzdelanieForm)
  veduci_bakalarske = IntegerField(u'Počet vedených bakalárskych prác')
  veduci_diplomove = IntegerField(u'Počet vedených diplomových prác')
  veduci_dizertacne = IntegerField(u'Počet vedených dizertačných prác')
  akt_pedag_cinnost = FieldList(FormField(PedagogickaCinnostForm))
  predch_pedag_cinnost = FieldList(FormField(PredchadzajucaPredagogickaCinnostForm))
  tvoriva_cinnost = FieldList(FormField(TvorivaCinnostForm))

if 'CHARAKTERISTIKA_DEBUG' in os.environ:
  app.debug = True

from local_settings import active_config
config = active_config(app)
app.secret_key = config.secret

@app.route('/')
def index():
  form = CharakteristikaForm()
  form.akt_pedag_cinnost.append_entry()
  form.predch_pedag_cinnost.append_entry()
  form.tvoriva_cinnost.append_entry()
  return render_template('form.html', form=form)

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