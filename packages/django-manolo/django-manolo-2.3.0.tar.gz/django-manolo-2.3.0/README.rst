Django-manolo
=============

|Pypi index| |Build Status| |Dependencies status| |Cover alls| |Download numbers|

Manolo, buscador de lobistas
============================

Presento un buscador de personas que ingresan las oficinas de
entidades del Estado peruano.
http://manolo.rocks

Motivación
==========

Todo aquel que visita el Organismo de Contrataciones debe registrarse
dejando su **nombre, documento de identidad, motivo de visita, empleado
público que lo recibe, hora de ingreso, salida y fecha**. Toda esta
información está disponible en la Internet en esta dirección:
http://visitas.osce.gob.pe/controlVisitas/index.php?r=consultas/visitaConsulta/index

El problema es que la interfaz no es muy amigable y sólo se pueden
buscar visitantes a la institución por día. Seleccionas cualquier día
del menú y veras todos los visitantes que de esa fecha. Si quieres saber
cuántas veces ha visitado el lugar una determinada persona, debes buscar
día por día, página por página, revisar línea por línea en búsqueda de
la persona de interés.

Obviamente este tipo de búsqueda es muy tedioso, aburrido, inexacto (se
presta a errores de conteo) además que toma demasiado tiempo hacer una
simple búsqueda.

Por eso decidí construir un simple buscador de personas que visitan
dicha institución estatal. La función de este buscador simple: **Tipeas
un nombre y aparecerán en pantalla todas las veces que la persona tenga
ingresos registrados al Organismo de Contrataciones.**

A partir de Manolo versión 2.0.0, la versión online (en http://manolo.rocks)
contiene una base de datos unificada conteniendo registro de visitas de 7
entidades del Estado peruano.

Crea tu propio buscador de lobistas
===================================
Ahora "Manolo" es un plugin para Django. Puedes crear rápidamente un
buscador de lobistas para tu institución estatal favorita. Para eso
necesitas conseguir el link donde esté alojado el registro de visitas de la
institución. Se lo das a Manolo y él hará lo suyo.

Más información en un post en el blog Útero de Marita:

http://aniversarioperu.utero.pe/2014/03/08/manolo-buscador-de-lobistas/

Esta es la dirección web de **Manolo, buscador de personas**:
http://manolo.rocks

Documentación
=============

"Manolo" es un paquete o *app* para Django y puede ser agregado
fácilmente a algún proyecto de Django a manera de plugin.

La documentación completa está en este enlace:
https://django-manolo.readthedocs.org.

Fork from Gihub
==================
Aquí puedes seguir el desarrollo de Manolo
https://github.com/aniversarioperu/django-manolo


Install
=======

* python3.4

Troubleshooting
===============
If error in pickle version appears. Remove contents of whoosh index folder and
rebuild the index:

::

    python manage.py rebuild_index  --settings=manolo.settings.local

Configure
=========
Create a `config.json` file to keep private credentials to use by settings
files:

::

    {
        "SECRET_KEY": "hola",
        "DB_USER": "postgres",
        "DB_PASS": "password",
        "DB_NAME": "manolo",
        "DB_PORT": "5432",
        "DB_HOST": "localhost"
    }

.. |Pypi index| image:: https://badge.fury.io/py/django-manolo.svg
   :target: https://badge.fury.io/py/django-manolo
.. |Build Status| image:: https://travis-ci.org/aniversarioperu/django-manolo.png?branch=master
   :target: https://travis-ci.org/aniversarioperu/django-manolo
.. |Cover alls| image:: https://coveralls.io/repos/aniversarioperu/django-manolo/badge.png?branch=master
   :target: https://coveralls.io/r/aniversarioperu/django-manolo?branch=master
.. |Dependencies status| image:: https://gemnasium.com/aniversarioperu/django-manolo.svg
   :target: https://gemnasium.com/aniversarioperu/django-manolo
.. |Download numbers| image:: https://pypip.in/download/django-manolo/badge.svg
   :target: https://crate.io/packages/django-manolo
   :alt: Downloads
