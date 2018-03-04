# -*- coding: utf-8 -*-
from colander import MappingSchema, SchemaNode, String, Integer, Bool, Sequence, Length, Email
import colander
import deform
from chameleon.utils import Markup

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
    missing=colander.null
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
    missing=colander.null
  )

class VzdelanieTitulProfesor(MappingSchema):
  nazov_skoly = SchemaNode(String(),
    title=u'Názov vysokej školy',
    missing=''
  )
  rok = SchemaNode(Integer(),
    title=u'Rok',
    missing=colander.null,
    description=u'Uvádza sa rok, kedy vysoká škola navrhla vymenovanie za profesora'
  )

class VzdelanieDoktorVied(MappingSchema):
  nazov_skoly = SchemaNode(String(),
    title=u'Názov vysokej školy alebo inštitúcie',
    missing=''
  )
  rok = SchemaNode(Integer(),
    title=u'Rok',
    missing=colander.null
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
    title=u'Stupeň štúdia',
    description=u'Napríklad: 1., 2.'
  )
  typ_cinnosti = SchemaNode(String(),
    title=u'Typ vzdelávacej činnosti',
    description=u'Napríklad: prednášky, cvičenia, semináre'
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
    title=u'Za posledných šesť rokov (2012-2017)'
  )

class VystupBiblio(MappingSchema):
  popis = SchemaNode(String(),
    title=u'Bibliografické informácie',
    widget=deform.widget.TextAreaWidget(rows=2)
  )
  nazov_zamestnavatela = SchemaNode(String(),
    title=u'Názov zamestnávateľa',
    description=u'Uvádza sa len v prípade ak práca vznikla v pracovnom pomere mimo UK.',
    missing=colander.null
  )

