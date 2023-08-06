Advanced Direct Connect (ADC) bot that connects to a hub and periodically downloads the filelist of each user. When it find changes it will announce these in the hub chat. It comes with chat commands that let you force scan users and list a history of changes.

It's written in Python and based on the great Twisted network framework.


changes
-------

* 0.3.1
  * bugfix: auto-announce changes when found
  * bugfix: better format for stored changes
  * bugfix: prevent filelist mixup when scanning many users

* 0.3.0
  * after some prototypes in go and with asyncio this is the first functional version with twisted


