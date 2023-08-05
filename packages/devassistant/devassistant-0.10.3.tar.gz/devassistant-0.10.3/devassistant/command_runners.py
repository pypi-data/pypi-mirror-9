import copy
import getpass
import grp
import json
import logging
import os
import re
import time
import string
import subprocess
import threading
import unicodedata

import dapp
import jinja2
import six
import yaml

import devassistant

from devassistant import exceptions
from devassistant.remote_auth import GitHubAuth
from devassistant.command_helpers import ClHelper, DialogHelper
from devassistant import lang
from devassistant.logger import logger
from devassistant.package_managers import DependencyInstaller
from devassistant import settings
from devassistant import utils
from devassistant import yaml_snippet_loader

"""Mapping of prefixes to command runner lists, e.g.:

'': [CR1, CR2], # default prefix is empty
'some_prefix': [CR3]

Lists should be traversed in reversed order, so that dynamically loaded command
runners can outrun (and hence "override") the default ones.
"""
command_runners = {}


def register_command_runner(arg):
    """Decorator that registers a command runner. Accepts either:

    - CommandRunner directly or
    - String prefix to register a command runner under (returning a decorator)
    """
    if isinstance(arg, str):
        def inner(command_runner):
            command_runners.setdefault(arg, [])
            command_runners[arg].append(command_runner)
            return command_runner
        return inner
    elif issubclass(arg, CommandRunner):
        command_runners.setdefault('', [])
        command_runners[''].append(arg)
        return arg
    else:
        msg = 'register_command_runner expects str or CommandRunner as argument, got: {0}'.\
            format(arg)
        raise ValueError(msg)


class CommandRunner(object):
    @classmethod
    def matches(cls, c):
        """Returns True if this command runner can run given command,
        False otherwise.

        Args:
            c - command to check, instance of devassistant.command.Command

        Returns:
            True if this runner can run the command, False otherwise
        """
        raise NotImplementedError()

    @classmethod
    def run(cls, c):
        """Runs the given command.

        Args:
            c - command to run, instance of devassistant.command.Command

        Returns:
            Tuple (logical_result, result) of the run (e.g. (True, 'output')). Usually,
            assistant should rather return [False, 'something'] then raise exception, so that
            execution could continue.

        Raises:
            Any exception that's subclass of devassistant.exceptions.CommandException
        """
        raise NotImplementedError()


@register_command_runner
class AtExitCommandRunner(CommandRunner):
    @classmethod
    def matches(cls, c):
        return c.comm_type == 'atexit'

    @classmethod
    def run(cls, c):
        utils.atexit(lang.run_section, copy.deepcopy(c.comm), copy.deepcopy(c.kwargs),
                     copy.deepcopy(c.kwargs['__assistant__']))
        return (True, c.comm)


@register_command_runner
class AskCommandRunner(CommandRunner):
    @classmethod
    def matches(cls, c):
        return c.comm_type.startswith('ask_')

    @classmethod
    def run(cls, c):
        ui = c.kwargs['__ui__']
        if c.input_res and not isinstance(c.input_res, dict):
            raise exceptions.CommandException('{0} needs a mapping as input!'.format(c.comm_type))
        if c.comm_type == 'ask_password':
            res = DialogHelper.ask_for_password(ui, **c.input_res)
        elif c.comm_type == 'ask_confirm':
            res = DialogHelper.ask_for_confirm_with_message(ui, **c.input_res)
        elif c.comm_type == 'ask_input':
            res = DialogHelper.ask_for_input_with_prompt(ui, **c.input_res)
        else:
            raise exceptions.CommandException('Unknown command type {ct}.'.format(ct=c.comm_type))
        return (bool(res), res)


@register_command_runner
class UseCommandRunner(CommandRunner):
    @classmethod
    def matches(cls, c):
        return c.comm_type == 'use'

    @classmethod
    def is_snippet_call(cls, cmd_call):
        return not (cmd_call.startswith('self.') or cmd_call.startswith('super.'))

    @classmethod
    def check_args(cls, c):
        if isinstance(c.input_res, dict):
            # check that we have 'sect' and 'args'
            if not ('sect' in c.input_res and 'args' in c.input_res):
                msg = '"use" command expects both "sect" and "args" as arguments.'
                raise exceptions.CommandException(msg)

            # check that 'sect' and 'args' have a proper form
            msg = None
            if not isinstance(c.input_res['sect'], six.string_types):
                msg = '"sect" argument for "use" command runner must be a string.'
            elif not isinstance(c.input_res['args'], dict):
                msg = '"args" argument for "use" command runner must be a mapping.'
            if msg:
                raise exceptions.CommandException(msg)

            sect = c.input_res['sect']
        elif isinstance(c.input_res, six.string_types):
            sect = c.input_res
        else:
            msg = '"use" command runner expects string or mapping as an argument.'
            raise exceptions.CommandException(msg)

        # check that sect is a string with at least one dot
        if '.' not in sect:
            msg = '"use" command section specification must be in form "what.which_section".'
            raise exceptions.CommandException(msg)
        # else everything is fine

    @classmethod
    def _construct_ctxt(cls, inp, original_ctxt):
        """If inp is string, this just duplicates the whole context
        (e.g. "use: snippet.run_section"), else else we pass just special
        values (__*__) plus the specified values, e.g.:
        - use:
            sect: snippet.run_section
            args:
              foo: $somevar
              spam: $spamspam
        """
        if isinstance(inp, dict):
            new_ctxt = copy.deepcopy(inp['args'])
            for k, v in original_ctxt.items():
                if k.startswith('__') and k.endswith('__'):
                    new_ctxt[k] = copy.deepcopy(v)
        else:
            new_ctxt = copy.deepcopy(original_ctxt)

        return new_ctxt

    @classmethod
    def run(cls, c):
        cls.check_args(c)
        kwargs = cls._construct_ctxt(c.input_res, c.kwargs)
        sect = c.input_res if isinstance(c.input_res, six.string_types) else c.input_res['sect']
        yaml_name, section_name = sect.rsplit('.', 1)
        assistant = c.kwargs['__assistant__']

        # Modify kwargs based on command
        if cls.is_snippet_call(sect):
            snip = cls.get_snippet(yaml_name)
            section = cls.get_snippet_section(section_name, snip)

            kwargs['__files__'].append(snip.get_files_section())
            kwargs['__files_dir__'].append(snip.get_files_dir())
            kwargs['__sourcefiles__'].append(snip.path)
        else:
            assistant = cls.get_assistant(yaml_name, section_name, assistant)
            section = cls.get_assistant_section(section_name, assistant)

            kwargs['__assistant__'] = assistant

        # Get section with modified kwargs
        if section_name.startswith('dependencies'):
            result = lang.dependencies_section(section, kwargs, runner=assistant)
        else:
            result = lang.run_section(section, kwargs, runner=assistant)

        return result

    @classmethod
    def get_snippet(cls, yaml_name):
        try:
            return yaml_snippet_loader.YamlSnippetLoader.get_snippet_by_name(yaml_name)
        except exceptions.SnippetNotFoundException as e:
            raise exceptions.CommandException(e)

    @classmethod
    def get_snippet_section(cls, section_name, snip):
        if section_name.startswith('run'):
            section = snip.get_run_section(section_name) if snip else None
        else:
            section = snip.get_dependencies_section(section_name) if snip else None

        if not section:
            raise exceptions.CommandException('Couldn\'t find section "{t}" in snippet "{n}".'.
                                              format(t=section_name, n=snip.dotted_name))
        return section

    @classmethod
    def get_assistant(cls, assistant_name, section_name, origin_assistant):
        if assistant_name == 'self':
            if not hasattr(origin_assistant, '_' + section_name):
                raise exceptions.CommandException('Assistant "{a}" has no section "{s}"'.
                                                  format(a=origin_assistant.name,
                                                         s=section_name))
            return origin_assistant
        elif assistant_name == 'super':
            a = origin_assistant.superassistant
            while a:
                if hasattr(a, 'assert_fully_loaded'):
                    a.assert_fully_loaded()
                if hasattr(a, '_' + section_name):
                    return a
                a = a.superassistant
            raise exceptions.CommandException('No superassistant of {a} has section {s}'.
                                              format(a=origin_assistant.name,
                                                     s=section_name))

    @classmethod
    def get_assistant_section(cls, section_name, assistant):
        if not hasattr(assistant, '_' + section_name):
            raise exceptions.CommandException('Assistant {a} has no section {s}'.
                                              format(a=assistant.name,
                                                     s=section_name))
        return getattr(assistant, '_' + section_name)


