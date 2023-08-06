liver
=====

Live scheduleR


Setup
~~~~~

Settings::

  PLAYOUTSERVER = {}
  PLAYOUTSERVER["token"] = "mytoken"
  PLAYOUTSERVER["prefix"] = "http://127.0.0.1:1935/vod/_definst_/smil:storage/"
  PLAYOUTSERVER["jwplayer_key"] = "jwplayer_key"

Recording scripts::

  liver-do-jobs   -t 3fa16564-3850-11e4-83cd-2120fb613c75 --loglevel 10 -H 172.25.14.31 --storagebasedir=/storage/
  liver-get-mo-to-delete  -t 3fa16564-3850-11e4-83cd-2120fb613c75 --loglevel 10 -H 172.25.14.31 --storagebasedir=/storage/


Cronjobs::

  (server)
  40 3 * * * liver-delete-jobs -k 90 --projectpath=/opt/comoda/ > /dev/null
  40 4 * * * liver-delete-recordings --projectpath=/opt/comoda/ > /dev/null

  (agent)
  0 */6 * * *liver-mo-status -t 3fa16564-3850-11e4-83cd-2120fb613c75 --loglevel 10 -H 172.25.14.31 --storagebasedir=/storage/


Libraries
~~~~~~~~~

 * django
 * python-dateutil
 * httplib2
 * simplejson
 * slugify

