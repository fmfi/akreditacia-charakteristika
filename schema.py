# -*- coding: utf-8 -*-
from colander import MappingSchema, SchemaNode, String, Integer, Bool, Sequence, Length, Email
import colander
import deform

def fmph_email_preparer(value):
  if value == colander.null:
    return value
  if value == '@fmph.uniba.sk':
    return colander.null
  return value

class Vzdelanie(MappingSchema):
  nazov_skoly = SchemaNode(String(),
    title=u'Názov vysokej školy alebo inštitúcie',
    missing=''
  )
  rok = SchemaNode(Integer(),
    title=u'Rok',
    missing=0
  )
  odbor_program = SchemaNode(String(),
    title=u'Odbor a program',
    missing='',
    description=u'Ak bolo vzdelanie získané v zahraničí, uvádza sa originálny názov študijného odboru a v zátvorke jeho preklad do štátneho jazyka.'
  )

class VzdelanieTitulDocent(MappingSchema):
  nazov_skoly = SchemaNode(String(),
    title=u'Názov vysokej školy',
    missing=''
  )
  rok = SchemaNode(Integer(),
    title=u'Rok udelenia titulu',
    missing=0
  )

class VzdelanieTitulProfesor(MappingSchema):
  nazov_skoly = SchemaNode(String(),
    title=u'Názov vysokej školy',
    missing=''
  )
  rok = SchemaNode(Integer(),
    title=u'Rok',
    missing=0,
    description=u'Uvádza sa rok, kedy vysoká škola navrhla vymenovanie za profesora'
  )

class VzdelanieDoktorVied(MappingSchema):
  nazov_skoly = SchemaNode(String(),
    title=u'Názov vysokej školy alebo inštitúcie',
    missing=''
  )
  rok = SchemaNode(Integer(),
    title=u'Rok',
    missing=0
  )
  odbor_program = SchemaNode(String(),
    title=u'Vedný odbor',
    missing=''
  )

class PedagogickaCinnost(MappingSchema):
  nazov_predmetu = SchemaNode(String(),
    title=u'Názov predmetu'
  )
  stupen_studia = SchemaNode(String(),
    title=u'Stupeň štúdia'
  )
  typ_cinnosti = SchemaNode(String(),
    title=u'Typ vzdelávacej činnosti'
  )

class PredchadzajucaPredagogickaCinnost(PedagogickaCinnost):
  akademicky_rok = SchemaNode(String(),
    title=u'Akademický rok'
  )
  skola = SchemaNode(String(),
    title=u'Názov vysokej školy',
    missing=''
  )

class TvorivaCinnost(MappingSchema):
  nazov_projektu = SchemaNode(String(),
    title=u'Názov projektu'
  )
  veduci_projektu = SchemaNode(Bool(),
    title=u'Vedúci projektu'
  )

class Vystup(MappingSchema):
  celkovo = SchemaNode(Integer(),
    title=u'Celkovo'
  )
  za_poslednych_6_rokov = SchemaNode(Integer(),
    title=u'Za posledných šesť rokov (2008-2013)'
  )

class VystupBiblio(MappingSchema):
  popis = SchemaNode(String(),
    title=u'Bibliografické informácie',
    widget=deform.widget.TextAreaWidget(rows=2)
  )

class VystupProjekt(MappingSchema):
  popis = SchemaNode(String(),
    title=u'Informácie o projekte',
    widget=deform.widget.TextAreaWidget(rows=2)
  )

class VystupSOhlasmi(MappingSchema):
  popis = SchemaNode(String(),
    title=u'Bibliografické informácie',
    widget=deform.widget.TextAreaWidget(rows=2)
  )
  ohlasy = SchemaNode(String(),
    title=u'Ohlasy',
    name='ohlas',
    widget=deform.widget.TextAreaWidget(rows=10)
  )