@register_command_runner
class ClCommandRunner(CommandRunner):
    @classmethod
    def matches(cls, c):
        return c.comm_type.startswith('cl')

    @classmethod
    def run(cls, c):
        log_level = logging.DEBUG
        as_user = None
        reraise = True

        if 'i' in c.comm_type:
            log_level = logging.INFO
        if 'r' in c.comm_type:
            as_user = 'root'
        if 'p' in c.comm_type:
            # we need this option for the case we don't want to exit assistant imediatelly,
            #  but at the same time we need the command output (we could use $(command), but
            #  that doesn't allow logging output at realtime)
            reraise = False

        try:
            result = ClHelper.run_command(c.input_res, log_level, as_user=as_user,
                env=c.kwargs.get('__env__', None))
        except exceptions.ClException as e:
            if reraise:
                raise
            else:
                return (False, e.output)

        return (True, result)


@register_command_runner
class DependenciesCommandRunner(CommandRunner):
    @classmethod
    def matches(cls, c):
        return c.comm_type.startswith('dependencies')

    @classmethod
    def run(cls, c):
        if not isinstance(c.input_res, list):
            msg = 'Dependencies for installation must be list, got {v}.'.format(v=c.input_res)
            raise exceptions.CommandException(msg)

        di = DependencyInstaller()
        di.install(c.input_res, c.kwargs['__ui__'], debug=c.kwargs.get('da_debug', False))
        return (True, c.input_res)


@register_command_runner
class DotDevassistantCommandRunner(CommandRunner):
    @classmethod
    def matches(cls, c):
        return c.comm_type.startswith('dda_')

    @classmethod
    def run(cls, c):
        cls.check_args(c)
        if c.comm_type == 'dda_c':
            cls._dot_devassistant_create(c.input_res, c.kwargs)
        elif c.comm_type == 'dda_r':
            cls._dot_devassistant_read(c.input_res, c.kwargs)
        elif c.comm_type == 'dda_dependencies':
            cls._dot_devassistant_dependencies(c.input_res, c.kwargs)
        elif c.comm_type == 'dda_run':
            cls._dot_devassistant_run(c.input_res, c.kwargs)
        elif c.comm_type == 'dda_w':
            # we intentionally pass c.comm to prevent any evaluation
            cls._dot_devassistant_write(c.comm)
        else:
            raise exceptions.CommandException('Unknown command type {ct}.'.format(ct=c.comm_type))

        return (True, '')

    @classmethod
    def check_args(cls, c):
        if c.comm_type == 'dda_w':
            if not isinstance(c.input_res, list) or len(c.input_res) != 2:
                msg = 'dda_w expects Yaml list with path to .devassistant and mapping to write.'
                raise exceptions.CommandException(msg)
        else:
            if not isinstance(c.input_res, six.string_types):
                msg = '{0} expects a string as an argument.'.format(c.comm_type)
                raise exceptions.CommandException(msg)

    @classmethod
    def __dot_devassistant_write_struct(cls, directory, struct):
        """Helper for other methods that write to .devassistant file."""
        dda_path = os.path.join(os.path.abspath(os.path.expanduser(directory)), '.devassistant')
        f = open(dda_path, 'w')
        yaml.dump(struct, stream=f, default_flow_style=False)
        f.close()

    @classmethod
    def __dot_devassistant_read_exact(cls, directory):
        """Helper for other methods that read .devassistant file."""
        dda_path = os.path.join(os.path.abspath(os.path.expanduser(directory)), '.devassistant')
        try:
            with open(dda_path, 'r') as stream:
                return yaml.load(stream) or {}
        except IOError as e:
            msg = 'Couldn\'t find/open/read .devassistant file: {0}'.format(e)
            if not six.PY3:
                msg = msg.decode('utf-8')
            raise exceptions.CommandException(msg)

    @classmethod
    def _dot_devassistant_create(cls, directory, kwargs):
        # we will only write original cli/gui args, other kwargs are "private" for this run
        original_kwargs = {}
        arg_names = map(lambda arg: arg.name, kwargs['__assistant__'].args)
        for arg in arg_names:
            if arg in kwargs:  # only write those that were actually used on invocation
                original_kwargs[arg] = kwargs[arg]
        to_write = {'devassistant_version': devassistant.__version__,
                    'original_kwargs': original_kwargs,
                    'project_type': kwargs['__assistant__'].project_type,
                    'dependencies': kwargs['__assistant__'].
                    dependencies(kwargs=copy.deepcopy(original_kwargs), expand_only=True)}
        cls.__dot_devassistant_write_struct(directory, to_write)

    @classmethod
    def _dot_devassistant_read(cls, comm, kwargs):
        """Reads and stores data from .devassistant file in kwargs.
        On top of it, it adds:
        - "name" - contains the name of current directory.
        - "dda__<var>" - (yes, that is double underscore) - for each <var> that
          this project was created with.
        """
        result = cls.__dot_devassistant_read_exact(comm)

        for k, v in result.items():
            kwargs.setdefault(k, v)
        for k, v in result.get('original_kwargs', {}).items():
            kwargs.setdefault('dda__' + k, v)
        kwargs.setdefault('name', os.path.basename(os.path.abspath(os.path.expanduser(comm))))

    @classmethod
    def _dot_devassistant_dependencies(cls, comm, kwargs):
        struct = []
        dda_content = cls.__dot_devassistant_read_exact(comm)
        original_kwargs = dda_content.get('original_kwargs', {})
        mixed_kwargs = copy.deepcopy(original_kwargs)
        mixed_kwargs.update(kwargs)
        struct = lang.dependencies_section(dda_content.get('dependencies', []),
                                           mixed_kwargs,
                                           runner=kwargs.get('__assistant__'))
        lang.Command('dependencies', struct, mixed_kwargs).run()

    @classmethod
    def _dot_devassistant_run(cls, comm, kwargs):
        dda_content = cls.__dot_devassistant_read_exact(comm)
        # TODO: we should really create devassistant.util.expand_path to not use
        # abspath + expanduser everywhere all the time...
        dda_fullpath = os.path.join(os.path.abspath(os.path.expanduser(comm)), '.devassistant')
        kwargs.setdefault('__sourcefiles__', [])
        kwargs['__sourcefiles__'].append(dda_fullpath)
        lang.run_section(dda_content.get('run', []),
                         kwargs,
                         runner=kwargs.get('__assistant__'))
        kwargs['__sourcefiles__'].pop()

    @classmethod
    def _dot_devassistant_write(cls, comm):
        dda_content = cls.__dot_devassistant_read_exact(comm[0])
        dda_content.update(comm[1])
        cls.__dot_devassistant_write_struct(comm[0], dda_content)


