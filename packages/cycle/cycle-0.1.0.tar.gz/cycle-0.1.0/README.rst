=====
cycle
=====

A Python software build management tool inspired by Maven.

Quickstart
----------

After installing cycle via pip or rpm, just generate your first simple project calling::

    cycle prototype generate mynewproject [-p prototype]
    
Intro
-----

Cycle is small prototype of a build tool inspired by Apache Maven.
On the long term, it should provide some of the features Maven provides, such as

* a predefined, but flexible to customize lifecycle for projects
* a flexible integration of additional commands
* integrations to pypi, github and other remote services
* and a bunch of prototypes (maven archetypes) with good common used conventions

Why I started the project?
--------------------------

I'm a sysadmin and developers for a while working with several languages and tools.
For some languages there a powerful tools and guidelines how to develop,
for other languages a developer has to review a bunch of projects to analyze the common practices.

For almost all software projects a basic software lifecylce is identical as you can
review for yourself looking at the Maven documentation, eg.

* generate a project from a skeleton/template
* generate additional config files (special environments, test-tools config, ...)
* registering/setup remote resource (pypi, scm repo, ...)
* develop and test (best in the way of feature branches)
* write/generate documentation
* release (source, binary, distro formats)

Sometimes this seems a bit far away from `DRY <http://en.wikipedia.org/wiki/Don%27t_repeat_yourself>`_?

Why not just using Maven?

Good question! Maybe the best answer is: Maven is too powerful and a too huge step for many
developers. At least working/customizing the pom.xml files seems to be a too horrible thing
for many.

So I try to develop this small Maven inspired tool as a lightweight tools for Python and other
languages. Let's look what it becomes :-)

Contributions are welcome.

References
==========

* `Apache Maven Website <https://maven.apache.org>`_
