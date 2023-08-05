#!/usr/bin/env python
#
# Copyright (c) 2014 LexisNexis Risk Data Management Inc.
#
# This file is part of the RadSSH software package.
#
# RadSSH is free software, released under the Revised BSD License.
# You are permitted to use, modify, and redsitribute this software
# according to the Revised BSD License, a copy of which should be
# included with the distribution as file LICENSE.txt
#

'''
Python wrapper for parallel execution shell
===========================================

*** This module should be run, not imported ***

Usage: ```python -m radssh.shell host [...]```

Will read settings from /etc/radssh_config, and supplement with ~/.radssh_config.
Settings may also be provided on the command line, using the form --keyword=value.
'''
from __future__ import print_function  # Requires Python 2.6 or higher


import sys
import os
import time
import socket
import pprint
import readline
import atexit
import traceback

import paramiko

from . import ssh
from . import config
from . import star_commands as star
from .console import RadSSHConsole, monochrome
import radssh.plugins

################################################################################

command_listeners = []


def shell(cluster, logdir=None, playbackfile=None, defaults=None):
    '''Very basic interactive shell'''
    if not defaults:
        defaults = config.load_default_settings()
    try:
        while True:
            if playbackfile:
                try:
                    cmd = next(playbackfile)
                    print('%s %s' % (defaults['shell.prompt'], cmd.strip()))
                except StopIteration:
                    break
            else:
                try:
                    cmd = raw_input('%s ' % defaults['shell.prompt'])
                except KeyboardInterrupt:
                    print('\n<Ctrl-C> during input\nUse EOF (<Ctrl-D>) or *exit to exit shell\n')
                    continue
                # Feed command line to any registered listeners from plugins
                for feed in command_listeners:
                    feed(cmd)
                with open(os.path.join(logdir, 'session.commands'), 'a') as f:
                    f.write('%s\n' % cmd)
            args = cmd.split()
            if len(args) > 0:
                if os.path.basename(args[0]) == 'sudo' and len(args) > 1:
                    initial_command = os.path.basename(args[1])
                else:
                    initial_command = os.path.basename(args[0])
                if initial_command in defaults['commands.forbidden'].split(','):
                    print('You really don\'t want to run %s without a TTY, do you?' % initial_command)
                    continue
                if initial_command in defaults['commands.restricted'].split(','):
                    print('Whoa, Cowboy! Are you sure you want to run the following command, Tex?')
                    print('Please double check all parameters, just to be sure...')
                    print('   >>>', cmd)
                    confirm = raw_input('Enter \'100%\' if completely sure: ')
                    if confirm != '100%':
                        continue
                if args[0].startswith('#'):
                    # Comment
                    continue
                if args[0].startswith('*'):
                    ret = star.call(cluster, logdir, cmd, (defaults['verbose'] == 'on'))
                    cluster.console.join()
                    if isinstance(ret, ssh.Cluster):
                        cluster.console.message('Switched cluster from %r to %r' % (cluster, ret))
                        cluster = ret
                    continue
                r = cluster.run_command(cmd)
                if logdir:
                    cluster.log_result(logdir)
                # Quick summary report, if jobs failed
                failures = {}
                completions = []
                completion_time = 0.0
                for k, job in r.items():
                    v = job.result
                    if job.completed:
                        if v.return_code == 0:
                            completions.append(k)
                            completion_time += job.end_time - job.start_time
                        else:
                            failures.setdefault(v.return_code, []).append(k)
                    else:
                        failures.setdefault(None, []).append(k)
                if failures:
                    print('\nSummary of failures:')
                    for k, v in failures.items():
                        if len(v) > 5:
                            print(k, '\t- (%d hosts)' % len(v))
                        else:
                            print(k, '\t-', sorted(v))
                if completions:
                    print('Average completion time for %d hosts: %fs' % (len(completions), (completion_time / len(completions))))
    except EOFError as e:
        print(e)
    print('Shell exiting')
    cluster.close_connections()

################################################################################
# Readline/libedit command completion
# Supports *commands, executables (LOCAL), and path (REMOTE) completion