@register_command_runner
class GitHubCommandRunner(CommandRunner):
    _user = None
    try:
        _gh_module = utils.import_module('github')
    except:
        _gh_module = None
    _required_yaml_args = {'default': ['login', 'reponame'],
                           'create_repo': ['login', 'reponame', 'private'],
                           'create_and_push': ['login', 'reponame', 'private'],
                           'create_fork': ['login', 'repo_url'],
                           'push': []}

    @classmethod
    def matches(cls, c):
        return c.comm_type == 'github'

    @classmethod
    def run(cls, c):
        """Arguments given to 'github' command may be:
        - Just a string (action), which implies that all the other arguments are deducted from
          global context and local system.
        - List containing a string (action) as a first item and rest of the args in a dict.
          (args not specified in the dict are taken from global context.

        Possible arguments:
        - login - taken from 'github' or system username - represents Github login
        - reponame - taken from 'name' (first applies os.path.basename) - repo to operate on
        """
        comm, kwargs = cls.format_args(c)
        if not cls._gh_module:
            logger.warning('PyGithub not installed, cannot execute github command.')
            return [False, '']

        # we pass arguments as kwargs, so that the auth decorator can easily query them
        # NOTE: these are not the variables from global context, but rather what
        # cls.format_args returned
        if comm == 'create_repo':
            ret = cls._github_create_repo(**kwargs)
        elif comm == 'push':
            ret = cls._github_push()
        elif comm == 'create_and_push':
            ret = cls._github_create_and_push(**kwargs)
        elif comm == 'add_remote_origin':
            ret = cls._github_add_remote_origin(**kwargs)
        elif comm == 'create_fork':
            ret = cls._github_fork(**kwargs)
        else:
            raise exceptions.CommandException('Unknown command type {ct}.'.format(ct=c.comm_type))

        return ret

    @classmethod
    def format_args(cls, c):
        args = c.input_res
        if isinstance(args, list):
            comm = args[0]
            args_rest = args[1]
        else:
            comm = args
            args_rest = {}
        # find out what arguments we will need
        kwargs = {'ui': c.kwargs['__ui__']}
        req_kwargs = cls._required_yaml_args.get(comm, cls._required_yaml_args['default'])
        for k in req_kwargs:
            kwargs[k] = getattr(cls, '_guess_' + k)(args_rest.get(k), c.kwargs)

        return comm, kwargs

    @classmethod
    def _guess_login(cls, explicit, ctxt):
        """Get github login, either from explicitly given string or 'github' global variable
        or from local username.

        Args:
            ctxt: global context

        Returns:
            guessed github login
        """
        return explicit or ctxt.get('github', None) or getpass.getuser()

    @classmethod
    def _guess_reponame(cls, explicit, ctxt):
        """Extract reponame, either from explicitly given string or from 'name' global variable,
        which is possibly a path.

        Args:
            ctxt: global context

        Returns:
            guessed reponame
        """
        name = explicit
        if not name:
            name = os.path.basename(ctxt.get('name', ''))
        if not name:
            raise exceptions.CommandException('Cannot guess Github reponame - no argument given'
                                              'and there is no "name" variable.')
        return name

    @classmethod
    def _guess_repo_url(cls, explicit, ctxt):
        """Get repo to fork in form of '<login>/<reponame>' from explicitly given string or
        global variable 'url'.

        Args:
            ctxt: global context

        Returns:
            guessed fork reponame
        """
        url = explicit or ctxt.get('url')
        if not url:
            raise exceptions.CommandException('Cannot guess name of Github repo to fork - no'
                                              'argument given and there is no "url" variable.')

        url = url[:-4] if url.endswith('.git') else url
        # if using git@github:username/reponame.git, strip the stuff before ":"
        url = url.split(':')[-1]
        return '/'.join(url.split('/')[-2:])

    @classmethod
    def _guess_private(cls, explicit, ctxt):
        return bool(explicit or ctxt.get('github_private') or False)

    @classmethod
    def _github_push(cls):
        try:
            ret = ClHelper.run_command("git push -u origin master")
            logger.info('Source code was successfully pushed.')
            return (True, ret)
        except exceptions.ClException as e:
            logger.warning('Problem pushing source code: {0}'.format(e.output))
            return (False, e.output)

    @classmethod
    @GitHubAuth.github_authenticated
    def _github_add_remote_origin(cls, **kwargs):
        """Note: the kwargs are not the global context here, but what cls.format_args returns."""
        reponame = kwargs['reponame']
        login = kwargs['login']
        # if system username != GH login, we need to use git@github.com-{login}:...
        # else just git@github.com:...
        dash_login = ''
        if getpass.getuser() != login:
            dash_login = '-' + login
        try:
            logger.info('Adding Github repo as git remote ...')
            ret = ClHelper.run_command("git remote add origin git@github.com{dl}:{l}/{r}.git".
                                       format(dl=dash_login, l=login, r=reponame))
            logger.info('Successfully added Github repo as git remote.')
            return (True, ret)
        except exceptions.ClException as e:
            logger.warning('Problem adding Github repo as git remote: {0}.'.format(e.output))
            return (False, e.output)

    @classmethod
    @GitHubAuth.github_authenticated
    def _github_create_repo(cls, **kwargs):
        """Create repo on GitHub.
        Note: the kwargs are not the global context here, but what cls.format_args returns.

        If repository already exists then CommandException will be raised.

        Raises:
            devassistant.exceptions.CommandException on error
        """
        reponame = kwargs['reponame']

        if reponame in map(lambda x: x.name, cls._user.get_repos()):
            msg = 'Failed to create Github repo: {0}/{1} alread exists.'.\
                format(cls._user.login, reponame)
            logger.warning(msg)
            return (False, msg)
        else:
            msg = ''
            success = False
            try:
                new_repo = cls._user.create_repo(reponame, private=kwargs['private'])
                msg = new_repo.clone_url
                success = True
            except cls._gh_module.GithubException as e:
                gh_errs = e.data.get('errors', [])
                gh_errs = '; '.join(map(lambda err: err.get('message', ''), gh_errs))
                msg = 'Failed to create GitHub repo. This sometime happens when you delete '
                msg += 'a repo and then you want to create the same one immediately. If that\'s '
                msg += 'the case, wait for few minutes and then try again.\n'
                msg += 'Github errors: ' + gh_errs
            except BaseException as e:
                msg = 'Failed to create Github repo: {0}'.\
                    format(getattr(e, 'message', 'Unknown error'))

            if success:
                logger.info('Your new repository: {0}'.format(new_repo.html_url))
            else:
                logger.warning(msg)

        return (success, msg)

    @classmethod
    @GitHubAuth.github_authenticated
    def _github_add_remote_and_push(cls, **kwargs):
        """Add a remote and push to GitHub. As this is not a callable subcommand of this
        command runner, it doesn't emit any informative logging messages on its own, only messages
        emitted by called methods.
        Note: the kwargs are not the global context here, but what cls.format_args returns.
        """
        ret = cls._github_add_remote_origin(**kwargs)
        if ret[0]:
            ret = cls._github_push()
        return ret

    @classmethod
    @GitHubAuth.github_authenticated
    def _github_create_and_push(cls, **kwargs):
        """Note: the kwargs are not the global context here, but what cls.format_args returns."""
        # we assume we're in the project directory
        logger.info('Registering your {priv}project on GitHub as {login}/{repo}...'.
                    format(priv='private ' if kwargs['private'] else '',
                           login=kwargs['login'],
                           repo=kwargs['reponame']))
        ret = cls._github_create_repo(**kwargs)
        if ret[0]:  # on success push the sources
            ret = cls._github_add_remote_and_push(**kwargs)
        return ret

    @classmethod
    @GitHubAuth.github_authenticated
    def _github_fork(cls, **kwargs):
        """Create a fork of repo from kwargs['fork_repo'].
        Note: the kwargs are not the global context here, but what cls.format_args returns.

        Raises:
            devassistant.exceptions.CommandException on error
        """
        timeout = 300  # 5 minutes
        fork_login, fork_reponame = kwargs['repo_url'].split('/')
        logger.info('Forking {repo} for user {login} on Github ...'.
                    format(login=kwargs['login'], repo=kwargs['repo_url']))
        success = False
        msg = ''
        try:
            repo = cls._gh_module.Github().get_user(fork_login).get_repo(fork_reponame)
            fork = cls._user.create_fork(repo)
            while timeout > 0:
                time.sleep(5)
                timeout -= 5
                try:
                    fork.get_contents('/')  # This function doesn't throw exception when clonable
                    success = True
                    break
                except cls._gh_module.GithubException as e:
                    if 'is empty' not in str(e):
                        raise e
            msg = fork.ssh_url
        except cls._gh_module.GithubException as e:
            msg = 'Failed to create Github fork with error: {err}'.format(err=e)
        except BaseException as e:
            msg = 'Exception while forking GH repo: {0}'.\
                format(getattr(e, 'message', 'Unknown error'))

        if success:
            logger.info('Fork is ready at {url}.'.format(url=fork.html_url))
        else:
            logger.warning(msg)

        return (success, msg)


