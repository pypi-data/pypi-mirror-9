Clok
====

[![https://badge.fury.io/py/clok](https://badge.fury.io/py/clok.png)](https://badge.fury.io/py/clok)
[![Build Status](https://travis-ci.org/fspot/clok.svg)](https://travis-ci.org/fspot/clok)
[![Coverage Status](https://coveralls.io/repos/fspot/clok/badge.png)](https://coveralls.io/r/fspot/clok)
[![License](https://pypip.in/license/clok/badge.svg)](https://pypi.python.org/pypi/clok/)

Listen to radio and set up alarms from your computer, and control it from a web UI. Relies on `mplayer`.

![Screenshot](https://lut.im/Kq4F6vuU/as1hYLr1)

#### Features :

- list / add / remove / edit radios and alarms
- play / stop radios
- easy to install (pure python dependencies) and to use (just type `clok`)
- can be controlled via web ui or via REST API

Installation
------------

```
$ sudo apt-get install mplayer
$ pip install clok
```


Usage
-----

```
Clok

Usage:
  clok [-a ADDRESS -p PORT --database FILE --log LOG]
  clok -h | --help
  clok -v | --version

Options:
  -h --help             Show this screen.
  -v --version          Show version.
  -d --database FILE    Specify the database filename (JSON storage).
                        [default: ./db.json]
  -a --address ADDRESS  Specify on which address to listen.
                        [default: 0.0.0.0]
  -p --port PORT        Specify on which port to listen.
                        [default: 8000]
  --log LOG             Specify where to log messages, and which level to set.
                        Can be "stderr", "syslog", or a filename, followed by the level.
                        [default: stderr:INFO]
  ```