class Charakteristika(MappingSchema):
  titul_pred = SchemaNode(String(),
    title=u'Tituly pred menom',
    missing=''
  )
  priezvisko = SchemaNode(String(),
    title=u'Priezvisko'
  )
  meno = SchemaNode(String(),
    title=u'Meno'
  )
  titul_za = SchemaNode(String(),
    title=u'Tituly za menom',
    missing=''
  )
  rok_narodenia = SchemaNode(Integer(),
    title=u'Rok narodenia'
  )
  pracovisko = SchemaNode(String(),
    title=u'Názov a adresa pracoviska',
    default=u'Univerzita Komenského v Bratislave\nFakulta matematiky, fyziky a informatiky\nMlynská dolina\n842 48 Bratislava',
    widget=deform.widget.TextAreaWidget(rows=5),
    description=u'Uvádza sa konkrétna adresa pracoviska, v ktorom je vykonávaná práca pre vysokú školu, obvykle ide o adresu, na ktorej sa nachádza kancelária zamestnanca. Ak je výkon práce  na viacerých miestach ako napríklad sídlo vysokej školy a detašované pracoviská, uvádzajú sa všetky miesta. Viac lokalít sa neuvádza, ak má zamestnanec kanceláriu na jednej adrese, ale v rámci vysokej školy alebo fakulty zabezpečuje predmety v budovách vysokej školy na inej adrese v rámci tej istej obce.'
  )
  email = SchemaNode(String(),
    title=u'E-mail',
    default='@fmph.uniba.sk',
    preparer=fmph_email_preparer,
    validator=Email()
  )
  vzd_druhy = Vzdelanie(
    title=u'Vysokoškolské vzdelanie druhého stupňa'
  )
  vzd_treti = Vzdelanie(
    title=u'Vysokoškolské vzdelanie tretieho stupňa'
  )
  vzd_docent = VzdelanieTitulDocent(
    title=u'Titul docent'
  )
  vzd_profesor = VzdelanieTitulProfesor(
    title=u'Titul profesor'
  )
  vzd_doktor_vied = VzdelanieDoktorVied(
    title=u'Doktor vied'
  )
  vzd_dalsie = SchemaNode(Sequence(),
    Vzdelanie(
      name='dalsie_vzdelanie',
      title=u'Ďaľšie vzdelanie'
    ),
    title=u'Ďaľšie vzdelávanie'
  )
  veduci_bakalarske = SchemaNode(Integer(),
    title=u'Počet vedených bakalárskych prác'
  )
  veduci_diplomove = SchemaNode(Integer(),
    title=u'Počet vedených diplomových prác'
  )
  veduci_dizertacne = SchemaNode(Integer(),
    title=u'Počet vedených dizertačných prác'
  )
  akt_pedag_cinnost = SchemaNode(Sequence(),
    PedagogickaCinnost(
      name='pedagogicka_cinnost',
      title=u'Pedagogická činnosť'
    ),
    title=u'Aktuálna pedagogická činnosť',
    description=u'Uvádza sa zoznam aktuálne vyučovaných predmetov. Uvádzajú sa len predmety vyučované v rámci vysokej školy, ktorá predkladá žiadosť.'
  )
  predch_pedag_cinnost = SchemaNode(Sequence(),
    PredchadzajucaPredagogickaCinnost(
      name='predchadzajuca_pedagogicka_cinnost',
      title=u'Pedagogická činnosť'
    ),
    title=u'Predchádzajúca pedagogická činnosť',
    description=u'Uvádza sa zoznam najviac piatich vybraných, v minulosti vyučovaných predmetov. Ak bol predmet vyučovaný na inej vysokej škole, uvádza sa aj názov vysokej školy, na ktorej bol predmet vyučovaný',
    validator=Length(max=5),
    widget=deform.widget.SequenceWidget(max_len=5)
  )
  tvoriva_cinnost = SchemaNode(Sequence(),
    TvorivaCinnost(
      name='tvoriva_cinnost',
      title=u'Tvorivá činnosť'
    ),
    title=u'Aktuálna tvorivá činnosť',
    description=u'Uvádza sa zoznam aktuálnych výskumných projektov alebo umeleckých projektov, na ktorých riešení zamestnanec participuje. Ak ide o vedúceho projektu, uvádza sa táto skutočnosť osobitne. Je možné uviesť aj výskumné projekty pre hospodársku sféru.'
  )
  vystup_wos_scopus = Vystup(
    title=u'Počet výstupov evidovaných vo Web of Science alebo Scopus'
  )
  vystup_a = Vystup(
    title=u'Počet výstupov kategórie A'
  )
  vystup_b = Vystup(
    title=u'Počet výstupov kategórie B'
  )
  vystup_citacie = Vystup(
    title=u'Počet citácií Web of Science alebo Scopus, v umeleckých študijných odboroch počet ohlasov v kategórii A'
  )
  vystup_projekty = Vystup(
    title=u'Počet projektov získaných na financovanie výskumu, tvorby',
    description=u'Uvádzajú sa len projekty, o ktorých financovaní rozhodla externá agentúra alebo inštitúcia, teda nebol financovaný v rámci grantovej schémy financovanej zo zdrojov vysokej školy. Výzva, v rámci ktorej bol projekt podporený musela byť otvorená, to je každý kto splnil zverejnené všeobecné kritériá musel mať možnosť požiadať o grant. Uvádzajú sa len projekty, kde bola osoba, o ktorej je charakteristika, zodpovedným riešiteľom alebo jeho zástupcom.'
  )
  vystup_prednasky_medzinarodne = Vystup(
    title=u'Počet pozvaných prednášok na medzinárodnej úrovni'
  )
  vystup_prednasky_narodne = Vystup(
    title=u'Počet pozvaných prednášok na národnej úrovni'
  )
  najv_prace_celkom = SchemaNode(Sequence(),
    VystupBiblio(
      name='najv_prace_celkom',
      title=u''
    ),
    title=u'Najvýznamnejšie publikované vedecké práce, verejne realizované alebo prezentované umelecké diela a výkony.',
    description=u'Uvádza sa najviac päť výstupov.',
    validator=Length(max=5),
    widget=deform.widget.SequenceWidget(max_len=5)
  )
  najv_prace_za_poslednych_6_rokov = SchemaNode(Sequence(),
    VystupBiblio(
      name='najv_prace_za_poslednych_6_rokov',
      title=u''
    ),
    title=u'Najvýznamnejšie publikované vedecké práce verejne realizované alebo prezentované umelecké diela alebo výkony v rokoch 2008-2013.',
    description=u'Uvádza sa najviac päť výstupov.',
    validator=Length(max=5),
    widget=deform.widget.SequenceWidget(max_len=5)
  )
  najv_projekty_za_poslednych_6_rokov = SchemaNode(Sequence(),
    VystupProjekt(
      name='najv_projekty_za_poslednych_6_rokov',
      title=u''
    ),
    title=u'Účasť na riešení (vedení) najvýznamnejších vedeckých projektov alebo umeleckých projektov v rokoch 2008-2013.',
    description=u'Uvádzajú sa len projekty v pozícií zodpovedného riešiteľa a jeho zástupcu. Uvádza sa najviac päť projektov.',
    validator=Length(max=5),
    widget=deform.widget.SequenceWidget(max_len=5)
  )
  vystupy_s_ohlasmi = SchemaNode(Sequence(),
    VystupSOhlasmi(
      name='vystup_s_ohlasmi',
      title=u'Výstup s ohlasmi'
    ),
    title=u'Výstupy v oblasti poznania príslušného študijného odboru s najvýznamnejšími ohlasmi a prehľad ohlasov na tieto výstupy.',
    description=u'Uvádza sa najviac päť výstupov s najvýznamnejšími ohlasmi. Okrem bibliografických údajov o výstupe sa uvádzajú aj informácie o jednotlivých ohlasoch – vrátane databázy, v ktorej je ohlas evidovaný. Uvádza sa najviac desať ohlasov na jeden výstup, z ktorých najmenej jeden vznikol v predchádzajúcich šiestich rokoch (v rokoch 2008-2013).',
    validator=Length(max=5),
    widget=deform.widget.SequenceWidget(max_len=5)
  )
  funkcie = SchemaNode(String(),
    title=u'Funkcie a členstvo vo vedeckých, odborných a profesijných spoločnostiach',
    widget=deform.widget.TextAreaWidget(rows=10),
    missing=''
  )
  dopln_program = SchemaNode(String(),
    title=u'Charakteristika aktivít súvisiacich s príslušným študijným programom',
    widget=deform.widget.TextAreaWidget(rows=5),
    missing='',
    description=u'Uvádza sa len u garanta a spolugaranta študijného programu. Zabezpečované aktivity by mali preukázať, že garant má podstatný vplyv na uskutočňovanie študijného programu. Maximálne 3500 znakov.',
    validator=Length(max=3500)
  )
  dopln_dalsie = SchemaNode(String(),
    title=u'Ďalšie aktivity',
    widget=deform.widget.TextAreaWidget(rows=5),
    missing='',
    description=u'Ak je to podstatné, uvádzajú sa iné aktivity súvisiace s vysokoškolským vzdelávaním alebo tvorivou činnosťou. Maximálne 3500 znakov.',
    validator=Length(max=3500)
  )