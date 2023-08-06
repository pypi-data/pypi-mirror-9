=====================
 slapos.recipe.build
=====================

.. contents::

Examples
--------

Recipe to build the software.

Example buildout::

  [buildout]
  parts =
    script

  [script]
  # default way with using script
  recipe = slapos.recipe.build
  url_0 = http://host/path/file.tar.gz
  md5sum = 9631070eac74f92a812d4785a84d1b4e
  script =
    import os
    os.chdir(%(work_directory)s)
    unpack(%(url_0), strip_path=True)
    execute('make')
    execute('make install DEST=%(location)s')
  slapos_promise =
    directory:bin
    dynlib:bin/file linked:libz.so.1,libc.so.6,libmagic.so.1 rpath:${zlib:location}/lib,!/lib
    directory:include
    file:include/magic.h
    directory:lib
    statlib:lib/libmagic.a
    statlib:lib/libmagic.la
    dynlib:lib/libmagic.so linked:libz.so.1,libc.so.6 rpath:${zlib:location}/lib
    dynlib:lib/libmagic.so.1 linked:libz.so.1,libc.so.6 rpath:${zlib:location}/lib
    dynlib:lib/libmagic.so.1.0.0 linked:libz.so.1,libc.so.6 rpath:${zlib:location}/lib
    directory:share
    directory:share/man
    directory:share/man/man1
    file:share/man/man1/file.1
    directory:share/man/man3
    file:share/man/man3/libmagic.3
    directory:share/man/man4
    file:share/man/man4/magic.4
    directory:share/man/man5
    directory:share/misc
    file:share/misc/magic.mgc

  [multiarchitecture]
  recipe = slapos.recipe.build
  slapos_promise =
    ...
  x86 = http://host/path/x86.zip [md5sum]
  x86-64 =  http://host/path/x64.zip [md5sum]
  script =
    if not self.options.get('url'): self.options['url'], self.options['md5sum'] = self.options[guessPlatform()].split(' ')
    extract_dir = self.extract(self.download(self.options['url'], self.options.get('md5sum')))
    workdir = guessworkdir(extract_dir)
    self.copyTree(workdir, "%(location)s")

You can remove formatting by using option “format = no” (default is “yes”)

For example::

  [escaping]
  recipe = slapos.recipe.build
  example = foobar's one
  script =
    print '%%s' %% self.options['example']
    # will print “foobar's one”

  [no-escaping]
  recipe = slapos.recipe.build
  example = foobar's one
  foo = bar
  format = no
  script =
    print '%s' % self.options['example']
    # will print “foobar's one”
    print '%(foo)s'
    # will print “%(foo)s”

Pure download
~~~~~~~~~~~~~

Note: deprecated entry-point.

::

  [buildout]
  parts =
    download

  [download]
  recipe = slapos.recipe.build:download
  url = https://some.url/file

Such profile will download https://some.url/file and put it in
buildout:parts-directory/download/download

filename parameter can be used to change destination named filename.

destination parameter allows to put explicit destination.

md5sum parameter allows pass md5sum.

mode (octal, so for rw-r--r-- use 0644) allows to set mode

Exposes target attribute which is path to downloaded file.

Notes
-----

This recipe suffers from buildout download utility issue, which will do not
try to redownload resource with wrong md5sum.

==============================
 slapos.recipe.build:gitclone
==============================

Checkout a git repository.
Supports slapos.libnetworkcache if present, and if boolean 'use-cache' option
is true.

Examples
--------

Those examples use slapos.recipe.build repository as an example.

Simple clone
~~~~~~~~~~~~

Only `repository` parameter is required. For each buildout run,
the recipe will pick up the latest commit on the remote master branch::

  >>> write(sample_buildout, 'buildout.cfg',
  ... """
  ... [buildout]
  ... parts = git-clone
  ...
  ... [git-clone]
  ... recipe = slapos.recipe.build:gitclone
  ... repository = http://git.erp5.org/repos/slapos.recipe.build.git
  ... use-cache = true
  ... """)

This will clone the git repository in `parts/git-clone` directory.
Then let's run the buildout::

  >>> print system(buildout)
  Installing git-clone.
  Cloning into '/sample-buildout/parts/git-clone'...

Let's take a look at the buildout parts directory now::

  >>> ls(sample_buildout, 'parts')
  d buildout
  d git-clone

When updating, it will do a "git fetch; git reset @{upstream}"::

  >>> print system(buildout)
  Updating git-clone.
  Fetching origin
  HEAD is now at ...

Specific branch
~~~~~~~~~~~~~~~

