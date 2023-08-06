import json
import logging
import pexpect
import pwd
import requests
import subprocess

import aj
from aj.api import *
from aj.api.http import BaseHttpHandler
from aj.security.verifier import ClientCertificateVerificator
from aj.util import *


class SudoError(Exception):
    def __init__(self, message):
        Exception.__init__(self)
        self.message = message


@public
@service
class AuthenticationMiddleware(BaseHttpHandler):
    def __init__(self, context):
        self.context = context
        self.auth = AuthenticationService.get(self.context)
        if not hasattr(context, 'identity'):
            context.identity = None

    def handle(self, http_context):
        if http_context.env['SSL_CLIENT_VALID']:
            if not self.context.identity:
                username = http_context.env['SSL_CLIENT_USER']
                logging.info(
                    'SSL client certificate %s verified as %s',
                    http_context.env['SSL_CLIENT_DIGEST'],
                    username
                )
                try:
                    pwd.getpwnam(username)
                    found = True
                except KeyError:
                    found = False
                if found:
                    self.auth.login(username)

        http_context.add_header('X-Auth-Identity', str(self.context.identity or ''))


@public
@service
class AuthenticationService(object):
    def __init__(self, context):
        self.context = context

    def check_password(self, username, password):
        child = None
        try:
            child = pexpect.spawn('/bin/su', ['-c', '/bin/echo SUCCESS', '-', username], timeout=5)
            child.expect('.*:')
            child.sendline(password)
            result = child.expect(['su: .*', 'SUCCESS'])
        except Exception as err:
            if child and child.isalive():
                child.close()
            logging.error('Error checking password: %s', err)
            return False
        if result == 0:
            return False
        else:
            return True

    def check_sudo_password(self, username, password):
        sudo = subprocess.Popen(
            ['sudo', '-S', '-u', 'eugene', '--', 'sh', '-c', 'sudo -k; sudo -S echo'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        o, e = sudo.communicate(password + '\n')
        if sudo.returncode != 0:
            raise SudoError((o + e).splitlines()[-1].strip())
        return True

    def check_persona_assertion(self, assertion, audience):
        params = {
            'assertion': assertion,
            'audience': audience,
        }

        resp = requests.post('https://verifier.login.persona.org/verify', data=params, verify=True)

        if resp.ok:
            verification_data = json.loads(resp.content)
            if verification_data['status'] == 'okay':
                email = verification_data['email']
                return email
            else:
                raise Exception('Persona auth failed')
        else:
            raise Exception('Request failed')

    def client_certificate_callback(self, connection, x509, errno, depth, result):
        if depth == 0 and (errno == 9 or errno == 10):
            return False  # expired / not yet valid
        if not aj.config.data['ssl']['client_auth']['force']:
            return True
        user = ClientCertificateVerificator.get(aj.context).verify(x509)
        return bool(user)

    def get_identity(self):
        return self.context.identity

    def login(self, username, demote=True):
        logging.info('Authenticating session as %s', username)
        if demote:
            self.context.worker.demote(username)
        self.context.identity = username

    def prepare_session_redirect(self, http_context, username):
        http_context.add_header('X-Session-Redirect', username)
