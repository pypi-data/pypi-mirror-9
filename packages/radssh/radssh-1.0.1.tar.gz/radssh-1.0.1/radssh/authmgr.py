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
AuthManager module for setting up a concise, flexible collection of available
authentication possibilities to connect to multiple servers via Paramiko.
Supports loading from an authentication file that can contain passwords
or key files, and a way to match them to a host or hosts.
'''

from __future__ import print_function  # Requires Python 2.6 or higher

import os
import warnings
import getpass
import fnmatch
import threading

import paramiko
import netaddr

from .pkcs import PKCS_OAEP, PKCSError
from .hostkey import printable_fingerprint


class PlainText(object):
    '''
    PlainText simply saves the string, and returns it. Nothing fancy.
    '''
    def __init__(self, plaintext):
        self.plaintext = plaintext

    def __str__(self):
        return self.plaintext


class RSAES_OAEP_Text(object):
    '''
    Class to permit decryption of password encoded with user's private key.
    Save the ciphertext, defer the decryption to plaintext until the
    plaintext is requested. Only decrypt on the initial get, save the result
    internally for subsequent calls.
    '''
    decoder_ring = PKCS_OAEP()

    def __init__(self, ciphertext):
        self.ciphertext = ciphertext
        self.plaintext = None
        # Use a lock to avoid multiple threads decrypting
        self.lock = threading.Lock()

    def __str__(self):
        if self.decoder_ring.unsupported:
            return None
        with self.lock:
            if not self.plaintext:
                self.plaintext = self.decoder_ring.decrypt(self.ciphertext)
        return self.plaintext


def _importKey(filename, allow_prompt=True):
    '''
    Import a RSA or DSA key from file contents
    If the key file requires a passphrase, ask for it only if allow_prompt is
    True. Otherwise, reraise the paramiko.PasswordRequiredException. If the
    key fails to load as a RSA key, try loading as DSA key. If it fails both,
    then raises a ValueError with the reported errors from both RSA and DSA
    attempts.
    '''
    # Try RSA first
    try:
        key = paramiko.RSAKey(filename=filename)
        return key
    except paramiko.PasswordRequiredException:
        # Need passphrase for RSA key
        if not allow_prompt:
            raise
        passphrase = getpass.getpass('Enter passphrase for RSA key [%s]: ' % filename)
        key = paramiko.RSAKey(filename=filename, password=passphrase)
        return key
    except paramiko.SSHException as e:
        rsa_exception = e

    # Format error - could be DSA key instead...
    try:
        key = paramiko.DSSKey(filename=filename)
        return key
    except paramiko.PasswordRequiredException:
        # Need passphrase for DSA key
        if not allow_prompt:
            raise
        passphrase = getpass.getpass('Enter passphrase for DSA key [%s]: ' % filename)
        key = paramiko.DSSKey(filename=filename, password=passphrase)
        return key
    except paramiko.SSHException as e:
        dsa_exception = e

    raise ValueError('Unable to key from [%s]\nRSA failure: %r\nDSA failure: %r' % (filename, rsa_exception, dsa_exception))


class AuthManager(object):
    '''Manage keys and passwords used for paramiko authentication'''
    def __init__(self, default_user, auth_file='./.radssh_authfile', include_agent=False, include_userkeys=False, default_password=None, try_auth_none=True):
        self.keys = []
        self.passwords = []
        self.default_password = None
        self.try_auth_none = try_auth_none
        if default_password:
            self.add_password(PlainText(default_password))
        self.deferred_keys = dict()
        if default_user:
            self.default_user = default_user
        else:
            self.default_user = os.environ.get('SSH_USER', os.environ['USER'])

        if include_agent:
            self.agent_connection = paramiko.Agent()
        else:
            self.agent_connection = None

        if include_userkeys:
            for keyfile in ('~/.ssh/id_rsa', '~/.ssh/id_dsa', '~/.ssh/identity'):
                k = os.path.expanduser(keyfile)
                if os.path.exists(k):
                    self.deferred_keys[k] = None
                    self.add_key(k)

        if auth_file:
            self.read_auth_file(auth_file)
        # If we got nothing, prompt the user
        if not (self.agent_connection and self.agent_connection.get_keys()) \
                and not self.passwords and not self.keys and self.default_password is None:
            self.interactive_password()

    def read_auth_file(self, auth_file):
        ''' Read in settings from an authfile. See docs for example format.'''
        try:
            with open(auth_file, 'r') as f:
                for line_no, line in enumerate(f, 1):
                    line = line.rstrip('\n\r')
                    fields = line.split('|', 2)
                    if not line.strip() or fields[0].startswith('#'):
                        continue
                    if len(fields) == 3:
                        filter = fields.pop(1)
                    else:
                        filter = None
                    data = fields[-1]
                    if fields[0] == 'password' or len(fields) == 1:
                        self.add_password(PlainText(data), filter)
                    elif fields[0] == 'PKCSOAEP':
                        try:
                            encrypted_password = RSAES_OAEP_Text(data)
                            if encrypted_password.decoder_ring.unsupported:
                                warnings.warn(RuntimeWarning(
                                    'Ignoring unusable PKCSOAEP encrypted password from [%s:%d]' %
                                    (auth_file, line_no)))
                                continue
                            self.add_password(encrypted_password, filter)
                        except Exception as e:
                            warnings.warn(RuntimeWarning('Failed to load PKCS encrypted password [%s:%d]\n%s' % (auth_file, line_no, repr(e))))
                    elif fields[0] == 'keyfile':
                        k = os.path.expanduser(data)
                        if os.path.exists(k):
                            self.deferred_keys[k] = None
                            self.add_key(k, filter)
                        else:
                            raise ValueError('Unable to load key from [%s]\n%r' % k)
                    else:
                        warnings.warn(RuntimeWarning('Unsupported auth type [%s:%d] %s' % (auth_file, line_no, fields[0])))
        except IOError:
            # Quietly fail if auth_file cannot be read
            pass

    def add_password(self, password, filter=None):
        '''Append to list of passwords to try based on filtering, but only keep at most one default'''
        if filter:
            self.passwords.append((filter, password))
        else:
            self.default_password = password

    def add_key(self, key, filter=None):
        '''Append to a list of explicit keys to try, separate from any agent keys'''
        self.keys.append((filter, key))

    def authenticate(self, T):
        '''
        Try available ways to authenticate a paramiko Transport.
        Attempts are made in the following progression:
        - User keys (~/.ssh/id_rsa, id_dsa, identity) if loaded
        - Explicit keys loaded from authfile (for matched hostname/IP)
        - Keys available via SSH Agent (if enabled)
        - Passwords loaded from authfile
        - Default password (if set)
        '''
        if T.is_authenticated():
            return
        if not T.is_active():
            T.connect()
        # Do an auth_none() call for 3 reasons:
        #    1) Get server response for available auth mechanisms
        #    2) OpenSSH 4.3 (CentOS5) fails to send banner unless this is done
        #       http://www.frostjedi.com/phpbb3/viewtopic.php?f=46&t=168230#p391496
        #    3) https://github.com/paramiko/paramiko/issues/432 workaround requires
        #       hacky save/restore of banner to keep Transport.get_banner() content
        try:
            connected = False
            save_banner = None
            server_authtypes_supported = ['publickey', 'password']
            if self.try_auth_none:
                T.auth_none(self.default_user)
                # If by some miracle or misconfiguration, auth_none succeeds...
                return True
        except paramiko.BadAuthenticationType as e:
            server_authtypes_supported = e.allowed_types

        # Part 1: Save the banner from auth_none response
        if hasattr(T, 'get_banner'):
            save_banner = T.get_banner()

        if 'publickey' in server_authtypes_supported:
            # Try explicit keys first
            connected = self.try_auth(T, self.keys)
            # Next, try agent keys, if enabled
            if not connected and self.agent_connection:
                # possibly re-trigger key broker,
                # then fabricate a list of filterless keys from ssh-agent
                agent_connection = paramiko.Agent()
                agent_keys = [(None, x) for x in agent_connection.get_keys()]
                connected = self.try_auth(T, agent_keys)
                # Early versions of Paramiko would raise exception if
                # attempting to close Agent socket if there was no running ssh-agent
                # AttributeError: Agent instance has no attribute 'conn'
                try:
                    agent_connection.close()
                except AttributeError:
                    pass

        # Attempt password if applicable. Include keyboard-interactive as well,
        # since it typically works with fallback, and we don't currently handle
        # full scope of keyboard-interactive (yet)
        if 'password' in server_authtypes_supported or 'keyboard-interactive' in server_authtypes_supported:
            if not connected:
                connected = self.try_auth(T, self.passwords, True)
            # Final step - try a default password (unfiltered)
            if not connected:
                if self.default_password:
                    connected = self.try_auth(T, [(None, self.default_password)], True)

        # Part 2 of save_banner workaround - shove it into the current auth_handler
        if hasattr(T, 'get_banner') and save_banner:
            T.auth_handler.banner = save_banner
        return connected

    def interactive_password(self):
        self.default_password = PlainText(getpass.getpass(
            'Please enter a password for (%s) :' % self.default_user))

    def __str__(self):
        return '<%s for %s : [%d Keys, Agent %s, %d Passwords]>' \
            % (self.__class__.__name__,
               self.default_user,
               len(self.keys),
               'Enabled' if self.agent_connection else 'Disabled',
               len(self.passwords))

    def try_auth(self, T, candidates, as_password=False):
        for filter, value in candidates:
            if filter and filter != '*':
                remote_ip = netaddr.IPAddress(T.getpeername()[0])
                try:
                    subnet = netaddr.IPGlob(filter)
                    if remote_ip not in subnet:
                        continue
                except netaddr.AddrFormatError:
                    try:
                        subnet = netaddr.IPNetwork(filter)
                        if remote_ip not in subnet:
                            continue
                    except netaddr.AddrFormatError:
                        # Not a subnet or IPGlob - try name based matching (fnmatch style, not regex)
                        if not fnmatch.fnmatch(T.name, filter):
                            continue
            try:
                if as_password:
                    key = value
                    # Quirky Force10 servers seem to request further password attempt
                    # for a second stage - retry password as long as it is listed as an option
                    while True:
                        if 'password' not in T.auth_password(self.default_user, str(key)):
                            break
                else:
                    # Actual keys may not be loaded yet. Only loaded when actively used, so
                    # we don't prompt for passphrases unless we absolutely have to.
                    if value not in self.deferred_keys:
                        # Not deferred - the value IS the key
                        key = value
                    elif not self.deferred_keys[value]:
                        # Deferred, and not yet loaded - try _importKey()
                        self.deferred_keys[value] = _importKey(value)
                        key = self.deferred_keys[value]
                    else:
                        # Deferred and already loaded
                        key = self.deferred_keys[value]
                    try:
                        T.auth_publickey(self.default_user, key)
                    except paramiko.BadAuthenticationType as e:
                        # Server configured to reject keys, don't bother trying any others
                        return None
                if T.is_authenticated():
                    return key
            except paramiko.AuthenticationException as e:
                pass

        return None

if __name__ == '__main__':
    import sys
    if not sys.argv[1:]:
        print('RadSSH AuthManager')
        print('Usage: python -m radssh.authmgr <authfile> [...]')
    for authfile in sys.argv[1:]:
        authfile = os.path.expanduser(authfile)
        sample = AuthManager(os.path.basename(authfile), auth_file=authfile, default_password='')
        print('\nLoaded authfile:', authfile)
        print(sample)
        if sample.keys:
            print('Explicit keys (%d)' % len(sample.keys))
            for filter, keyfile in sample.keys:
                if keyfile in sample.deferred_keys:
                    try:
                        key = _importKey(keyfile, False)
                        key_info = '%s (%s:%d bit)' % (keyfile, key.get_name(), key.get_bits())
                    except Exception as e:
                        key_info = '%s (Passphrase-Protected)' % (keyfile)
                if not filter:
                    filter = '(ALL)'
                print('\t', key_info, 'for hosts matching:', filter)
        else:
            print('No explicit keys loaded')
        if sample.agent_connection:
            agent_keys = sample.agent_connection.get_keys()
            print('SSH Agent available (contains %d keys)' % len(agent_keys))
            for key in agent_keys:
                print('\t', key.get_name(), printable_fingerprint(key))
        else:
            print('No SSH Agent connection')
        if sample.passwords:
            print('Explicit passwords (%d)' % len(sample.passwords))
            for filter, password in sample.passwords:
                if not filter:
                    filter = '(ALL)'
                print('\t', repr(password), 'for hosts matching:', filter)
        else:
            print('No explicit passwords loaded')
        if sample.default_password:
            print('Authfile includes a default password [%s]' % repr(sample.default_password))