class VystupProjekt(MappingSchema):
  popis = SchemaNode(String(),
    title=u'Informácie o projekte',
    widget=deform.widget.TextAreaWidget(rows=2)
  )
  nazov_zamestnavatela = SchemaNode(String(),
    title=u'Názov zamestnávateľa',
    description=u'Uvádza sa len v prípade ak projekt vznikol v pracovnom pomere mimo UK.',
    missing=colander.null
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
  nazov_zamestnavatela = SchemaNode(String(),
    title=u'Názov zamestnávateľa',
    description=u'Uvádza sa len v prípade ak výstup vznikol v pracovnom pomere mimo UK.',
    missing=colander.null
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
      title=u'Ďalšie vzdelanie'
    ),
    title=u'Ďalšie vzdelávanie'
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
    title=Markup(u'<span class="cislovanie-ak">III.2</span> Aktuálna pedagogická činnosť'),
    description=Markup(u'Uvádza sa zoznam aktuálne vyučovaných predmetov. <strong>Uvádzajú sa len predmety vyučované v rámci vysokej školy, ktorá predkladá žiadosť.</strong>')
  )
  predch_pedag_cinnost = SchemaNode(Sequence(),
    PredchadzajucaPredagogickaCinnost(
      name='predchadzajuca_pedagogicka_cinnost',
      title=u'Pedagogická činnosť'
    ),
    title=Markup(u'<span class="cislovanie-ak">III.3</span> Predchádzajúca pedagogická činnosť'),
    description=u'Uvádza sa zoznam najviac piatich vybraných, v minulosti vyučovaných predmetov. Ak bol predmet vyučovaný na inej vysokej škole, uvádza sa aj názov vysokej školy, na ktorej bol predmet vyučovaný',
    validator=Length(max=5),
    widget=deform.widget.SequenceWidget(max_len=5)
  )
  tvoriva_cinnost = SchemaNode(Sequence(),
    TvorivaCinnost(
      name='tvoriva_cinnost',
      title=u'Tvorivá činnosť'
    ),
    title=Markup(u'<span class="cislovanie-ak">III.4</span> Aktuálna tvorivá činnosť'),
    description=u'Uvádza sa zoznam aktuálnych výskumných projektov, na ktorých riešení zamestnanec participuje. Ak ide o vedúceho projektu, uvádza sa táto skutočnosť osobitne. Je možné uviesť aj výskumné projekty pre hospodársku sféru.'
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
    title=u'Počet citácií Web of Science alebo Scopus'
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
    title=Markup(u'<span class="cislovanie-ak">IV.2</span> Najvýznamnejšie publikované vedecké práce'),
    description=Markup(u'Uvádza sa najviac päť výstupov. <strong>Ak práca vznikla v pracovnom pomere mimo UK, treba uviesť zamestnávateľa</strong>.'),
    validator=Length(max=5),
    widget=deform.widget.SequenceWidget(max_len=5)
  )
  najv_prace_za_poslednych_6_rokov = SchemaNode(Sequence(),
    VystupBiblio(
      name='najv_prace_za_poslednych_6_rokov',
      title=u''
    ),
    title=Markup(u'<span class="cislovanie-ak">IV.3</span> Najvýznamnejšie publikované vedecké práce v rokoch 2012-2017'),
    description=Markup(u'Uvádza sa najviac päť výstupov. <strong>Ak práca vznikla v pracovnom pomere mimo UK, treba uviesť zamestnávateľa</strong>.'),
    validator=Length(max=5),
    widget=deform.widget.SequenceWidget(max_len=5)
  )
  najv_projekty_za_poslednych_6_rokov = SchemaNode(Sequence(),
    VystupProjekt(
      name='najv_projekty_za_poslednych_6_rokov',
      title=u''
    ),
    title=Markup(u'<span class="cislovanie-ak">IV.4</span> Účasť na riešení (vedení) najvýznamnejších vedeckých projektov v rokoch 2012-2017'),
    description=Markup(u'Uvádzajú sa len projekty v pozícií zodpovedného riešiteľa a jeho zástupcu. Uvádza sa najviac päť projektov. <strong>Ak projekt vznikol v pracovnom pomere mimo UK, treba uviesť zamestnávateľa</strong>.'),
    validator=Length(max=5),
    widget=deform.widget.SequenceWidget(max_len=5)
  )
  vystupy_s_ohlasmi = SchemaNode(Sequence(),
    VystupSOhlasmi(
      name='vystup_s_ohlasmi',
      title=u'Výstup s ohlasmi'
    ),
    title=Markup(u'<span class="cislovanie-ak">IV.5</span> Výstupy v oblasti poznania príslušného študijného odboru s najvýznamnejšími ohlasmi a prehľad ohlasov na tieto výstupy'),
    description=Markup(u'Uvádza sa najviac päť výstupov s najvýznamnejšími ohlasmi. <strong>Ak výstup vznikol v pracovnom pomere mimo UK, treba uviesť zamestnávateľa</strong>. Okrem bibliografických údajov o výstupe sa uvádzajú aj informácie o jednotlivých ohlasoch – vrátane databázy, v ktorej je ohlas evidovaný. Uvádza sa najviac desať ohlasov na jeden výstup, z ktorých najmenej jeden vznikol v predchádzajúcich šiestich rokoch (v rokoch 2012-2017).'),
    validator=Length(max=5),
    widget=deform.widget.SequenceWidget(max_len=5)
  )
  funkcie = SchemaNode(String(),
    title=Markup(u'<span class="cislovanie-ak">IV.6</span> Funkcie a členstvo vo vedeckých, odborných a profesijných spoločnostiach'),
    widget=deform.widget.TextAreaWidget(rows=10),
    missing=''
  )
  dopln_program = SchemaNode(String(),
    title=Markup(u'<span class="cislovanie-ak">V.1</span> Charakteristika aktivít súvisiacich s príslušným študijným programom'),
    widget=deform.widget.TextAreaWidget(rows=5),
    missing='',
    description=u'Uvádza sa len u garanta a spolugaranta študijného programu. Zabezpečované aktivity by mali preukázať, že garant má podstatný vplyv na uskutočňovanie študijného programu. Maximálne 3500 znakov.',
    validator=Length(max=3500)
  )
  dopln_dalsie = SchemaNode(String(),
    title=Markup(u'<span class="cislovanie-ak">V.2</span> Ďalšie aktivity'),
    widget=deform.widget.TextAreaWidget(rows=5),
    missing='',
    description=u'Ak je to podstatné, uvádzajú sa iné aktivity súvisiace s vysokoškolským vzdelávaním alebo tvorivou činnosťou. Maximálne 3500 znakov.',
    validator=Length(max=3500)
  )
  konecna_podoba = SchemaNode(Bool(),
    title=u'Formulár je v konečnej podobe a možno ho použiť v akreditačnom spise',
  )