You can specify a specific branch using `branch` option. For each
run it will take the latest commit on this remote branch::

  >>> write(sample_buildout, 'buildout.cfg',
  ... """
  ... [buildout]
  ... parts = git-clone
  ...
  ... [git-clone]
  ... recipe = slapos.recipe.build:gitclone
  ... repository = http://git.erp5.org/repos/slapos.recipe.build.git
  ... branch = build
  ... """)

Then let's run the buildout::

  >>> print system(buildout)
  Uninstalling git-clone.
  Running uninstall recipe.
  Installing git-clone.
  Cloning into '/sample-buildout/parts/git-clone'...

Let's take a look at the buildout parts directory now::

  >>> ls(sample_buildout, 'parts')
  d buildout
  d git-clone

And let's see that current branch is "build"::

  >>> import subprocess
  >>> cd('parts', 'git-clone')
  >>> print subprocess.check_output(['git', 'branch'])
  * build

When updating, it will do a "git fetch; git reset build"::

  >>> cd(sample_buildout)
  >>> print system(buildout)
  Updating git-clone.
  Fetching origin
  HEAD is now at ...

Specific revision
~~~~~~~~~~~~~~~~~

You can specify a specific commit hash or tag using `revision` option.
This option has priority over the "branch" option::

  >>> cd(sample_buildout)
  >>> write(sample_buildout, 'buildout.cfg',
  ... """
  ... [buildout]
  ... parts = git-clone
  ...
  ... [git-clone]
  ... recipe = slapos.recipe.build:gitclone
  ... repository = http://git.erp5.org/repos/slapos.recipe.build.git
  ... revision = 2566127
  ... """)

Then let's run the buildout::

  >>> print system(buildout)
  Uninstalling git-clone.
  Running uninstall recipe.
  Installing git-clone.
  Cloning into '/sample-buildout/parts/git-clone'...

Let's take a look at the buildout parts directory now::

  >>> ls(sample_buildout, 'parts')
  d buildout
  d git-clone

And let's see that current revision is "2566127"::

  >>> import subprocess
  >>> cd(sample_buildout, 'parts', 'git-clone')
  >>> print subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'])
  2566127

When updating, it will do a "git fetch; git reset revision"::

  >>> cd(sample_buildout)
  >>> print system(buildout)
  Updating git-clone.
  Fetching origin
  HEAD is now at 2566127 ...

Empty revision/branch
~~~~~~~~~~~~~~~~~~~~~

Specifying an empty revision or an empty branch will make buildout
ignore those values as if it was not present at all (allowing to easily
extend an existing section specifying a branch)::

  >>> cd(sample_buildout)
  >>> write(sample_buildout, 'buildout.cfg',
  ... """
  ... [buildout]
  ... parts = git-clone
  ...
  ... [git-clone-with-branch]
  ... recipe = slapos.recipe.build:gitclone
  ... repository = http://git.erp5.org/repos/slapos.recipe.build.git
  ... revision = 2566127
  ...
  ... [git-clone]
  ... <= git-clone-with-branch
  ... revision =
  ... branch = master
  ... """)

  >>> print system(buildout)
  Uninstalling git-clone.
  Running uninstall recipe.
  Installing git-clone.
  Cloning into '/sample-buildout/parts/git-clone'...

  >>> cd(sample_buildout, 'parts', 'git-clone')
  >>> print system('git branch')
  * master

Revision/branch priority
~~~~~~~~~~~~~~~~~~~~~~~~

If both revision and branch parameters are set, revision parameters is used
and branch parameter is ignored::

  >>> cd(sample_buildout)
  >>> write(sample_buildout, 'buildout.cfg',
  ... """
  ... [buildout]
  ... parts = git-clone
  ...
  ... [git-clone]
  ... recipe = slapos.recipe.build:gitclone
  ... repository = http://git.erp5.org/repos/slapos.recipe.build.git
  ... branch = mybranch
  ... revision = 2566127
  ... """)

  >>> print system(buildout)
  Uninstalling git-clone.
  Running uninstall recipe.
  Installing git-clone.
  Warning: "branch" parameter with value "mybranch" is ignored. Checking out to revision 2566127...
  Cloning into '/sample-buildout/parts/git-clone'...
  HEAD is now at 2566127 ...

  >>> cd(sample_buildout, 'parts', 'git-clone')
  >>> print system('git branch')
  * master

Setup a "develop" repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you need to setup a repository that will be manually alterated over time for
development purposes, you need to make sure buildout will NOT alter it and NOT
erase your local modifications by specifying the "develop" flag::

  [buildout]
  parts = git-clone

  [git-clone]
  recipe = slapos.recipe.build:gitclone
  repository = https://example.net/example.git/
  develop = true

  >>> cd(sample_buildout)
  >>> write(sample_buildout, 'buildout.cfg',
  ... """
  ... [buildout]
  ... parts = git-clone
  ...
  ... [git-clone]
  ... recipe = slapos.recipe.build:gitclone
  ... repository = http://git.erp5.org/repos/slapos.recipe.build.git
  ... develop = true
  ... """)

  >>> print system(buildout)
  Uninstalling git-clone.
  Running uninstall recipe.
  Installing git-clone.
  Cloning into '/sample-buildout/parts/git-clone'...

