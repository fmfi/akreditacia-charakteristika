# Inštalácia

    sudo adduser --system --group ka
    sudo mkdir /var/www-apps/charakteristika
    sudo chown ka:ka /var/www-apps/charakteristika
    cd /var/www-apps/charakteristika
    # všimnime si bodku na konci príkazu
    sudo -u ka -H git clone https://github.com/fmfi/akreditacia-charakteristika.git .

    # Nainštalujeme systémové závislosti
    sudo apt-get install libsasl2-dev python-dev libldap2-dev libssl-dev libpq-dev python-virtualenv
    
    # Prepneme sa na používateľa ka
    sudo -u ka -H -s
    
    # Nastavíme virtual environment
    virtualenv venv
    source venv/bin/activate
    
    # Nainštalujeme python závislosti
    pip install -r requirements.txt
    
## Konfigurácia

Skopírujme `local_settings.py.example` do `local_settings.py` a upravme.

### Tajný kľúč

`self.secret` musí byť náhodný tajný reťazec, najlepšie je vygenerovať ho automaticky:

```bash
python -c 'import os; print repr(os.urandom(32))'
```

toto vypíše pythonový string literál, ktorý sa dá použiť ako tajný kľúč.

### Kam posielať e-maily s výnimkami

Chceme zmeniť nastavenie `ADMINS`, čo je pythonovské pole so zoznamom e-mailových adries kam posielať hlásenia:

```python
ADMINS = ['email@example.com']
```

Tiež môžme zmeniť nastavenie SMTP servera v časti, kde sa vyrába SMTP handler:

```python
mail_handler = SMTPHandler('smtp.example.com',
    'charakteristika@example.com',
    ADMINS, 'Charakteristika - error')
```

Argumenty SMTPHandler-a sú hostname SMTP servera, adresa odosielateľa, adresy prijímateľa,
predmet správy, prípadne nastavenia zabezpečenia komunikácie, viď [Python dokumentáciu SMTP handlera](https://docs.python.org/2/library/logging.handlers.html#smtphandler).

### Adresár kde sa ukladajú charakteristiky

Ukladajú sa sem JSON a RTF verzie charakteristík. Adresár musí byť zapisovateľný používateľom, pod ktorým beží aplikácia (v našom príklade je to `ka`).

```python
self.document_dir = '/cesta/k/adresaru'
```

### Pripojenie do databázy

`self.conn_str` je connection string do PostgreSQL databázy obsahujúcej informácie o privilégiách používateľov. Momentálne sa používa tá istá databáza ako pri infolistoch, resp. len tabuľka `ilsp_opravnenia` z nej. Viď tiež [nastavenie databázy v projekte infolist-editor](https://github.com/fmfi/infolist-editor#pr%C3%ADprava-datab%C3%A1zy).

```python
self.conn_str = 'host=localhost dbname= user= password='
```

## Nastavenie Apache2

```ApacheConf
WSGIScriptAlias /ka/charakteristika /var/www-apps/charakteristika/charakteristika.py
WSGIDaemonProcess kacharakteristika user=ka group=ka processes=2 threads=15 display-name={%GROUP} python-path=/var/www-apps/charakteristika:/var/www-apps/charakteristika/venv/lib/python2.7/site-packages home=/var/www-apps/charakteristika
<Directory /var/www-apps/charakteristika/>
	WSGIProcessGroup kacharakteristika
	WSGICallableObject app
	Order deny,allow
	Allow from all
</Directory>
<Location /ka/charakteristika/login>
	CosignAllowPublicAccess Off
	AuthType Cosign
</Location>
```