class radssh_tab_handler(object):
    '''Class wrapper for readline TAB key completion'''
    def __init__(self, cluster, star):
        # Need access to the cluster object to get SFTP service
        # for remote path completion, and the star command dictionary
        # to know what *commands are available.
        self.cluster = cluster
        self.star = star
        try:
            self.using_libedit = ('libedit' in readline.__doc__)
        except TypeError:
            # pyreadline (windows) readline.__doc__ is None (not iterable)
            self.using_libedit = False
        self.completion_choices = []
        readline.set_completer()
        readline.set_completer(self.complete)
        readline.set_completer_delims(' \t\n/*')
        if self.using_libedit:
            readline.parse_and_bind('bind ^I rl_complete')
        else:
            readline.parse_and_bind('tab: complete')

    def complete_star_command(self, lead_in, text, state):
        if state == 0:
            # Rebuild cached list of choices that match
            # Reset list to empty (choices = [] would reference local, not persistent list)
            del self.completion_choices[:]
            for choice in self.star.commands.keys():
                if choice.startswith(lead_in):
                    self.completion_choices.append(choice + ' ')
        # Discrepancy with readline/libedit and handling of leading *
        if self.using_libedit:
            return self.completion_choices[state]
        else:
            return self.completion_choices[state][1:]

    def complete_executable(self, lead_in, text, state):
        if state == 0:
            del self.completion_choices[:]
            for path_dir in os.environ['PATH'].split(os.path.pathsep):
                try:
                    for f in os.listdir(path_dir):
                        try:
                            if os.path.isdir(os.path.join(path_dir, f)):
                                continue
                            st = os.stat(os.path.join(path_dir, f))
                            if (st.st_mode & 0o111) and f.startswith(text):
                                self.completion_choices.append(f + ' ')
                        except OSError as e:
                            continue
                except OSError as e:
                    continue
            self.completion_choices.append(None)
        return self.completion_choices[state]

    def complete_remote_path(self, lead_in, text, state):
        if state == 0:
            del self.completion_choices[:]
            for t in self.cluster.connections.values():
                if t.is_authenticated():
                    break
            else:
                print('No authenticated connections')
                raise RuntimeError('Tab Completion unavailable')
            s = t.open_sftp_client()
            parent = os.path.dirname(lead_in)
            partial = os.path.basename(lead_in)
            if not parent:
                parent = './'
            for x in s.listdir(parent):
                if x.startswith(partial):
                    full_path = os.path.join(parent, x)
                    try:
                        # See if target is a directory, and append '/' if it is
                        s.chdir(full_path)
                        x += '/'
                        full_path += '/'
                    except Exception as e:
                        pass
                    if self.using_libedit:
                        self.completion_choices.append(full_path)
                    else:
                        self.completion_choices.append(x)
            self.completion_choices.append(None)
        return self.completion_choices[state]

    def complete_local_path(self, lead_in, text, state):
        if state == 0:
            del self.completion_choices[:]
            parent = os.path.dirname(lead_in)
            partial = os.path.basename(lead_in)
            if not parent:
                parent = './'
            for x in os.listdir(parent):
                if x.startswith(partial):
                    full_path = os.path.join(parent, x)
                    if os.path.isdir(full_path):
                        # See if target is a directory, and append '/' if it is
                        x += '/'
                        full_path += '/'
                    if self.using_libedit:
                        self.completion_choices.append(full_path)
                    else:
                        self.completion_choices.append(x)
            self.completion_choices.append(None)
        return self.completion_choices[state]

    def complete(self, text, state):
        buffer = readline.get_line_buffer()
        lead_in = buffer[:readline.get_endidx()].split()[-1]
        try:
            if buffer.startswith('*') and ' ' in buffer:
                # See if *command has custom tab completion
                star_command = self.star.commands.get(buffer.split()[0], None)
                if star_command and star_command.tab_completion:
                    return star_command.tab_completion(self, buffer, lead_in, text, state)
            if lead_in.startswith('*'):
                # User needs help completing *command...
                return self.complete_star_command(lead_in, text, state)
            else:
                # Default behavior - remote file path completion
                return self.complete_remote_path(lead_in, text, state)
        except Exception as e:
            raise


################################################################################