Buildout will then keep local modifications, instead of resetting the
repository::

  >>> cd(sample_buildout, 'parts', 'git-clone')
  >>> print system('echo foo > setup.py')

  >>> cd(sample_buildout)
  >>> print system(buildout)
  Updating git-clone.

  >>> cd(sample_buildout, 'parts', 'git-clone')
  >>> print system('cat setup.py')
  foo

Then, when update occurs, nothing is done::

  >>> cd(sample_buildout, 'parts', 'git-clone')
  >>> print system('echo kept > local_change')

  >>> print system('git remote add broken http://git.erp5.org/repos/nowhere')
  ...

  >>> cd(sample_buildout)
  >>> print system(buildout)
  Updating git-clone.
  >>> cd(sample_buildout, 'parts', 'git-clone')
  >>> print system('cat local_change')
  kept

In case of uninstall, buildout will keep the repository directory::

  >>> cd(sample_buildout)
  >>> write(sample_buildout, 'buildout.cfg',
  ... """
  ... [buildout]
  ... parts = git-clone
  ...
  ... [git-clone]
  ... recipe = slapos.recipe.build:gitclone
  ... repository = http://git.erp5.org/repos/slapos.recipe.build.git
  ... develop = true
  ... # Triggers uninstall/install because of section signature change
  ... foo = bar
  ... """)

  >>> print system(buildout)
  Uninstalling git-clone.
  Running uninstall recipe.
  You have uncommited changes in /sample-buildout/parts/git-clone. This folder will be left as is.
  Installing git-clone.
  destination directory already exists.

Specific git binary
~~~~~~~~~~~~~~~~~~~

The default git command is `git`, if for a any reason you don't
have git in your path, you can specify git binary path with `git-command`
option.

Ignore SSL certificate
~~~~~~~~~~~~~~~~~~~~~~

By default, when remote server use SSL protocol git checks if the SSL
certificate of the remote server is valid before executing commands.
You can force git to ignore this check using `ignore-ssl-certificate`
boolean option::

  [buildout]
  parts = git-clone

  [git-clone]
  recipe = slapos.recipe.build:gitclone
  repository = https://example.net/example.git/
  ignore-ssl-certificate = true

Full example
~~~~~~~~~~~~

::

  [buildout]
  parts = git-clone

  [git-binary]
  recipe = hexagonit.recipe.cmmi
  url = http://git-core.googlecode.com/files/git-1.7.12.tar.gz

  [git-clone]
  recipe = slapos.recipe.build:gitclone
  repository = http://example.net/example.git/
  git-command = ${git-binary:location}/bin/git
  revision = 0123456789abcdef

==========================
 slapos.recipe.build:cpan
==========================

Downloads and installs perl modules using Comprehensive Perl Archive Network (cpan).

Examples
--------

Basic example
~~~~~~~~~~~~~

Here is example to install one or several modules::

  [buildout]
  parts = perl-modules

  [perl-modules]
  recipe = slapos.recipe.build:cpan
  modules =
    Class::Date
    Other::Module
  # Optional argument specifying perl buildout part, if existing.
  # If specified, recipe will use the perl installed by buildout.
  # If not specified, will take the globally available perl executable.
  perl = perl

Specific version
~~~~~~~~~~~~~~~~

Note that cpan won't allow you to specify version and will always take latest
version available. To choose a specific version, you will need to specify
the full path in cpan like in ::

  [buildout]
  parts = perl-modules

  [perl-modules]
  recipe = slapos.recipe.build:cpan
  modules =
    D/DL/DLUX/Class-Date-1.1.10.tar.gz
  perl = perl

Notes
-----

Currently, the modules will be installed in site-perl directory. Location of this
directory changes depending on the perl installation.

=========================
 slapos.recipe.build:npm
=========================

Downloads and installs node.js packages using Node Package Manager (NPM).

Examples
--------

Basic example
~~~~~~~~~~~~~

Here is example to install one or several modules::

  [buildout]
  parts = node-package

  [node-package]
  recipe = slapos.recipe.build:npm
  modules =
    colors
    express

  # Optional argument specifying perl buildout part, if existing.
  # If specified, recipe will use the perl installed by buildout.
  # If not specified, will take the globally available perl executable.
  node = node-0.6

Specific version
~~~~~~~~~~~~~~~~
::

  [buildout]
  parts = node-package

  [node-package]
  recipe = slapos.recipe.build:npm
  modules =
    express@1.0.2
  node = node-0.6
