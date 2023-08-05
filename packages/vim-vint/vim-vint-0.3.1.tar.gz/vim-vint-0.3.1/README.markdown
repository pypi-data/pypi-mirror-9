![logo](https://raw.githubusercontent.com/Kuniwak/vint/logo/logo.png)

[![Development Status](https://pypip.in/status/vim-vint/badge.svg)](https://pypi.python.org/pypi/vim-vint/)
[![Latest Version](https://pypip.in/version/vim-vint/badge.svg)](https://pypi.python.org/pypi/vim-vint/)
[![Supported Python versions](https://pypip.in/py_versions/vim-vint/badge.svg)](https://pypi.python.org/pypi/vim-vint/)
[![Supported Python implementations](https://pypip.in/implementation/vim-vint/badge.svg)](https://pypi.python.org/pypi/vim-vint/)
[![Build Status](https://travis-ci.org/Kuniwak/vint.svg?branch=master)](https://travis-ci.org/Kuniwak/vint)

Vint is a Vim script Language Lint.
The goal to reach for Vint is:

- Highly extensible lint
- Highly customizable lint
- High performance lint

**But now, Vint is under development. We hope you develop a policy to help us.**


Quick start
-----------

You can install with [pip](https://pip.pypa.io/en/latest/).

	$ pip install vim-vint

You can use Vint with [scrooloose/syntastic](https://github.com/scrooloose/syntastic) by [todesking/vint-syntastic](https://github.com/todesking/vint-syntastic).


Configure
---------

Vint will read config files on the following priority order:

- [User config](#user-config):
  - e.g. `~/.vintrc.yaml`

- [Project config](#project-config):
  - e.g. `path/to/proj/.vintrc.yaml`

- [Command line config](#command-line-config):
  - e.g. `$ vint --error`, `$ vint --max-violations 10`

- [Comment config](#comment-config) (highest priority):
  - e.g. `" vint: -ProhibitAbbreviationOption +ProhibitSetNoCompatible`


### User config

You can configure global Vint config by `~/.vintrc.yaml` as following:

```yaml
cmdargs:
  # Checking more strictly
  severity: style_problem

  # Enable coloring
  color: true

policies:
  # Disable a violation
  ProhibitSomethingEvil:
    enabled: false

  # Enable a violation
  ProhibitSomethingBad:
    enabled: true
```

You can see all policy names on [Vint linting policy summary](https://github.com/Kuniwak/vint/wiki/Vint-linting-policy-summary).


### Project config

You can configure project local Vint config by `.vintrc.yaml` as following:

```yaml
cmdargs:
  # Checking more strictly
  severity: style_problem

  # Enable coloring
  color: true

policies:
  # Disable a violation
  ProhibitSomethingEvil:
    enabled: false

  # Enable a violation
  ProhibitSomethingBad:
    enabled: true
```

You can see all policy names on [Vint linting policy summary](https://github.com/Kuniwak/vint/wiki/Vint-linting-policy-summary).


### Command line config

You can configure linting severity, max errors, ... as following:

	$ vint --color --style ~/.vimrc


### Comment config

You can enable/disable linting policies by a comment as following:

```viml
" vint: -ProhibitAbbreviationOption

let s:save_cpo = &cpo
set cpo&vim

" vint: +ProhibitAbbreviationOption

" do something...

" vint: -ProhibitAbbreviationOption

let &cpo = s:save_cpo
unlet s:save_cpo
```

This syntax is: `" vint: [+-]<PolicyName> [+-]<PolicyName> ...`.

You can see all policy names on [Vint linting policy summary](https://github.com/Kuniwak/vint/wiki/Vint-linting-policy-summary).


Code health
-----------

[![Coverage Status](https://img.shields.io/coveralls/Kuniwak/vint.svg)](https://coveralls.io/r/Kuniwak/vint)
[![Code Health](https://landscape.io/github/Kuniwak/vint/master/landscape.png)](https://landscape.io/github/Kuniwak/vint/master)
[![Dependency Status](https://gemnasium.com/Kuniwak/vint.svg)](https://gemnasium.com/Kuniwak/vint)


License
-------

[MIT](http://orgachem.mit-license.org/)


Acknowledgement
---------------

* [ynkdir/vim-vimlparser](https://github.com/ynkdir/vim-vimlparser)
* [Google Vimscript Style Guide](http://google-styleguide.googlecode.com/svn/trunk/vimscriptguide.xml?showone=Catching_Exceptions#Catching_Exceptions)
* [Anti-pattern of vimrc](http://rbtnn.hateblo.jp/entry/2014/12/28/010913)
