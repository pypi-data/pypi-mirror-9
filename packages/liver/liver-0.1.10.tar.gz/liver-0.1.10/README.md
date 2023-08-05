liver
=====

Live scheduleR


Setup
~~~~~


Recording scripts::

  liver-do-jobs   -t 3fa16564-3850-11e4-83cd-2120fb613c75 --loglevel 10 -H 172.25.14.31 --storagebasedir=/storage/
  liver-get-mo-to-delete  -t 3fa16564-3850-11e4-83cd-2120fb613c75 --loglevel 10 -H 172.25.14.31 --storagebasedir=/storage/


Cronjobs::

  (server)
  40 3 * * * cd /opt/comoda; ./liver-delete-jobs -k 90 > /dev/null
  40 4 * * * cd /opt/comoda; ./liver-delete-recordings > /dev/null

  (agent)
  0 */6 * * *liver-mo-status -t 3fa16564-3850-11e4-83cd-2120fb613c75 --loglevel 10 -H 172.25.14.31 --storagebasedir=/storage/


Libraries
~~~~~~~~~

 * django
 * python-dateutil
 * httplib2
 * simplejson
 * slugify