@register_command_runner
class LogCommandRunner(CommandRunner):
    @classmethod
    def matches(cls, c):
        return c.comm_type.startswith('log_')

    @classmethod
    def run(cls, c):
        if c.comm_type in map(lambda x: 'log_{0}'.format(x), settings.LOG_LEVELS_MAP):
            logger.log(settings.LOG_SHORT_TO_NUM_LEVEL[c.comm_type[-1]], c.input_res)
            if c.comm_type[-1] in 'ce':
                e = exceptions.CommandException(c.input_res)
                e.already_logged = True
                raise e
        else:
            raise exceptions.CommandException('Unknown command type {ct}.'.format(ct=c.comm_type))

        return (True, c.input_res)


@register_command_runner
class SCLCommandRunner(CommandRunner):
    @classmethod
    def matches(cls, c):
        return c.comm_type.startswith('scl ')

    @classmethod
    def _get_scl_command_processor(cls, scl_call):
        def scl_command_processor(cmd_str):
            if cmd_str.startswith('cd '):
                return cmd_str
            # we can be sure that we haven't yet added precisely the same delimiter,
            #  since it would have been removed in run()
            heredoc_delimiter = 'DA_SCL_{0}_EOF'.format('_'.join(scl_call))
            cmd_str = 'scl {scls} - << {delim}\n{cmd_str}\n{delim}'.\
                format(cmd_str=cmd_str,
                       scls=' '.join(scl_call),
                       delim=heredoc_delimiter)
            return cmd_str
        return scl_command_processor

    @classmethod
    def run(cls, c):
        """SCLCommandRunner adds command processors to ClHelper in order to wrap
        commands in possibly multiple nested calls of "scl <action> <collection>".
        Note: Identical calls are ignored."""
        c.kwargs.setdefault('__assistant__', None)
        # a unique name for command processor
        comproc_name = c.comm_type
        # if such a command processor is already there, don't re-push/re-pop
        pushpop = comproc_name not in ClHelper.command_processors

        if pushpop:
            ClHelper.command_processors[comproc_name] =\
                cls._get_scl_command_processor(c.comm_type.split()[1:])

        # use "c.comm", not "c.input_res" - we need unformatted input here
        retval = lang.run_section(c.comm,
                                  c.kwargs,
                                  runner=c.kwargs['__assistant__'])

        if pushpop:
            ClHelper.command_processors.pop(comproc_name)
        return retval


