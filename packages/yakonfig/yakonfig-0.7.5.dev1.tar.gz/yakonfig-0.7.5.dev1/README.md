yakonfig
========

yet another config management library, or a yak on a fig

Yakonfig parses a YAML configuration file at application startup, and makes parts of that configuration available to modules within the application.  It is intended for multi-module applications where each module needs a separate configuration.  The Yakonfig library merges application-provided default configuration, a user-provided configuration file, and command-line options to produce a unified global configuration.

yakonfig API
------------

Applications using Yakonfig generally create an ``argparse.ArgumentParser`` object and call ``yakonfig.parse_args()``, giving it a list of configurable modules or other items.  A typical application setup looks like:

```python
	import argparse
	import dblogger
	import kvlayer
	import yakonfig

	def main():
	  parser = argparse.ArgumentParser()
	  yakonfig.parse_args(parser, [yakonfig, dblogger, kvlayer])
	  ...

	if __name__ == '__main__':
	  main()
```

The application will include ``--help``, ``--config FILE``, and ``--dump-config MODE`` flags by default; modules can provide additional command-line arguments.

The module list passed to ``parse_args()`` is a list of objects that look similar to ``yakonfig.Configurable`` objects.  They can be actual objects, typically factories, or they can be classes or even Python modules that happen to include the same names.  A top-level Python module might look like:

```python
	import a_package.submodule

	#: Name of this module in the config file
	config_name = 'a_package'
	#: Inner blocks within this configuration
	sub_modules = [a_package.submodule]
	#: Default configuration
	default_config = {'random_number': 17}
```

The objects contained in the ``sub_modules`` list have the same format.  Running ``./my_program.py --dump-config=default`` would print out a YAML file:

```yaml
	a_package:
	  random_number: 17
	  submodule: ...
```

A typical pattern is to create a factory object that has many configurable objects within it, such as stages in a data-processing pipeline.  The ``yakonfig.factory.AutoFactory`` class supports this pattern.  Objects built by the factory do not declare any of the configuration metadata; instead, Yakonfig determines the configuration name and default configuration by inspecting the object's constructor, or the function's argument list.  The factory class itself needs to include the standard configuration metadata.

```python
	class a_stage(object):
	  def __init__(self, random_number=17):
	    self.random_number = random_number
	  def __call__(self):
	    print self.random_number

	class StageFactory(yakonfig.factory.AutoFactory):
	  config_name='stage_factory'
	  auto_config=[a_stage]
	  def __call__(self):
	    stage = self.create(a_stage)
	    stage()
```

The corresponding default YAML configuration:

```yaml
	stage_factory:
	  a_stage:
	    random_number: 17
```

See [tests](src/tests/yakonfig/test_yakonfig.py) for further illustrations.
