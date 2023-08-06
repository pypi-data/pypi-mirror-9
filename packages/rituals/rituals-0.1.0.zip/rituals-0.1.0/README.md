# rituals

Common tasks for [Invoke](http://www.pyinvoke.org/) that are needed again and again.

![GINOSAJI](https://raw.githubusercontent.com/jhermann/rituals/master/static/img/symbol-200.png) … and again and again.

![GPL v2 licensed](http://img.shields.io/badge/license-GPL_v2-red.svg)
[![Travis CI](https://api.travis-ci.org/jhermann/rituals.svg)](https://travis-ci.org/jhermann/rituals)


## Common Tasks

The following describes the common task implementations that the ``invoke_tasks`` module contains.
See the next section on how to integrate them into your `tasks.py`.

* ``help`` –    Default task, when invoked with no task names.
* ``clean`` –   Perform house-cleaning.
* ``build`` –   Build the project.
* ``dist`` –    Distribute the project.
* ``test`` –    Perform standard unittests.
* ``check`` –   Perform source code checks.

Use ``inv -h ‹task›`` as usual to get details on the options of these tasks.
Look at the [invoke_tasks](https://github.com/jhermann/rituals/blob/master/src/rituals/invoke_tasks.py) source
if you want to know what these tasks do exactly.


## Usage

### Add common tasks to your project's `task.py`

Add `rituals` to your `dev-requirements.txt` or a similar file,
or add it to `setup_requires` in your `setup.py`.
Then at the start of your `tasks.py`, use the following statement to define _all_ tasks that are considered standard:

```py
from rituals.invoke_tasks import *
```

Of course, you can also do more selective imports, or remove specific tasks from the standard set via `del`.

| :warning: | For now, these tasks expect an importable `setup.py` that defines a `project` dict with the setup parameters, see [javaprops](https://github.com/Feed-The-Web/javaprops) and [py-generic-project](https://github.com/Springerle/py-generic-project) for examples. |
|:---:|:---:|

To refer to the current GitHub ``master`` branch, use a ``pip`` requirement like this:

```
-e git+https://github.com/jhermann/rituals.git#egg=rituals
```


### Change default project layout

By default, sources are expected in `src/‹packagename›` and tests in `src/tests`.

You can change this by calling one of the following functions, directly after the import from `rituals.invoke_tasks`.

* `config.set_maven_layout()` – Changes locations to `src/main/python/‹packagename›` and `src/test/python`.
* `config.set_flat_layout()` – Changes locations to `‹packagename›` and `tests`.


### Change default project configuration

**TODO**


## Contributing

To create a working directory for this project, call these commands:

```sh
git clone "https://github.com/jhermann/rituals.git"
cd rituals; deactivate; /usr/bin/virtualenv .venv/$(basename $PWD)
. .venv/$(basename $PWD)/bin/activate
pip install -U pip; pip install -r "dev-requirements.txt"
invoke build --docs
```

To use the source in this working directory within another project,
first activate that project's virtualenv.
Then change your current directory to _this_ project,
and either call ``pip install -e .`` or ``python setup.py develop -U``.

See [CONTRIBUTING.md](https://github.com/jhermann/rituals/blob/master/CONTRIBUTING.md) for more.


## Related Projects

* [pyinvoke/invocations](https://github.com/pyinvoke/invocations) – A collection of reusable Invoke tasks and task modules.


## Acknowledgements

* Logo elements from [clker.com Free Clipart](http://www.clker.com/).
* In case you wonder about the logo, [watch this](http://youtu.be/9VDvgL58h_Y).