@register_command_runner
class Jinja2Runner(CommandRunner):
    @classmethod
    def matches(cls, c):
        return c.comm_type in ['jinja_render', 'jinja_render_dir']

    @classmethod
    def _make_output_file_name(cls, outdir, template, output_override=None):
        """ Form an output filename by joining outdir and filename:
            - if 'output_override' is not empty string or None, just use it for filename
            - otherwise, use filename produced according to these rulse:
              - if template has '.tpl' suffix, strip it and use the stripped name
              - else just use given template name
        """

        output = ''
        if output_override:
            output = output_override
        elif template.endswith('.tpl'):
            output = template[:-len('.tpl')]
        else:
            output = template

        return os.path.join(outdir, output)

    @classmethod
    def _try_obtain_common_params(cls, comm):
        """ Retrieve parameters common for all jinja_render* actions from Command instance.
        These are mandatory:
        - 'template'    template descriptor from `files' section. it consist of
                         the only `source' key -- a name of template to use
        - 'data'        dict of parameters to use when rendering
        - 'destination' path for output files
        These are optional:
        - 'overwrite'   overwrite file(s) if it (they) exist(s)
        """
        args = comm.input_res
        ct = comm.comm_type

        wrong_tpl_msg = '{0} requires a "template" argument which must point to a file'.format(ct)
        wrong_tpl_msg += ' in "files" section. Got: {0}'.format(args.get('template', None))

        if 'template' not in args or not isinstance(args['template'], dict):
            raise exceptions.CommandException(wrong_tpl_msg)
        template = args['template']

        if 'source' not in template or not isinstance(template['source'], six.string_types):
            raise exceptions.CommandException(wrong_tpl_msg)
        template = template['source']

        if 'destination' not in args or not isinstance(args['destination'], six.string_types):
            msg = '{0} requires a string "destination" argument. Got: {1}'.\
                format(ct, args.get('destination'))
            raise exceptions.CommandException(msg)
        destination = args['destination']

        if not os.path.isdir(destination):
            msg = '{0}: Specified "destination" directory "{1}" doesn\'t exist!'.\
                format(ct, destination)
            raise exceptions.CommandException(msg)

        data = {}
        if 'data' in args and isinstance(args['data'], dict):
            data = args['data']
        logger.debug('Template context data: {0}'.format(data))

        overwrite = args.get('overwrite', False)
        overwrite = True if str(overwrite).lower() in ['true', 'yes'] else False

        return (template, destination, data, overwrite)

    @classmethod
    def run(cls, c):
        # Transform list of dicts (where keys are unique) into a single dict
        args = c.input_res
        logger.debug('Jinja2Runner args={0}'.format(repr(args)))

        # Create a jinja environment
        logger.debug('Using templates dir: {0}'.format(c.files_dir))
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(c.files_dir))
        env.trim_blocks = True
        env.lstrip_blocks = True
        template, destination, data, overwrite = cls._try_obtain_common_params(c)

        if c.comm_type == 'jinja_render':
            given_output = args.get('output', '')
            if not isinstance(given_output, six.string_types):
                raise exceptions.CommandException('Jinja2Runner: output must be string, got {0}'.
                                                  format(given_output))
            result_fn = cls._make_output_file_name(destination, template, given_output)
            cls._render_one_template(env, template, result_fn, data, overwrite)
        elif c.comm_type == 'jinja_render_dir':
            cls._render_dir(env, template, destination, data, overwrite)

        return (True, 'success')

    @classmethod
    def _render_one_template(cls, env, template, result_filename, data, overwrite):
        # Get a template instance
        tpl = None
        try:
            logger.debug('Using template file: {0}'.format(template))
            tpl = env.get_template(template)
        except jinja2.TemplateNotFound as e:
            raise exceptions.CommandException('Template {t} not found in path {p}.'.
                                              format(t=template, p=env.loader.searchpath))
        except jinja2.TemplateError as e:
            raise exceptions.CommandException('Template file failure: {0}'.format(e.message))

        # Check if destination file exists, overwrite if needed
        if os.path.exists(result_filename):
            if overwrite:
                logger.info('Overwriting the destination file {0}'.format(result_filename))
                os.remove(result_filename)
            else:
                raise exceptions.CommandException('The destination file already exists: {0}'.
                                                  format(result_filename))

        # Generate an output file finally...
        with open(result_filename, 'w') as out:
            result = tpl.render(**data)
            out.write(result)

        return (True, 'success')

    @classmethod
    def _render_dir(cls, env, template_dir, destination, data, overwrite):
        template_basedir = env.loader.searchpath[0]
        to_walk = os.path.join(template_basedir, template_dir)
        for dirpath, dirnames, filenames in os.walk(to_walk):
            for f in filenames:
                # get filename of template relative to template_dir
                tpl_name = cls._strip_dir_prefix(template_basedir, os.path.join(dirpath, f))
                dest_name = cls._make_output_file_name(
                    destination,
                    cls._strip_dir_prefix(template_dir, tpl_name))
                # if needed, create the dir that will contain the template
                dest_dir = os.path.dirname(dest_name)
                if not os.path.exists(dest_dir):
                    os.makedirs(dest_dir)

                cls._render_one_template(env, tpl_name, dest_name, data, overwrite)

    @classmethod
    def _strip_dir_prefix(cls, prefix, path):
        """Strips given prefix from given path, e.g.:
        if prefix == '/foo/bar/' and path == '/foo/bar/baz/spam', this returns 'baz/spam'
        """
        return path[len(prefix):].strip(os.path.sep)


@register_command_runner
class AsUserCommandRunner(CommandRunner):
    @classmethod
    def matches(cls, c):
        return c.comm_type.startswith('as ')

    @classmethod
    def get_user_from_comm_type(cls, comm_type):
        split_type = comm_type.split()
        if len(split_type) != 2:
            raise exceptions.CommandException('"as" expects format "as <username>".')
        user = split_type[1]
        return user

    @classmethod
    def run(cls, c):
        user = cls.get_user_from_comm_type(c.comm_type)
        to_run = utils.cl_string_for_da_eval(c.comm, c.kwargs)

        def sub_da_logger(msg):
            logger.info(msg, extra={'event_type': 'sub_da'})

        try:
            out = ClHelper.run_command(to_run, output_callback=sub_da_logger, as_user=user,
                env=c.kwargs.get('__env__', {}))
            ret = True
        except exceptions.ClException as e:
            out = e.output
            ret = False
        return (ret, out)


