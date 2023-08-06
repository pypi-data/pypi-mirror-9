.. image:: https://travis-ci.org/aniversarioperu/salvitobot.svg?branch=master
   :target: https://travis-ci.org/aniversarioperu/salvitobot
   :alt: Latest Travis CI build status

.. image:: https://readthedocs.org/projects/salvitobot/badge/?version=latest
   :target: http://salvitobot.readthedocs.org/en/latest/
   :alt: Documentation Status

.. image:: https://pypip.in/version/salvitobot/badge.svg?style=flat
   :target: https://pypi.python.org/pypi/salvitobot/
   :alt: Latest Version

.. image:: https://img.shields.io/badge/WTF-license-blue.svg?style=flat
   :target: https://github.com/aniversarioperu/salvitobot/blob/master/LICENSE
   :alt: WTF License

En construcción!
================

SalvitoBot
==========

Estamos muy lejos de estar preparados para evacuar la costa peruana en
caso de emergencia debido a tsunamis. Por eso aquí en el uterope hemos
programado un Twitter bot para que nos alerte en caso de sismos y
tsunamis.

Funcionamiento
==============

Este bot, `@SalvitoBot <https://twitter.com/salvitobot>`_, se activa
automáticamente cada 5 minutos y extrae información en *real-time* sobre
**sismos** y **tsunamis** de estas dos fuentes:

-  `Pacific Tsunami Warning Center (NOA) <http://ptwc.weather.gov/>`__
-  `USGS Earthquake Hazards Program <http://earthquake.usgs.gov/>`__

Estas dos páginas webs proveen información estructurada de tal manera
que es fácilmente procesable por software de computadora.
**@SalvitoBot** consume la información en formato GeoJSON y XML desde
esas dos fuentes. En el caso haya algún reporte de sismo o tsunami para
Chile y Perú, este bot emitirá un tuit como estos:

https://twitter.com/salvitobot/status/451570699275337728

https://twitter.com/salvitobot/status/451567670815510528

La idea es que estos tuits se emitirán tan pronto aparezcan en los
reportes emitidos por el **PTWC** de la NOA y el **USCGS**. Este bot
estará alerta y activo día y noche, de madrugada, todos los días (no
solo en horario de oficina).

Hemos configurado para que @SalvitoBot emita los tuits con *mention* a
la cuenta de `@IndeciPeru <https://twitter.com/indeciperu>`_ para que
puedan alertar al resto de tuiteros y la información se propague más
rápido.

Código fuente
=============

Este bot es **MADE IN UTERO** y además es *opensource*. Aquí encontrarás
el código fuente: https://github.com/utero/salvitobot/

@SalvitoBot ha sido sometido a varias pruebas pero la prueba de fuego de
su funcionamiento y utilidad será cuando ocurra el próximo sismo dentro
de territorio peruano o chileno.

**PS.** Desde luego que este método es muy rudimentario y sería mucho
mejor si las autoridades se ponen las pilas e instalan un servicio
parecido al que tienen en Chile. Por mientras, hacemos lo que está
dentro de nuestras posibilidades para ayudar.

Requisitos
==========

-  Python3.4

Instalación
===========

::

    pip install salvitobot


Configuración
=============
Renombrar el archivo ``config.json.bak`` a ``config.json`` y agregar constraseñas
y claves secretas:

.. code:: javascript

    {
        "twitter_key": "",
        "twitter_secret": "",
        "twitter_token": "",
        "twitter_token_secret": "",
        "wordpress_client": "https://mydomain.wordpress.com/xmlrpc.php",
        "wordpress_username": "usuario",
        "wordpress_password": "contrasena"
    }

Las información que deber ir en ``twitter_key``, ``twitter_secret``, ``twitter_token``
y ``twitter_token_secret`` se obtiene al registrar una nueva "app" en Twitter.
Para eso debes dirigirte a esta página https://apps.twitter.com/

Uso
===

Encuentra sismos recientes para Perú:

.. code:: python

    >>> import salvitobot
    >>> bot = salvitobot.Bot()
    >>> bot.get_quake(country='Peru')
    >>> bot.quake
    []

Encuentra sismos recientes para Venezuela:

.. code:: python

    >>> bot.get_quake(country='Venezuela')
    >>> bot.quake
    [{'tz': -240,
    'depth': 72.38,
    'time': 1423173055590,
    'datetime_utc': datetime.datetime(2015, 2, 5, 21, 50, 55, 589999, tzinfo=<UTC>),
    'longitude': -62.0483,
    'tuit': 'SISMO. 4.7 grados mb en 58km NNE of Gueiria, Venezuela. A horas  http://earthquake.usgs.gov/earthquakes/eventpage/usc000tmka',
    'link': 'http://earthquake.usgs.gov/earthquakes/eventpage/usc000tmka',
    'type': 'earthquake',
    'place': '58km NNE of Gueiria, Venezuela',
    'magnitude': 4.7,
    'magnitude_type': 'mb',
    'code': 'c000tmka',
    'latitude': 11.0419}]]

Averigua si este sismo es nuevo y no está en la base de datos:

.. code:: python

    >>> bot.is_new_quake()
    True

Ya que es nuevo, escribe un post y publícalo en WordPress:

.. code:: python

    >>> bot.write_stories()
    <BLANKLINE>
    Un temblor de mediana magnitud de 4.7 grados tuvo
    lugar el 05 Feb, 2015 por la tarde a 58km NNE of Gueiria, Venezuela
    según el Servicio Geológico de EE.UU.
    El temblor se produjo a las 21:50 de la tarde,
    del Tiempo universal coordinado (UTC), a una profundidad de
    72.38 kilómetros.
    <BLANKLINE>
    Según el USGS, el epicentro se ubicó a _related_place_.
    <BLANKLINE>
    En los últimos _days_ días, no se registraron temblores de magnitud 3.0 o mayores en esta
    zona.
    <BLANKLINE>
    La información proviene del USGS Earthquake Notification Service. Este post
    fue elaborado por un algoritmo escrito por el autor.
    <BLANKLINE>

Puedes postear el texto en tu blog Wordpress, envíe un tuit y por email:

.. code:: python

    >>> bot.post_to_wp()
    >>> bot.tweet()
    >>> bot.send_email_to(['myemailaccount@gmail.com'])

Lee la documentación completa aquí: http://salvitobot.readthedocs.org/en/latest/

`salvitobot` was written by `AniversarioPeru <aniversarioperu1@gmail.com>`_.
