# -*- coding: utf-8 -*-
from colander import MappingSchema, SchemaNode, String, Integer, Bool, Sequence
import deform

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

class Vystup(MappingSchema):
  celkovo = SchemaNode(Integer(), title=u'Celkovo')
  za_poslednych_6_rokov = SchemaNode(Integer(), title=u'Za posledných šesť rokov')

class VystupSOhlasmi(MappingSchema):
  bibliografia = SchemaNode(String(), title=u'Bibliografické informácie', widget=deform.widget.TextAreaWidget(rows=2))
  ohlasy = SchemaNode(Sequence(), SchemaNode(String(), title='', name='ohlas', widget=deform.widget.TextAreaWidget(rows=2)), title=u'Ohlasy')

class Charakteristika(MappingSchema):
  titul_pred = SchemaNode(String(), title=u'Tituly pred menom', missing='')
  priezvisko = SchemaNode(String(), title=u'Priezvisko')
  meno = SchemaNode(String(), title=u'Meno')
  titul_za = SchemaNode(String(), title=u'Tituly za menom', missing='')
  rok_narodenia = SchemaNode(Integer(), title=u'Rok narodenia')
  pracovisko = SchemaNode(String(), title=u'Názov a adresa pracoviska', widget=deform.widget.TextAreaWidget(rows=5))
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
  vystup_wos_scopus = Vystup(title='Počet výstupov evidovaných vo Web of Science alebo Scopus')
  vystup_a = Vystup(title='Počet výstupov kategórie A')
  vystup_b = Vystup(title='Počet výstupov kategórie B')
  vystup_citacie = Vystup(title='Počet citácií Web of Science alebo Scopus, v umeleckých študijných odboroch počet ohlasov v kategórii A')
  vystup_projekty = Vystup(title='Počet projektov získaných na financovanie výskumu, tvorby')
  vystup_prednasky_medzinarodne = Vystup(title='Počet pozvaných prednášok na medzinárodnej úrovni')
  vystup_prednasky_narodne = Vystup(title='Počet pozvaných prednášok na národnej úrovni')
  najv_prace_celkom = SchemaNode(Sequence(), SchemaNode(String(), name='najv_prace_celkom', title=''), title=u'Najvýznamnejšie publikované vedecké práce, verejne realizované alebo prezentované umelecké diela a výkony. Maximálne  päť.')
  najv_prace_za_poslednych_6_rokov = SchemaNode(Sequence(), SchemaNode(String(), name='najv_prace_za_poslednych_6_rokov', title=''), title=u'Najvýznamnejšie publikované vedecké práce verejne realizované alebo prezentované umelecké diela alebo výkony za posledných šesť rokov. Maximálne päť výstupov.')
  najv_projekty_za_poslednych_6_rokov = SchemaNode(Sequence(), SchemaNode(String(), name='najv_projekty_za_poslednych_6_rokov', title=''), title=u'Účasť na riešení (vedení) najvýznamnejších vedeckých projektov alebo umeleckých projektov za posledných  šesť rokov. Maximálne päť projektov.')
  vystupy_s_ohlasmi = SchemaNode(Sequence(), VystupSOhlasmi(name='vystup_s_ohlasmi', title=u'Výstup s ohlasmi'), title=u'Výstupy v oblasti poznania príslušného študijného odboru s najvýznamnejšími ohlasmi a prehľad ohlasov na tieto výstupy. Maximálne päť výstupov a desať najvýznamnejších ohlasov na jeden výstup.')
  funkcie = SchemaNode(String(), title=u'Funkcie a členstvo vo vedeckých, odborných a profesijných spoločnostiach', widget=deform.widget.TextAreaWidget(rows=10), missing='')
  dopln_program = SchemaNode(String(), title=u'Charakteristika aktivít súvisiacich s príslušným študijným programom', widget=deform.widget.TextAreaWidget(rows=5), missing='')
  dopln_dalsie = SchemaNode(String(), title=u'Ďalšie aktivity', widget=deform.widget.TextAreaWidget(rows=5), missing='')