@register_command_runner
class DockerCommandRunner(CommandRunner):
    _has_docker_group = None
    _client = None
    try:
        _docker_module = utils.import_module('docker')
    except:
        _docker_module = None

    @classmethod
    def matches(cls, c):
        return c.comm_type.startswith('docker_')

    @classmethod
    def _docker_group_active(cls):
        if cls._has_docker_group is None:
            logger.debug('Determining if current user has active "docker" group ...')
            # we have to run cl command, too see if the user has already re-logged
            # after being added to docker group, so that he can effectively use it
            if 'docker' in ClHelper.run_command('groups').split():
                logger.debug('Current user is in "docker" group.')
                cls._has_docker_group = True
            else:
                logger.debug('Current user is not in "docker" group.')
                cls._has_docker_group = False
        return cls._has_docker_group

    @classmethod
    def _docker_group_added(cls):
        username = getpass.getuser()
        return username in grp.getgrnam('docker').gr_mem

    @classmethod
    def _docker_group_add(cls):
        username = getpass.getuser()
        try:
            logger.info('Adding {0} to group docker ...'.format(username))
            ClHelper.run_command('bash -c "usermod -a -G docker {0}"'.format(username),
                                 as_user='root')
        except exceptions.ClException as e:
            msg = 'Failed to add user to "docker" group: {0}'.format(e.output)
            raise exceptions.CommandException(msg)

    @classmethod
    def _docker_service_running(cls):
        try:
            ClHelper.run_command('systemctl status docker')
            return True
        except exceptions.ClException:
            return False

    @classmethod
    def _docker_service_enable_and_run(cls):
        # TODO: add some conditionals for various platforms
        logger.info('Enabling and running docker service ...')
        try:
            cmd_str = 'bash -c "systemctl enable docker && systemctl start docker"'
            ClHelper.run_command(cmd_str, as_user='root')
        except exceptions.ClException:
            raise exceptions.CommandException('Failed to enable and run docker service.')

        # we need to wait until /var/run/docker.sock is created
        # let's wait for 30 seconds
        logger.info('Waiting for /var/run/docker.sock to be created (max 15 seconds) ...')
        success = False
        for i in range(0, 30):
            time.sleep(i * 0.5)
            try:
                ClHelper.run_command('ls /var/run/docker.sock')
                success = True
                break
            except exceptions.ClException:
                pass

        if not success:
            logger.warning('/var/run/docker.sock doesn\'t exist, docker will likely not work!')

    @classmethod
    def run(cls, c):
        # this will raise if something is inproperly set
        cls._docker_check_setup()
        if c.comm_type == 'docker_check_setup':
            return (True, '')

        if not cls._client:
            cls._client = cls._docker_module.Client()

        if c.comm_type in ['docker_run', 'docker_attach', 'docker_find_img', 'docker_start',
            'docker_stop', 'docker_cc', 'docker_build']:
            method = getattr(cls, '_' + c.comm_type)
            ret = method(c.input_res)
        elif c.comm_type == 'docker_container_ip':
            ret = cls._docker_get_container_attr('NetworkSettings.IPAddress', c.input_res)
        elif c.comm_type == 'docker_container_name':
            ret = cls._docker_get_container_attr('Name', c.input_res)
        else:
            raise exceptions.CommandException('Unknown command type {ct}.'.format(ct=c.comm_type))

        return ret

    @classmethod
    def _docker_check_setup(cls):
        """Check that environment allows running docker:
        a) The Docker module can be imported
        b) Only users in "docker" group can use docker; there are three possible situations:
            1) user is not added to docker group => we need to add him there and then go to 2)
            2) user has been added to docker group, but would need to log out for it to
               take effect => inform and raise exception
            3) user has been added to docker group in a previous login session => all ok
        """
        if cls._docker_module is None:
            msg = 'The Docker Python module is not present. It is possible that Docker does ' +\
                  'not support your architecture yet.'
            raise exceptions.CommandException(msg)

        if not cls._docker_group_active():
            if not cls._docker_group_added():
                # situation 1
                cls._docker_group_add()
            msg = 'Your user has just been added to "docker" group. Please log out and in ' +\
                'and rerun this command.'
            raise exceptions.CommandException(msg)
        # else situation 3

        if not cls._docker_service_running():
            cls._docker_service_enable_and_run()

    @classmethod
    def _check_docker_method_args(cls, method, args, required, yaml_method):
        """Checks that items in iterable args are subset of method arguments and
        that required arguments are present in args.

        Args:
            method: instance of method of docker client
            args: iterable containing args to check
            required: iterable of required arguments
            yaml_method: name of yaml method for possible exception message

        Raises:
            exceptions.CommandException if args are not subset of method arguments
                or one or more required arguments are not present
        """
        args = set(args)
        margs = set(method.func_code.co_varnames)
        rargs = set(required)

        dif = args - margs
        if dif:
            msg = '"{ym}" does not expect "{dif}" in input mapping.'.format(
                ym=yaml_method, dif=', '.join(dif))
            raise exceptions.CommandException(msg)

        dif = rargs - args
        if dif:
            msg = '"{ym}" is missing required "{dif}" in input mapping.'.format(
                ym=yaml_method, dif=', '.join(dif))
            raise exceptions.CommandException(msg)

    @classmethod
    def _docker_build(cls, args):
        if isinstance(args, six.string_types):
            raise exceptions.CommandException('docker_build now needs a mapping to pass' +
                'to a docker-py client, please consult command reference for details.')

        cls._check_docker_method_args(cls._client.build, args.keys(), ['path'], 'docker_build')

        logger.info('Building Docker image, this may take a while ...')
        success_re = re.compile(r'Successfully built ([0-9a-f]+)')
        logres = False
        final_image = ''

        if 'rm' not in args:
            args['rm'] = True
        args['stream'] = False

        output = cls._client.build(**args)
        base_images = {}
        # docker duplicates "Download complete" messages for few reasons,
        #  we want to deduplicate them
        base_images_downloaded = []
        for chunk in output:
            # chunk is a JSON chunk, for explanation see
            #  https://github.com/docker/docker-py/issues/255#issuecomment-47600754
            logger.debug('Got message from Docker client: {0}'.format(chunk))
            parsed_json = json.loads(chunk)
            if 'status' in parsed_json and parsed_json['status'].startswith('Download'):
                i = parsed_json['id']
                # we're downloading base images
                if parsed_json['status'] == 'Downloading':
                    current = parsed_json['progressDetail']['current']
                    total = parsed_json['progressDetail']['total']
                    if i not in base_images:
                        # starting download
                        logger.info('Downloading base image {0} ...'.format(i))
                        base_images[i] = 0
                    else:
                        # download progress - print when we're in half
                        if base_images[i] < total / 2 and current > total / 2:
                            logger.info('50 % of image {0} downloaded ...'.format(i))
                        base_images[i] = current
                elif parsed_json['status'] == 'Download complete':
                    # download complete
                    if i not in base_images_downloaded:
                        logger.info('Base image {0} downloaded.'.format(i))
                        base_images_downloaded.append(i)
            elif 'stream' in parsed_json:
                # we're actually building
                l = parsed_json.get('stream', '').strip()
                logger.info(l, extra={'event_type': 'cmd_out'})
                success_found = success_re.search(l)
                if success_found:
                    logres = True
                    final_image = success_found.group(1)

        return (logres, final_image)

    @classmethod
    def _docker_run(cls, inp):
        # TODO: remove in 1.0.0
        raise exceptions.CommandException('docker_run command has been removed, see command' +
            'reference for details on replacing it.')

    @classmethod
    def _docker_cc(cls, inp):
        """Creates a docker container"""
        cls._check_docker_method_args(cls._client.create_container, inp.keys(),
            ['image'], 'docker_cc')
        res = cls._client.create_container(**inp)
        return (True, res['Id'])

    @classmethod
    def _docker_start(cls, inp):
        cls._check_docker_method_args(cls._client.start, inp.keys(),
            ['container'], 'docker_start')
        cls._client.start(**inp)
        # there is no real result here, so just return container hash again
        return (True, inp['container'])

    @classmethod
    def _docker_stop(cls, inp):
        if isinstance(inp, dict):
            cls._check_docker_method_args(cls._client.stop, inp.keys(),
                ['container'], 'docker_stop')
            if 'container' not in inp:
                msg = 'docker_stop requires you to specify "container" when providing mapping.'
                raise exceptions.CommandException(msg)
            container = inp['container']
            timeout = int(inp.get('timeout', 10))
        else:
            container = inp
            timeout = 10
        cls._client.stop(container, timeout)
        return (True, container)

    @classmethod
    def _docker_attach(cls, container_ids):
        result = []
        logres = False
        queue = six.moves.queue.Queue()

        if isinstance(container_ids, six.string_types):
            container_ids = container_ids.split()

        # we need a thread to read from every container
        class ContainerAttacher(threading.Thread):
            def __init__(self, container_id, client):
                super(ContainerAttacher, self).__init__()
                self.cid = container_id
                if '_' not in self.cid and len(self.cid) > 25:  # probably a hash
                    self.nicecid = cid[:12]
                else:
                    self.nicecid = self.cid
                self.client = client
                self.daemon = True

            def _get_container_state_attr(self, attr):
                return self.client.inspect_container(self.cid)['State'][attr]

            def _is_container_running(self):
                return self._get_container_state_attr('Running')

            def run(self):
                """While container is running, queue it's output.
                When it stops, queue None and exit.
                """
                it = self.client.attach(self.cid, stream=True)
                try:
                    line = next(it)
                except StopIteration:
                    line = None

                while line is not None:
                    msg = '{cid}: {out}'.format(cid=self.nicecid, out=line.decode('utf-8').strip())
                    queue.put(msg)
                    try:
                        line = next(it)
                    except StopIteration:
                        line = None

                queue.put('Container {cid} ended with return value {out}'.format(
                    cid=self.cid,
                    out=self._get_container_state_attr('ExitCode')))

        # init threads, read from queue while something is in there and when
        #  all threads exit, finish reading from the queue and join threads
        threads = [ContainerAttacher(cid, cls._client) for cid in container_ids]
        [t.start() for t in threads]
        while any((t.is_alive() for t in threads)) or not queue.empty():
            try:
                line = queue.get(timeout=0.1)
                logger.info(line)
                result.append(line)
            except six.moves.queue.Empty:
                pass
        [t.join() for t in threads]

        return (logres, '\n'.join(result))

    @classmethod
    def _docker_find_img(cls, hash_start):
        # hash start can theoretically be an int, so convert to unicode string either way
        hash_start = six.text_type(hash_start)
        hashes = cls._client.images(quiet=True)
        matching = list(filter(lambda x: x.startswith(hash_start), hashes))

        res = ' '.join(matching)
        # we return True if there is exactly one found hash
        logres = bool(' ' not in res and res)

        return (logres, res)

    @classmethod
    def _docker_get_container_attr(cls, attr, container_id):
        # container id can be either hash or name
        logres = True

        try:
            res = cls._client.inspect_container(container_id)
            # split on dots an loop to get access to nested dicts
            for a in attr.split('.'):
                if not isinstance(res, dict) or a not in res:
                    logres = False
                    res = 'Container doesn\'t have attribute {a}'.format(a=attr)
                else:
                    res = res[a]
        except cls._docker_module.errors.APIError as e:
            msg = 'Failed to obtain container attribute: {e}'.format(e=e)
            raise exceptions.CommandException(msg)

        return (logres, res)