def radssh_shell_main():
    args = sys.argv[1:]
    defaults = config.load_settings(args)

    if 'socket.timeout' in defaults:
        socket.setdefaulttimeout(float(defaults['socket.timeout']))

    # Make an AuthManager to handle user authentication
    a = ssh.AuthManager(defaults['username'],
                        auth_file=os.path.expanduser(defaults['authfile']),
                        include_agent=(defaults['ssh-agent'] == 'on'),
                        include_userkeys=(defaults['ssh-identity'] == 'on'),
                        try_auth_none=(defaults['try_auth_none'] == 'on'))

    # Load Plugins to aid in host lookups and add *commands dynamically
    loaded_plugins = {}
    plugin_failures = []
    exe_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
    system_plugin_dir = os.path.join(exe_dir, 'plugins')
    disable_plugins = defaults['disable_plugins'].split(',')
    plugin_dirs = [x for x in defaults['plugins'].split(';') if x]
    plugin_dirs.append(system_plugin_dir)

    for x in plugin_dirs:
        plugin_dir = os.path.abspath(os.path.expanduser(x))
        if not os.path.exists(plugin_dir):
            continue
        for module in sorted(os.listdir(plugin_dir)):
            if module.endswith('.py') and not module.startswith('__'):
                plugin = module[:-3]
                # Skip modules found in more that 1 location, and ones explicitly disabled
                if plugin in loaded_plugins or plugin in disable_plugins:
                    continue
                try:
                    this_plugin = radssh.plugins.load_plugin(os.path.join(plugin_dir, module))
                    if hasattr(this_plugin, 'init'):
                        this_plugin.init(defaults=defaults, auth=a, plugins=loaded_plugins, star_commands=star.commands, shell=shell)
                    if hasattr(this_plugin, 'star_commands'):
                        star.commands.update(this_plugin.star_commands)
                    if hasattr(this_plugin, 'command_listener'):
                        command_listeners.append(this_plugin.command_listener)
                    loaded_plugins[plugin] = this_plugin
                    if defaults['verbose'] == 'on':
                        print('Loaded plugin %s' % plugin)

                except Exception as e:
                    plugin_failures.append((os.path.join(plugin_dir, module), sys.exc_info()))

    if plugin_failures:
        print('*** %d plugin(s) failed to load. ***' % len(plugin_failures))
        if defaults['verbose'] != 'on':
            print('    Use --verbose=on option to see details.')
        else:
            for path, exc in plugin_failures:
                print('    ', path)
                print('        ', exc[1])  # Exception Value
                print('-' * 50)
                traceback.print_tb(exc[2])  # Traceback
                print('-' * 50)

    # Use command line args as connect list, or give user option to supply list now
    if not args:
        print('No command line arguments given.')
        print('You can connect to a number of hosts by hostname or IP')
        if loaded_plugins:
            print('You can also give symbolic names that can be translated by')
            print('the following loaded plugins:')
            for module, plugin in loaded_plugins.items():
                try:
                    lookup_doc = plugin.lookup.__doc__
                    print(module, plugin.__doc__)
                    print('\t%s' % lookup_doc)
                    try:
                        plugin.banner()
                    except AttributeError:
                        pass
                except AttributeError:
                    pass
        connect_list = raw_input('Enter a list of connection destinations: ').split()
    else:
        connect_list = args

    if not connect_list:
        sys.exit(0)

    # Do the connections if needed, offer names to plugin lookup() functions
    hosts = []
    for arg in connect_list:
        expanded = False
        for helper, resolver in loaded_plugins.items():
            cluster = None
            try:
                cluster = resolver.lookup(arg)
            except AttributeError as e:
                # No lookup function in plugin, pass quietly
                pass
            except Exception as e:
                print(repr(e))
                pass
            if cluster:
                expanded = True
                print(arg, 'expanded by', helper)
                for label, host, conn in cluster:
                    if conn:
                        hosts.append((label, conn))
                    else:
                        hosts.append((label, host))
                break
        if not expanded:
            hosts.append((arg, arg))

    # Setup Logging
    logdir = os.path.expanduser(time.strftime(defaults['logdir']))
    if not os.path.exists(logdir):
        os.mkdir(logdir)
    if defaults.get('paramiko_log_level'):
        paramiko.util.log_to_file(os.path.join(logdir, 'paramiko.log'),
                                  int(defaults['paramiko_log_level']))

    # Almost done with all the preliminary setup steps...
    if defaults['verbose'] == 'on':
        print('*** Parallel Shell ***')
        print('Using AuthManager:', a)
        print('Logging to %s' % logdir)
        pprint.pprint(defaults, indent=4)
        print()
        star.star_help()

    # Create a RadSSHConsole instance for screen output
    if defaults['shell.console'] != 'color' or not sys.stdout.isatty():
        console = RadSSHConsole(formatter=monochrome)
    else:
        console = RadSSHConsole()

    # Finally, we are able to create the Cluster
    print('Connecting to %d hosts...' % len(hosts))
    cluster = ssh.Cluster(hosts, auth=a, console=console, defaults=defaults)
    if defaults['verbose'] == 'on':
        star.star_info(cluster, logdir, '', [])

    # Command line history support
    if defaults.get('historyfile'):
        histfile = os.path.expanduser(defaults['historyfile'])
        try:
            readline.read_history_file(histfile)
        except IOError:
            pass
        readline.set_history_length(int(os.environ.get('HISTSIZE', 1000)))
        atexit.register(readline.write_history_file, histfile)

    # Add TAB completion for *commands and remote file paths
    tab_completion = radssh_tab_handler(cluster, star)

    # With the cluster object, start interactive session
    shell(cluster=cluster, logdir=logdir, defaults=defaults)


if __name__ == '__main__':
    radssh_shell_main()
