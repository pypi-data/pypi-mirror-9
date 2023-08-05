.. image:: https://travis-ci.org/aniversarioperu/salvitobot.svg?branch=master
   :target: https://travis-ci.org/aniversarioperu/salvitobot
   :alt: Latest Travis CI build status

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
        "wordpress_username": "salvitobot",
        "wordpress_password": ""
    }

`salvitobot` was written by `AniversarioPeru <aniversarioperu1@gmail.com>`_.