@register_command_runner
class VagrantDockerCommandRunner(CommandRunner):
    @classmethod
    def matches(cls, c):
        return c.comm_type == 'vagrant_docker'

    @classmethod
    def run(cls, c):
        prev_env_vdp = c.kwargs['__env__'].get('VAGRANT_DEFAULT_PROVIDER', None)
        c.kwargs['__env__']['VAGRANT_DEFAULT_PROVIDER'] = 'docker'

        vagrant_cmd = c.input_res.split()[0]
        if vagrant_cmd == 'up':
            res = cls._vagrant_run_cmd(c, 'start', logging.INFO)
        elif vagrant_cmd in ['halt', 'destroy', 'reload']:
            res = cls._vagrant_run_cmd(c, vagrant_cmd)
        else:
            msg = 'Unsupported vagrant docker command {c}, use "cl: vagrant {c}"'.\
                format(c=c.input_res)
            raise exceptions.CommandException(msg)

        if prev_env_vdp is not None:
            c.kwargs['__env__']['VAGRANT_DEFAULT_PROVIDER'] = prev_env_vdp
        return res

    @classmethod
    def _vagrant_run_cmd(cls, c, what, log_level=logging.DEBUG):
        try:
            out = ClHelper.run_command('vagrant ' + c.input_res, log_level=log_level,
                env=c.kwargs['__env__'])
        except exceptions.ClException as e:
            msg = 'Failed to {what} docker containers:\n{out}'.\
                format(what=what, out=e.output)
            raise exceptions.CommandException(msg)

        return (True, cls._docker_containers_from_vagrant_output(out))

    @classmethod
    def _docker_containers_from_vagrant_output(cls, output):
        """Returns list of containers from output of vagrant commands like
        halt, destroy, run, ... (e.g. from lines "==> container_name: blahblah")."""
        c_name_regex = re.compile(r'^\s*=*>\s*([\w]+):\s+')
        containers = []
        for line in output.splitlines():
            match = c_name_regex.search(line)
            if match is not None and match.group(1) not in containers:
                containers.append(match.group(1))
        return containers


@register_command_runner
class NormalizeCommandRunner(CommandRunner):
    @classmethod
    def matches(cls, c):
        return c.comm_type == 'normalize'

    @classmethod
    def _get_args(cls, inp):
        if isinstance(inp, six.string_types):
            return (inp, '')
        elif isinstance(inp, dict):
            if 'what' not in inp:
                raise exceptions.CommandException('"normalize" command expects "what" as input')
            return (inp['what'], inp.get('ok_chars', ''))
        else:
            msg = '"normalize" command expects string or mapping as input'
            raise exceptions.CommandException(msg)

    @classmethod
    def run(cls, c):
        """Normalizes c.input_res (string):

        - removes digit from start
        - replaces dashes and whitespaces with underscores
        """
        to_norm, ok_chars = cls._get_args(c.input_res)

        if six.PY2 and isinstance(to_norm, str):
            to_norm = to_norm.decode('utf8')
        normalized = unicodedata.normalize('NFKD', to_norm)
        if six.PY2:
            normalized = normalized.encode('ascii', 'ignore')
        normalized = normalized.lstrip('0123456789')
        badchars = ''.join(set('-+\\|()[]{}<>,./:\'" \t;`!@#$%^&*') - set(ok_chars))
        if six.PY2:
            tt = string.maketrans(badchars, '_' * len(badchars))
        else:
            tt = str.maketrans(badchars, '_' * len(badchars))
        normalized = normalized.translate(tt)

        # due to unicodedata.normalize, we have to encode and decode as ascii
        #  to actually get a proper string
        normalized = normalized.encode('ascii', 'ignore').decode('ascii')
        return (True, normalized)


@register_command_runner
class SetupProjectDirCommandRunner(CommandRunner):
    @classmethod
    def matches(cls, c):
        return c.comm_type == 'setup_project_dir'

    @classmethod
    def _get_args(cls, inp, ctxt):
        args = {}
        if not isinstance(inp, dict):
            raise exceptions.CommandException('"setup_project_dir" expects mapping as input')

        args['from'] = inp.get('from', None)
        if args['from'] is None:
            raise exceptions.CommandException('"setup_project_dir" requires "from" argument')

        args['contdir_var'] = inp.get('contdir_var', 'contdir')
        args['topdir_var'] = inp.get('topdir_var', 'topdir')
        args['topdir_normalized_var'] = inp.get('topdir_normalized_var', 'topdir_normalized')
        args['accept_path'] = bool(inp.get('accept_path', True))
        args['create_topdir'] = inp.get('create_topdir', True)
        args['normalize_ok_chars'] = inp.get('normalize_ok_chars', '')
        if not args['create_topdir'] in [True, False, 'normalized']:
            msg = '"setup_project_dir" expects "create_topdir" to be one of: ' +\
                'True, False, normalized'
            raise exceptions.CommandException(msg)
        args['on_existing'] = inp.get('on_existing', 'fail')
        if not args['on_existing'] in ['fail', 'pass']:
            msg = '"setup_project_dir" expects "on_existing" to be one of: "fail", "pass"'
            raise exceptions.CommandException(msg)

        return args

    @classmethod
    def run(cls, c):
        args = cls._get_args(c.input_res, c.kwargs)
        if not six.PY3:
            args['from'] = args['from'].encode('utf-8')
        contdir, topdir = os.path.split(args['from'])
        normalized_topdir = lang.Command('normalize',
            {'what': topdir, 'ok_chars': args['normalize_ok_chars']}).run()[1]

        try:  # ok, this is a bit ugly, but we need to check multiple calls for the exception
            if contdir:  # we need to create containing directory
                if not args['accept_path']:
                    msg = 'Path is not accepted as project name by this assistant (got "{0}")'
                    raise exceptions.CommandException(msg.format(args['from']))

                if not os.path.exists(contdir):
                    os.makedirs(contdir)
                elif not os.path.isdir(contdir):
                    msg = 'Can\'t create subdirectory in "{0}", it\'s not a directory'.\
                        format(contdir)
                    raise exceptions.CommandException(msg)
            actual_topdir = normalized_topdir if args['create_topdir'] == 'normalized' else topdir
            topdir_fullpath = os.path.join(contdir, actual_topdir)
            if args['create_topdir']:
                if os.path.exists(topdir_fullpath):
                    if args['on_existing'] == 'fail':
                        msg = 'Directory "{0}" already exists, can\'t proceed'.\
                            format(topdir_fullpath)
                        raise exceptions.CommandException(msg)
                    elif not os.path.isdir(topdir_fullpath):
                        msg = 'Location "{0}" exists, but is not a directory, can\'t proceed'.\
                            format(topdir_fullpath)
                        raise exceptions.CommandException(msg)
                else:
                    os.makedirs(topdir_fullpath)

        except OSError as e:
            msg = 'Failed to create directory {0}: {1}'.format(args['from'], e.message)
            raise exceptions.CommandException(msg)

        # if contdir == '', then return current dir ('.')
        c.kwargs[args['contdir_var']] = contdir or '.'
        c.kwargs[args['topdir_var']] = topdir
        c.kwargs[args['topdir_normalized_var']] = normalized_topdir

        return (True, topdir_fullpath if args['create_topdir'] else contdir)


