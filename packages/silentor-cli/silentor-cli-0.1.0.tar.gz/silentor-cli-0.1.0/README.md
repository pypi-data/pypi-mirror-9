silentor-cli
------------
[![PyPI version](https://badge.fury.io/py/silentor-cli.svg)](http://badge.fury.io/py/silentor-cli)

command line interface for [silentor](http://github.com/jayin/silentor)

install
-------

```shell
pip install silentor-cli
```

Usage
-----

- view the latest version of silentor
```shell
$ silentor version
```

- create a silentor application
```shell
$ silentor new {you app name}
```

- run you application
```shell
$ cd path/to/{you app name}
$ silentor server {port}
```

OK,just checkout you browser

Development
-----------

- upgrade the lasest release of silentor

automatic  
```shell
$ ./upgrade.py
```

or manually  
```shell
$ cd path/to/silentor-cli
$ git checkout -q gh-pages
$ git pull
$ git checkout {tag_name}
```

TODO
----

- [ ] auto upgrade your silentor app

License
-------

MIT