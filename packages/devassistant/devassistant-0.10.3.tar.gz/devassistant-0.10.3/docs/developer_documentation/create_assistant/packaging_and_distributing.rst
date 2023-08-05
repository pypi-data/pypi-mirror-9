.. _packaging_and_distributing:

Packaging and Distributing Your Assistant
=========================================

**Note: this functionality is under heavy development and is not fully implemented yet.**

So now you know how to :ref:`create an assistant <create_your_own_assistant>`.
But what if you want to share your assistant with others?

For that you could send them all the files from your assistant and tell them where they belong.
But that would be very unpleasant and that's why we've invented DAP.
DAP is a format of extension for DevAssistant that contains custom assistants.
It means DevAssistant Package.

A DAP is a tar.gz archive with ``.dap`` extension. The name of a DAP is always
``<package_name>-<version>.dap`` - i.e. ``foo-0.0.1.dap``.

Directory structure of a DAP
----------------------------

The directory structure of a DAP copies the structure of ``~/.devassistant`` or
``/usr/share/devassistant`` folder. The only difference is, that it can only contain assistants,
files and icons that that belongs to it's namespace.

Each DAP has an unique name (lat's say ``foo``) and it can only contain assistants ``foo`` or
``foo/*``. Therefore, the directory structure looks like this::

   foo-0.0.1/
     meta.yaml
     assistants/
       {crt,twk,prep,extra}/
         foo.yaml
         foo/
     files/
       {crt,twk,prep,extra,snippets}/
         foo/
     snippets/
       foo.yaml
       foo/
     icons/
       {crt,twk,prep,extra,snippets}/
         foo.{png,svg}
         foo/
     doc/
         foo/

Note several things:

- Each of this is optional, i.e. you don't create ``files`` or ``snippets`` folder if you provide
  no files or snippets. Only mandatory thing is ``meta.yaml`` (see below).
- Everything goes to the particular folder, just like you've learned in the chapter about
  :ref:`creating assistants <create_your_own_assistant>`. However, you can only add stuff named
  as your DAP (means either a folder or a file with a particular extension). If you have more
  levels of assistants, such as ``crt/foo/bar/spam.yaml``, you have to include top-level
  assistants (in this case both ``crt/foo.yaml`` and ``crt/foo/bar.yaml``). And you have to
  preserve the structure in other folders as well (i.e. no ``icons/crt/foo/spam.svg`` but
  ``icons/crt/foo/bar/spam.svg``).
- The top level folder is named ``<package_name>-<version>``.

.. _meta_yaml_ref:

meta.yaml explained
^^^^^^^^^^^^^^^^^^^

There is an important file called ``meta.yaml`` in every DAP. It contains mandatory information about the DAP as well as additional optional metadata. Let's see an explained example:

::

    package_name: foo # required
    version: 0.0.1 # required
    license: GPLv2 # required
    authors: [Bohuslav Kabrda <bkabrda@mailserver.com>, ...] # required
    homepage: https://github.com/bkabrda/assistant-foo # optional
    summary: Some brief one line text # required
    bugreports: <a single URL or email address> # optional
    dependencies:
      # for now, dependencies are possible, but the version specifiers are ignored
      - bar
      - eggs >= 1.0
      - spam== 0.1     # as you can see, spaces are optional
      - ook   <    2.5 # and more can be added, however, don't use tabs
    supported_platforms: [fedora, darwin] # optional
    description: |
        Some not-so-brief optional text.
        It can be split to multiple lines.
        
        BTW you can use **Markdown**.

* **package name** can contain lowercase letters (ASCII only), numbers, underscore and dash (while it can only start and end with a letter or digit), it has to be unique, several names are reserved by DevAssitant itself (e.g. python, ruby)

* **version** follows this scheme: <num>[.<num>]*[dev|a|b], where 1.0.5 < 1.1dev < 1.1a < 1.1b < 1.1

* **license** is specified via license tag used in Fedora https://fedoraproject.org/wiki/Licensing:Main?rd=Licensing#Good_Licenses

* **authors** is a list of authors with their e-mail addresses (_at_ can be used instead of @)

* **homepage** is an URL to existing webpage that describes the DAP or contains the code (such as in example), only http(s) or ftp is allowed, no IP addresses

* **summary** and **description** are self-descriptive in the given example

* **bugreports** defines where the user should report bugs, it can be either an URL (issue tracker) or an e-mail address (mailing list or personal)

* **dependencies** specifies other DAPs this one needs to run - either non-versioned or versioned, optional; note, that versions are ignored for now, they'll start working in one of the future DevAssistant releases

* **supported_platforms** optionally lists all platforms (Linux distributions etc.), that this DAP is known to work on. When missing or empty, all platforms are considered supported. You can choose from the following options: arch, centos, debian, fedora, gentoo, mageia, mandrake, mandriva, redhat, rocks, slackware, suse, turbolinux, unitedlinux, yellowdog and darwin (for Mac OS).


Assistant for creating assistants packages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

There is a DevAssistant package containing set of assistants that help you create this quite complicated directory structure and package your DAP. It's called dap and you can `get it form DAPI <https://dapi.devassistant.org/dap/dap/>`_.

.. code:: sh

  # install dap from DAPI
  $ da pkg install dap

  # observe available options
  $ da create dap --help

  # create DAP directory structure named foo with (empty) create and tweak assistants
  $ da create dap -n foo --crt --twk

  # you can also tweak your DAP directory structure a bit by adding assistants of different kind

  # observe available options
  $ da tweak dap add -h

  # add a snippet
  $ da tweak dap add --snippet

  # once ready, you can also pack you assistant
  $ da tweak dap pack

  # as well as check if DevAssistant thinks your package is sane
  $ da pkg lint foo-0.0.1.dap

Uploading your DAP to DevAssistant Package Index
------------------------------------------------

Once the package is finished (you have run all the steps from the previous
chapter - that means you have a DAP file which passes the linting without
errors), you can share your DAP on `DAPI <http://dapi.devassistant.org/>`_
(DevAssistant Package Index).

To do that, log into `DAPI <http://dapi.devassistant.org/>`_ with your Github
or Fedora account, and click `Upload a DAP
<http://dapi.devassistant.org/upload>`_ link in the top menu. There you will
find legal information about what you may (and may not) upload and an upload
field, where you select the \*.dap file on your machine. After that, just click
*Upload*, and the server will take care of the rest.

To update your package later, simply increase the version in `meta.yaml`,
re-run `da tweak dap pack` and `da pkg lint foo-0.0.2.dap`, and upload it to
DAPI just the same. The server will understand it's an update and will act
accordingly.