@register_command_runner
class PingPongCommandRunner(CommandRunner):
    @classmethod
    def matches(cls, c):
        return c.comm_type == 'pingpong'

    @classmethod
    def run(cls, c):
        run = c.input_res
        if isinstance(c.input_res, dict):
            # input_res is a referenced file from files section
            run = os.path.join(c.kwargs['__files_dir__'][-1], c.input_res['source'])

        # TODO: if there is an exception, the subprocess can just keep running, fix this
        proc = subprocess.Popen(run, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, shell=True)

        @utils.atexit
        def kill_atexit_if_alive():
            if proc.poll() is None:
                # if pingpong process is the last command, it may take some time to
                #  terminate, so give it one second
                logger.debug('Waiting for PingPong process invoked by "{0}" to terminate ...'.
                             format(run))
                time.sleep(1)
                if proc.poll() is None:
                    logger.debug('Process didn\'t terminate, killing ...')
                    proc.kill()
                    logger.debug('Killed.')
                else:
                    logger.debug('Process terminated OK.')
        server = dapp.DAPPServer(proc, logger=logger)
        return cls._play_pingpong(server, c.kwargs)

    @classmethod
    def _play_pingpong(cls, server, ctxt):
        # TODO: if we encounter an error on client side, we should terminate it
        # note: ctxt must always be updated with dapp.update_ctxt, so that all changes
        #  are done on the same object and therefore available for subsequent Yaml commands
        # 1) send "run" message
        # 2) recieve first message from the subprocess
        try:
            server.send_msg_run(ctxt)
            msg = server.recv_msg()
        except dapp.DAPPException as e:
            raise exceptions.CommandException(e)

        # 3) receive messages and do whatever the subprocess asks
        while msg:
            if msg['msg_type'] in ['finished', 'failed']:
                break
            elif msg['msg_type'] == 'call_command':
                ct, ci = msg['command_type'], msg['command_input']
                dapp.update_ctxt(ctxt, msg['ctxt'])
                try:
                    lres, res = lang.Command(ct, ci, ctxt).run()
                    server.send_msg_command_result(ctxt, lres=lres, res=res)
                except BaseException as e:
                    server.send_msg_command_exception(ctxt, str(e))
                try:
                    msg = server.recv_msg()
                except dapp.DAPPException as e:
                    raise exceptions.CommandException(e)
            else:
                msg = 'PingPong script sent unexpected message type "{0}".'.format(msg['msg_type'])
                raise exceptions.CommandException(msg)

        # 4) check the last message from subprocess and return proper values
        if not msg:
            raise exceptions.CommandException('Last message from PingPong script was empty!')
        lres = False
        res = ''
        if msg['msg_type'] == 'finished':
            lres = msg['lres']
            res = msg['res']
            dapp.update_ctxt(ctxt, msg['ctxt'])
        elif msg['msg_type'] == 'failed':
            logger.debug('PingPong script failed, failure description logged below as error.')
            raise exceptions.CommandException(msg['fail_desc'])
        else:
            e = 'Wrong message from PingPong script:\n{m}'.format(m=msg)
            raise exceptions.CommandException(e)
        return (lres, res)


@register_command_runner
class LoadCmdCommandRunner(CommandRunner):
    @classmethod
    def matches(cls, c):
        return c.comm_type == 'load_cmd'

    @classmethod
    def _get_args(cls, c):
        load_only = []
        prefix = ''
        from_files_section = False
        if isinstance(c.input_res, dict):
            if 'source' in c.input_res:  # just a file from "files" was passed
                from_file = c.input_res['source']
                from_files_section = True
            elif 'from_file' not in c.input_res:
                msg = '"load_msg" requires "from_file" argument or file from "files" section.'
                raise exceptions.CommandException(msg)
            else:
                load_only = c.input_res.get('load_only', load_only)
                prefix = c.input_res.get('prefix', prefix)
                if isinstance(c.input_res['from_file'], dict):
                    # from_file is "files" section file
                    from_file = c.input_res['from_file']['source']
                    from_files_section = True
                else:
                    from_file = c.input_res['from_file']
        elif isinstance(c.input_res, six.string_types):
            from_file = c.input_res
        else:
            raise exceptions.CommandException('"load_cmd" requires dict or string.')

        if from_files_section:
            # if we have file from "files" section, we can resolve the full path right now
            abs_path = os.path.join(c.kwargs['__files_dir__'][-1], from_file)
            if not os.path.exists(abs_path):
                abs_path = None
        else:
            # else we try to find it in load paths
            abs_path = os.path.join('files', from_file.lstrip(os.path.sep))
            abs_path = utils.find_file_in_load_dirs(abs_path)

        if abs_path is None:
            msg = 'Can\'t load commands from "{0}", file not found.'.format(from_file)
            raise exceptions.CommandException(msg)

        return prefix, abs_path, load_only

    @classmethod
    def run(cls, c):
        prefix, from_file, load_only = cls._get_args(c)
        try:
            # use from_file as module name, but replaces dots, otherwise Python
            #  will think that it separates parent module and complain that the
            #  parent module doesn't exist
            mod_name = from_file.replace('.', '_dot_')
            mod = utils.import_by_path(mod_name, from_file)
        except BaseException as e:
            msg = 'Failed to load commands from "{0}": {1}'.format(from_file, e)
            raise exceptions.CommandException(msg)

        crs = []
        for k, v in vars(mod).items():
            if isinstance(v, type) and issubclass(v, CommandRunner) and v != CommandRunner:
                if not load_only or (k in load_only):
                    register_command_runner(prefix)(v)
                    crs.append(k)

        return (len(crs) > 0, crs)


@register_command_runner
class EnvCommandRunner(CommandRunner):
    @classmethod
    def matches(cls, c):
        return c.comm_type in ['env_set', 'env_unset']

    @classmethod
    def run(cls, c):
        c.kwargs.setdefault('__env__', {})
        res = None
        if c.comm_type == 'env_set':
            if not isinstance(c.input_res, dict):
                raise exceptions.CommandException('env_set expects mapping as input')
            c.kwargs['__env__'].update(c.input_res)
            res = c.input_res
        else:
            res = {}
            # accept a single variable name or a list of names
            if isinstance(c.input_res, six.string_types):
                unset = [c.input_res]
            elif isinstance(c.input_res, list):
                unset = c.input_res
            else:
                raise exceptions.CommandException('env_unset expects string or list as input')
            for k in unset:
                if k in c.kwargs['__env__']:
                    res[k] = c.kwargs['__env__'][k]
                    del c.kwargs['__env__'][k]

        return (True, res)
