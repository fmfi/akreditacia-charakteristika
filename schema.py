# -*- coding: utf-8 -*-
from colander import MappingSchema, SchemaNode, String, Integer, Bool, Sequence

class Vzdelanie(MappingSchema):
  nazov_skoly = SchemaNode(String(), title=u'Názov vysokej školy alebo inštitúcie', missing='')
  rok = SchemaNode(Integer(), title=u'Rok', missing=0)
  odbor_program = SchemaNode(String(), title=u'Odbor a program', missing='')

class PedagogickaCinnost(MappingSchema):
  nazov_predmetu = SchemaNode(String(), title=u'Názov predmetu')
  stupen_studia = SchemaNode(String(), title=u'Stupeň štúdia')
  typ_cinnosti = SchemaNode(String(), title=u'Typ vzdelávacej činnosti')

class PredchadzajucaPredagogickaCinnost(PedagogickaCinnost):
  akademicky_rok = SchemaNode(String(), title=u'Akademický rok')
  skola = SchemaNode(String(), title=u'Názov vysokej školy', missing='')

class TvorivaCinnost(MappingSchema):
  nazov_projektu = SchemaNode(String(), title=u'Názov projektu')
  veduci_projektu = SchemaNode(Bool(), title=u'Vedúci projektu')

class Charakteristika(MappingSchema):
  titul_pred = SchemaNode(String(), title=u'Tituly pred menom', missing='')
  priezvisko = SchemaNode(String(), title=u'Priezvisko')
  meno = SchemaNode(String(), title=u'Meno')
  titul_za = SchemaNode(String(), title=u'Tituly za menom', missing='')
  rok_narodenia = SchemaNode(Integer(), title=u'Rok narodenia')
  pracovisko = SchemaNode(String(), title=u'Názov a adresa pracoviska')
  email = SchemaNode(String(), title=u'E-mail')
  vzd_druhy = Vzdelanie(title='Vysokoškolské vzdelanie druhého stupňa')
  vzd_treti = Vzdelanie(title='Vysokoškolské vzdelanie tretieho stupňa')
  vzd_docent = Vzdelanie(title='Titul docent')
  vzd_profesor = Vzdelanie(title='Titul profesor')
  vzd_doktor_vied = Vzdelanie(title='Doktor vied')
  vzd_dalsie = SchemaNode(Sequence(), Vzdelanie(name='dalsie_vzdelanie', title=u'Ďaľšie vzdelanie'), title=u'Ďaľšie vzdelávanie')
  veduci_bakalarske = SchemaNode(Integer(), title=u'Počet vedených bakalárskych prác')
  veduci_diplomove = SchemaNode(Integer(), title=u'Počet vedených diplomových prác')
  veduci_dizertacne = SchemaNode(Integer(), title=u'Počet vedených dizertačných prác')
  akt_pedag_cinnost = SchemaNode(Sequence(), PedagogickaCinnost(name='pedagogicka_cinnost', title=u'Pedagogická činnosť'), title=u'Aktuálna pedagogická činnosť')
  predch_pedag_cinnost = SchemaNode(Sequence(), PredchadzajucaPredagogickaCinnost(name='predchadzajuca_pedagogicka_cinnost', title=u'Pedagogická činnosť'), title=u'Predchádzajúca pedagogická činnosť')
  tvoriva_cinnost = SchemaNode(Sequence(), TvorivaCinnost(name='tvoriva_cinnost', title=u'Tvorivá činnosť'), title=u'Aktuálna tvorivá činnosť')