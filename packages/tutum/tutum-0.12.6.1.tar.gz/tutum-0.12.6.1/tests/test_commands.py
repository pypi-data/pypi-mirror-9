# -*- coding: utf-8 -*-
import unittest
import __builtin__
import StringIO
import uuid

import mock
from tutum.api.exceptions import *

from tutumcli.commands import *
import tutumcli


class LoginTestCase(unittest.TestCase):
    def setUp(self):
        # backup configfile
        self.data = None
        file = None
        try:
            configFile = os.path.join(os.path.expanduser('~'), TUTUM_FILE)
            file = open(configFile, 'r')
            self.data = file.read()
        except:
            pass
        finally:
            if file:
                file.close()

        self.raw_input_holder = __builtin__.raw_input
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        sys.stdout = self.stdout_buf = StringIO.StringIO()
        sys.stderr = self.stderr_buf = StringIO.StringIO()

    def tearDown(self):
        __builtin__.raw_input = self.raw_input_holder
        sys.stdout = self.stdout
        sys.stdout = self.stderr

        if self.data:
            file = None
            try:
                configFile = os.path.join(os.path.expanduser('~'), TUTUM_FILE)
                file = open(configFile, 'w')
                file.write(self.data)
            except:
                pass
            finally:
                if file:
                    file.close()

    def set_username(self, username):
        __builtin__.raw_input = lambda _: username

    @mock.patch('tutumcli.commands.getpass.getpass', return_value='test_password')
    @mock.patch('tutumcli.commands.tutum.auth.get_auth')
    def test_login_success(self, mock_get_auth, mock_password):
        user = uuid.uuid4()
        apikey = uuid.uuid4()
        __builtin__.raw_input = lambda _: user  # set username
        mock_get_auth.return_value = (user, apikey)
        login()
        out = self.stdout_buf.getvalue().strip()
        self.stdout_buf.truncate(0)
        self.assertEqual('Login succeeded!', out)
        configFile = os.path.join(os.path.expanduser('~'), TUTUM_FILE)
        output = '''[auth]
user = %s
apikey = %s''' % (user, apikey)
        file = open(configFile, 'r')
        try:
            data = file.read()
            self.assertEqual(output.strip(), data.strip())
        finally:
            file.close()
            os.remove(configFile)

    @mock.patch('tutumcli.commands.utils.try_register', return_value=(True, 'Registration succeeded!'))
    @mock.patch('tutumcli.commands.getpass.getpass', return_value='test_password')
    @mock.patch('tutumcli.commands.tutum.auth.get_auth', side_effect=TutumAuthError)
    def test_login_register_success(self, mock_get_auth, mock_getpass, mock_register):
        __builtin__.raw_input = lambda _: 'test_username'  # set username
        login()
        mock_register.assert_called_with('test_username', 'test_password')
        out = self.stdout_buf.getvalue().strip()
        self.stdout_buf.truncate(0)
        self.assertEqual('Registration succeeded!', out)

    @mock.patch('tutumcli.commands.utils.try_register',
                return_value=(False, 'ERROR: username: A user with that username already exists.'))
    @mock.patch('tutumcli.commands.sys.exit')
    @mock.patch('tutumcli.commands.getpass.getpass', return_value='test_password')
    @mock.patch('tutumcli.commands.tutum.auth.get_auth', side_effect=TutumAuthError)
    def test_login_register_user_exist(self, mock_get_auth, mock_getpass, mock_exit, mock_register):
        __builtin__.raw_input = lambda _: 'test_username'  # set username
        login()
        mock_register.assert_called_with('test_username', 'test_password')
        out = self.stderr_buf.getvalue().strip()
        self.stderr_buf.truncate(0)
        self.assertEqual('Wrong username and/or password. Please try to login again', out)
        mock_exit.assert_called_with(TUTUM_AUTH_ERROR_EXIT_CODE)

    @mock.patch('tutumcli.commands.utils.try_register',
                return_value=(False, 'password1: This field is required.\npassword2: This field is required.'
                                     '\nemail: This field is required.'))
    @mock.patch('tutumcli.commands.sys.exit')
    @mock.patch('tutumcli.commands.getpass.getpass', return_value='test_password')
    @mock.patch('tutumcli.commands.tutum.auth.get_auth', side_effect=TutumAuthError)
    def test_login_register_password_required(self, mock_get_auth, mock_getpass, mock_exit, mock_register):
        __builtin__.raw_input = lambda _: 'test_username'  # set username
        login()
        mock_register.assert_called_with('test_username', 'test_password')
        out = self.stderr_buf.getvalue().strip()
        self.stderr_buf.truncate(0)
        self.assertEqual('password: This field is required.\nemail: This field is required.', out)
        mock_exit.assert_called_with(TUTUM_AUTH_ERROR_EXIT_CODE)

    @mock.patch('tutumcli.commands.sys.exit')
    @mock.patch('tutumcli.commands.getpass.getpass', return_value='test_password')
    @mock.patch('tutumcli.commands.tutum.auth.get_auth', side_effect=Exception('Cannot open config file'))
    def test_login_register_Exception(self, mock_get_auth, mock_getpass, mock_exit):
        __builtin__.raw_input = lambda _: 'test_username'  # set username
        login()
        out = self.stderr_buf.getvalue().strip()
        self.stderr_buf.truncate(0)
        self.assertEqual('Cannot open config file', out)
        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)


class ServiceCreateTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()

    def tearDown(self):
        sys.stdout = self.stdout

    @mock.patch('tutumcli.commands.tutum.Service.start')
    @mock.patch('tutumcli.commands.tutum.Service.save')
    @mock.patch('tutumcli.commands.tutum.Service.create')
    def test_service_create(self, mock_create, mock_save, mock_start):
        exposed_ports = [800, 222]
        published_ports = ['80:80/tcp', '22:22']
        ports = utils.parse_published_ports(published_ports)
        ports.extend(utils.parse_exposed_ports(exposed_ports))
        container_envvars = ['MYSQL_ADMIN=admin', 'MYSQL_PASS=password']
        linked_to_service = ['mysql:mysql', 'redis:redis']

        service = tutumcli.commands.tutum.Service()
        service.uuid = '7A4CFE51-03BB-42D6-825E-3B533888D8CD'
        mock_create.return_value = service
        service_create('imagename', 'containername', 1, '256M', True, 3, '-d', '/bin/mysql',
                       exposed_ports, published_ports, container_envvars, [], '', linked_to_service,
                       'OFF', 'OFF', 'OFF', 'poweruser', True, None, None, None)

        mock_create.assert_called_with(image='imagename', name='containername', cpu_shares=1,
                                       memory='256M', privileged=True,
                                       target_num_containers=3, run_command='-d',
                                       entrypoint='/bin/mysql', container_ports=ports,
                                       container_envvars=utils.parse_envvars(container_envvars, []),
                                       linked_to_service=utils.parse_links(linked_to_service, 'to_service'),
                                       autorestart='OFF', autodestroy='OFF', autoredeploy='OFF',
                                       roles='poweruser', sequential_deployment=True, tags=[], bindings=[],
                                       deployment_strategy=None)
        mock_save.assert_called()
        mock_start.assert_not_called()
        self.assertEqual(service.uuid, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('tutumcli.commands.tutum.Service.start')
    @mock.patch('tutumcli.commands.tutum.Service.save')
    @mock.patch('tutumcli.commands.tutum.Service.create')
    def test_service_create_exposing_publishing_same_port(self, mock_create, mock_save, mock_start):
        exposed_ports = [80]
        published_ports = ['800:80/tcp']
        ports = [{'inner_port': '80', 'outer_port': '800', 'protocol': 'tcp', 'published': True}]
        container_envvars = ['MYSQL_ADMIN=admin', 'MYSQL_PASS=password']
        linked_to_service = ['mysql:mysql', 'redis:redis']
        service = tutumcli.commands.tutum.Service()
        service.uuid = '7A4CFE51-03BB-42D6-825E-3B533888D8CD'
        mock_create.return_value = service
        service_run('imagename', 'containername', 1, '256M', True, 3, '-d', '/bin/mysql',
                    exposed_ports, published_ports, container_envvars, [], '', linked_to_service,
                    'OFF', 'OFF', 'OFF', 'poweruser', True, None, None, None)

        mock_create.assert_called_with(image='imagename', name='containername', cpu_shares=1,
                                       memory='256M', privileged=True,
                                       target_num_containers=3, run_command='-d',
                                       entrypoint='/bin/mysql', container_ports=ports,
                                       container_envvars=utils.parse_envvars(container_envvars, []),
                                       linked_to_service=utils.parse_links(linked_to_service, 'to_service'),
                                       autorestart='OFF', autodestroy='OFF', autoredeploy='OFF',
                                       roles='poweruser', sequential_deployment=True, tags=[], bindings=[],
                                       deployment_strategy=None)
        mock_save.assert_called()
        mock_start.assert_not_called()
        self.assertEqual(service.uuid, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('tutumcli.commands.sys.exit')
    @mock.patch('tutumcli.commands.tutum.Service.create', side_effect=TutumApiError)
    def test_service_create_with_exception(self, mock_create, mock_exit):
        exposed_ports = ['80', '22']
        published_ports = ['80:80/tcp', '22:22']
        container_envvars = ['MYSQL_ADMIN=admin', 'MYSQL_PASS=password']
        linked_to_service = ['mysql:mysql', 'redis:redis']
        service_create('imagename', 'containername', 1, '256M', True, 3, '-d', '/bin/mysql',
                       exposed_ports, published_ports, container_envvars, [], '', linked_to_service,
                       'OFF', 'OFF', 'OFF', 'poweruser', True, None, None, None)

        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)


class ServiceInspectTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()

    def tearDown(self):
        sys.stdout = self.stdout

    @mock.patch('tutumcli.commands.tutum.Service.get_all_attributes')
    @mock.patch('tutumcli.commands.utils.fetch_remote_service')
    def test_service_inspect(self, mock_fetch_remote_service, mock_get_all_attributes):
        output = '''{
  "key": [
    {
      "name": "test",
      "id": "1"
    }
  ]
}'''
        uuid = '7A4CFE51-03BB-42D6-825E-3B533888D8CD'
        service = tutumcli.commands.tutum.Service()
        service.uuid = uuid
        mock_fetch_remote_service.return_value = service
        mock_get_all_attributes.return_value = {'key': [{'name': 'test', 'id': '1'}]}
        service_inspect(['test_id'])

        self.assertEqual(' '.join(output.split()), ' '.join(self.buf.getvalue().strip().split()))
        self.buf.truncate(0)

    @mock.patch('tutumcli.commands.sys.exit')
    @mock.patch('tutumcli.commands.utils.fetch_remote_service', side_effect=TutumApiError)
    def test_service_inspect_with_exception(self, mock_fetch_remote_service, mock_exit):
        service = tutumcli.commands.tutum.Service()
        mock_fetch_remote_service.return_value = service
        service_inspect(['test_id', 'test_id2'])

        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)


class ServiceLogsTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()

    def tearDown(self):
        sys.stdout = self.stdout

    @mock.patch('tutumcli.commands.utils.fetch_remote_service')
    def test_service_logs(self, mock_fetch_remote_service):
        log = 'Here is the log'
        service = tutumcli.commands.tutum.Service
        service.logs = log
        mock_fetch_remote_service.return_value = service
        service_logs(['test_id'])

        self.assertEqual(log, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('tutumcli.commands.sys.exit')
    @mock.patch('tutumcli.commands.utils.fetch_remote_service', side_effect=TutumApiError)
    def test_service_logs_with_exception(self, mock_fetch_remote_service, mock_exit):
        service = tutumcli.commands.tutum.Service()
        mock_fetch_remote_service.return_value = service
        service_logs(['test_id', 'test_id2'])

        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)


class ServicePsTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()

        service1 = tutumcli.commands.tutum.Service()
        service1.current_num_containers = 3
        service1.name = 'SERVICE1'
        service1.uuid = '7A4CFE51-03BB-42D6-825E-3B533888D8CD'
        service1.image_name = 'test/service1'
        service1.web_public_dns = 'service1.io'
        service1.state = 'Running'
        service1.deployed_datetime = ''
        service1.synchronized = True
        service1.public_dns = "www.myhello1service.com"
        service2 = tutumcli.commands.tutum.Service()
        service2.current_num_containers = 2
        service2.name = 'SERVICE2'
        service2.uuid = '8B4CFE51-03BB-42D6-825E-3B533888D8CD'
        service2.image_name = 'test/service2'
        service2.web_public_dns = 'service2.io'
        service2.state = 'Stopped'
        service2.deployed_datetime = ''
        service2.synchronized = True
        service2.public_dns = "www.myhello2service.com"
        self.servicelist = [service1, service2]

    def tearDown(self):
        sys.stdout = self.stdout

    @mock.patch('tutumcli.commands.tutum.Service.list')
    def test_service_ps(self, mock_list):
        output = u'''NAME      UUID      STATUS       #CONTAINERS  IMAGE          DEPLOYED    PUBLIC DNS
SERVICE1  7A4CFE51  ▶ Running              3  test/service1              www.myhello1service.com
SERVICE2  8B4CFE51  ◼ Stopped              2  test/service2              www.myhello2service.com'''
        mock_list.return_value = self.servicelist
        service_ps(status='Running')

        mock_list.assert_called_with(state='Running')
        self.assertEqual(output, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('tutumcli.commands.tutum.Service.list')
    def test_service_ps_quiet(self, mock_list):
        output = '''7A4CFE51-03BB-42D6-825E-3B533888D8CD
8B4CFE51-03BB-42D6-825E-3B533888D8CD'''
        mock_list.return_value = self.servicelist
        service_ps(quiet=True)

        self.assertEqual(output, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('tutumcli.commands.sys.exit')
    @mock.patch('tutumcli.commands.tutum.Service.list', side_effect=TutumApiError)
    def test_service_ps_with_exception(self, mock_list, mock_exit):
        service_ps()

        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)

    @mock.patch('tutumcli.commands.tutum.Service.list')
    def test_service_ps_unsync(self, mock_list):
        output = u'''NAME      UUID      STATUS          #CONTAINERS  IMAGE          DEPLOYED    PUBLIC DNS
SERVICE1  7A4CFE51  ▶ Running(*)              3  test/service1              www.myhello1service.com
SERVICE2  8B4CFE51  ◼ Stopped                 2  test/service2              www.myhello2service.com

(*) Please note that this service needs to be redeployed to have its configuration changes applied'''
        self.servicelist[0].synchronized = False
        mock_list.return_value = self.servicelist
        service_ps(status='Running')

        mock_list.assert_called_with(state='Running')
        self.assertEqual(output, self.buf.getvalue().strip())
        self.buf.truncate(0)


class ServiceRunTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()

    def tearDown(self):
        sys.stdout = self.stdout

    @mock.patch('tutumcli.commands.tutum.Service.start')
    @mock.patch('tutumcli.commands.tutum.Service.save')
    @mock.patch('tutumcli.commands.tutum.Service.create')
    def test_service_run(self, mock_create, mock_save, mock_start):
        exposed_ports = [800, 222]
        published_ports = ['80:80/tcp', '22:22']
        ports = utils.parse_published_ports(published_ports)
        ports.extend(utils.parse_exposed_ports(exposed_ports))
        container_envvars = ['MYSQL_ADMIN=admin', 'MYSQL_PASS=password']
        linked_to_service = ['mysql:mysql', 'redis:redis']

        service = tutumcli.commands.tutum.Service()
        service.uuid = '7A4CFE51-03BB-42D6-825E-3B533888D8CD'
        mock_create.return_value = service
        mock_start.return_value = True
        service_run('imagename', 'containername', 1, '256M', True, 3, '-d', '/bin/mysql',
                    exposed_ports, published_ports, container_envvars, [], '', linked_to_service,
                    'OFF', 'OFF', 'OFF', 'poweruser', True, None, None, None)

        mock_create.assert_called_with(image='imagename', name='containername', cpu_shares=1,
                                       memory='256M', privileged=True,
                                       target_num_containers=3, run_command='-d',
                                       entrypoint='/bin/mysql', container_ports=ports,
                                       container_envvars=utils.parse_envvars(container_envvars, []),
                                       linked_to_service=utils.parse_links(linked_to_service, 'to_service'),
                                       autorestart='OFF', autodestroy='OFF', autoredeploy='OFF',
                                       roles='poweruser', sequential_deployment=True, tags=[], bindings=[],
                                       deployment_strategy=None)
        mock_save.assert_called()
        mock_start.assert_called()
        self.assertEqual(service.uuid, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('tutumcli.commands.tutum.Service.start')
    @mock.patch('tutumcli.commands.tutum.Service.save')
    @mock.patch('tutumcli.commands.tutum.Service.create')
    def test_service_run_exposing_publishing_same_port(self, mock_create, mock_save, mock_start):
        exposed_ports = [80]
        published_ports = ['800:80/tcp']
        ports = [{'inner_port': '80', 'outer_port': '800', 'protocol': 'tcp', 'published': True}]
        container_envvars = ['MYSQL_ADMIN=admin', 'MYSQL_PASS=password']
        linked_to_service = ['mysql:mysql', 'redis:redis']

        service = tutumcli.commands.tutum.Service()
        service.uuid = '7A4CFE51-03BB-42D6-825E-3B533888D8CD'
        mock_create.return_value = service
        mock_start.return_value = True
        service_run('imagename', 'containername', 1, '256M', True, 3, '-d', '/bin/mysql',
                    exposed_ports, published_ports, container_envvars, [], '', linked_to_service,
                    'OFF', 'OFF', 'OFF', 'poweruser', True, None, None, None)

        mock_create.assert_called_with(image='imagename', name='containername', cpu_shares=1,
                                       memory='256M', privileged=True,
                                       target_num_containers=3, run_command='-d',
                                       entrypoint='/bin/mysql', container_ports=ports,
                                       container_envvars=utils.parse_envvars(container_envvars, []),
                                       linked_to_service=utils.parse_links(linked_to_service, 'to_service'),
                                       autorestart='OFF', autodestroy='OFF', autoredeploy='OFF',
                                       roles='poweruser', sequential_deployment=True, tags=[], bindings=[],
                                       deployment_strategy=None)
        mock_save.assert_called()
        mock_start.assert_called()
        self.assertEqual(service.uuid, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('tutumcli.commands.sys.exit')
    @mock.patch('tutumcli.commands.tutum.Service.create', side_effect=TutumApiError)
    def test_service_run_with_exception(self, mock_create, mock_exit):
        exposed_ports = ['80', '22']
        published_ports = ['80:80/tcp', '22:22']
        container_envvars = ['MYSQL_ADMIN=admin', 'MYSQL_PASS=password']
        linked_to_service = ['mysql:mysql', 'redis:redis']
        service_run('imagename', 'containername', 1, '256M', True, 3, '-d', '/bin/mysql',
                    exposed_ports, published_ports, container_envvars, [], '', linked_to_service,
                    'OFF', 'OFF', 'OFF', 'poweruser', True, None, None, None)

        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)


class ServiceScaleTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()

    def tearDown(self):
        sys.stdout = self.stdout

    @mock.patch('tutumcli.commands.tutum.Service.save')
    @mock.patch('tutumcli.commands.utils.fetch_remote_service')
    def test_service_scale(self, mock_fetch_remote_service, mock_save):
        service = tutumcli.commands.tutum.Service()
        service.uuid = '7A4CFE51-03BB-42D6-825E-3B533888D8CD'
        mock_fetch_remote_service.return_value = service
        service_scale(['7A4CFE51-03BB-42D6-825E-3B533888D8CD'], 3)

        mock_save.assert_called()
        self.assertEqual(3, service.target_num_containers)
        self.assertEqual(service.uuid, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('tutumcli.commands.sys.exit')
    @mock.patch('tutumcli.commands.utils.fetch_remote_service', side_effect=TutumApiError)
    def test_service_scale_with_exception(self, mock_fetch_remote_service, mock_exit):
        service_scale(['test_id'], 3)

        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)


class ServiceSetTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()

    def tearDown(self):
        sys.stdout = self.stdout

    @mock.patch('tutumcli.commands.tutum.Service.save')
    @mock.patch('tutumcli.commands.utils.fetch_remote_service')
    def test_service_set(self, mock_fetch_remote_service, mock_save):
        service = tutumcli.commands.tutum.Service()
        exposed_ports = [80]
        published_ports = ['800:80/tcp']
        ports = [{'inner_port': '80', 'outer_port': '800', 'protocol': 'tcp', 'published': True}]
        container_envvars = ['MYSQL_ADMIN=admin', 'MYSQL_PASS=password']
        linked_to_service = ['mysql:mysql', 'redis:redis']
        service.uuid = '7A4CFE51-03BB-42D6-825E-3B533888D8CD'

        mock_fetch_remote_service.return_value = service
        service_set([service.uuid], 'imagename', 1, '256M', True, 3, '-d', '/bin/mysql',
                    exposed_ports, published_ports, container_envvars, [], '', linked_to_service,
                    'OFF', 'OFF', 'OFF', 'poweruser', True, False, None, None, None)

        mock_save.assert_called()
        self.assertEqual('7A4CFE51-03BB-42D6-825E-3B533888D8CD\n'
                         'Service must be redeployed to have its configuration changes applied.\n'
                         'To redeploy execute: $ tutum service redeploy 7A4CFE51-03BB-42D6-825E-3B533888D8CD',
                         self.buf.getvalue().strip())
        self.assertEqual(1, service.cpu_shares)
        self.assertEqual('256M', service.memory)
        self.assertEqual(True, service.privileged)
        self.assertEqual(3, service.target_num_containers)
        self.assertEqual('-d', service.run_command)
        self.assertEqual('/bin/mysql', service.entrypoint)
        self.assertEqual(ports, service.container_ports)
        self.assertEqual(utils.parse_envvars(container_envvars, []), service.container_envvars)
        self.assertEqual(utils.parse_links(linked_to_service, 'to_service'), service.linked_to_service)
        self.assertEqual('OFF', service.autorestart)
        self.assertEqual('OFF', service.autodestroy)
        self.assertEqual('OFF', service.autoredeploy)
        self.assertEqual('poweruser', service.roles)
        self.assertEqual(True, service.sequential_deployment)
        self.buf.truncate(0)

    @mock.patch('tutumcli.commands.sys.exit')
    @mock.patch('tutumcli.commands.utils.fetch_remote_service', side_effect=TutumApiError)
    def test_service_set_with_exception(self, mock_fetch_remote_service, mock_exit):
        service = tutumcli.commands.tutum.Service()
        exposed_ports = [80]
        published_ports = ['800:80/tcp']
        container_envvars = ['MYSQL_ADMIN=admin', 'MYSQL_PASS=password']
        linked_to_service = ['mysql:mysql', 'redis:redis']

        mock_fetch_remote_service.return_value = service
        service_set(['7A4CFE51-03BB-42D6-825E-3B533888D8CD'], 'imagename', 1, '256M', True, 3, '-d', '/bin/mysql',
                    exposed_ports, published_ports, container_envvars, [], '', linked_to_service,
                    'OFF', 'OFF', 'OFF', 'poweruser', True, False, None, None, None)

        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)


class ServiceStartTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()

    def tearDown(self):
        sys.stdout = self.stdout

    @mock.patch('tutumcli.commands.tutum.Service.start')
    @mock.patch('tutumcli.commands.utils.fetch_remote_service')
    def test_service_start(self, mock_fetch_remote_service, mock_start):
        service = tutumcli.commands.tutum.Service()
        service.uuid = '7A4CFE51-03BB-42D6-825E-3B533888D8CD'
        mock_fetch_remote_service.return_value = service
        mock_start.return_value = True
        service_start(['7A4CFE51-03BB-42D6-825E-3B533888D8CD'])

        self.assertEqual(service.uuid, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('tutumcli.commands.sys.exit')
    @mock.patch('tutumcli.commands.utils.fetch_remote_service', side_effect=TutumApiError)
    def test_service_start_with_exception(self, mock_fetch_remote_service, mock_exit):
        service_start(['7A4CFE51-03BB-42D6-825E-3B533888D8CD'])

        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)


class ServiceStopTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()

    def tearDown(self):
        sys.stdout = self.stdout

    @mock.patch('tutumcli.commands.tutum.Service.stop')
    @mock.patch('tutumcli.commands.utils.fetch_remote_service')
    def test_service_stop(self, mock_fetch_remote_service, mock_stop):
        service = tutumcli.commands.tutum.Service()
        service.uuid = '7A4CFE51-03BB-42D6-825E-3B533888D8CD'
        mock_fetch_remote_service.return_value = service
        mock_stop.return_value = True
        service_stop(['7A4CFE51-03BB-42D6-825E-3B533888D8CD'])

        self.assertEqual(service.uuid, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('tutumcli.commands.sys.exit')
    @mock.patch('tutumcli.commands.utils.fetch_remote_service', side_effect=TutumApiError)
    def test_service_stop_with_exception(self, mock_fetch_remote_service, mock_exit):
        service_start(['7A4CFE51-03BB-42D6-825E-3B533888D8CD'])

        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)


class ServiceTerminateTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()

    def tearDown(self):
        sys.stdout = self.stdout

    @mock.patch('tutumcli.commands.tutum.Service.delete')
    @mock.patch('tutumcli.commands.utils.fetch_remote_service')
    def test_service_teminate(self, mock_fetch_remote_service, mock_delete):
        service = tutumcli.commands.tutum.Service()
        service.uuid = '7A4CFE51-03BB-42D6-825E-3B533888D8CD'
        mock_fetch_remote_service.return_value = service
        mock_delete.return_value = True
        service_terminate(['7A4CFE51-03BB-42D6-825E-3B533888D8CD'])

        self.assertEqual(service.uuid, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('tutumcli.commands.sys.exit')
    @mock.patch('tutumcli.commands.utils.fetch_remote_service', side_effect=TutumApiError)
    def test_service_terminate_with_exception(self, mock_fetch_remote_service, mock_exit):
        service_terminate(['7A4CFE51-03BB-42D6-825E-3B533888D8CD'])

        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)


class ServiceRedeployTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()

    def tearDown(self):
        sys.stdout = self.stdout

    @mock.patch('tutumcli.commands.tutum.Service.redeploy')
    @mock.patch('tutumcli.commands.utils.fetch_remote_service')
    def test_service_teminate(self, mock_fetch_remote_service, mock_redeploy):
        service = tutumcli.commands.tutum.Service()
        service.uuid = '7A4CFE51-03BB-42D6-825E-3B533888D8CD'
        mock_fetch_remote_service.return_value = service
        mock_redeploy.return_value = True
        service_redeploy(['7A4CFE51-03BB-42D6-825E-3B533888D8CD'])

        self.assertEqual(service.uuid, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('tutumcli.commands.sys.exit')
    @mock.patch('tutumcli.commands.utils.fetch_remote_service', side_effect=TutumApiError)
    def test_service_terminate_with_exception(self, mock_fetch_remote_service, mock_exit):
        service_redeploy(['7A4CFE51-03BB-42D6-825E-3B533888D8CD'])

        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)


class ContainerInspectTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()

    def tearDown(self):
        sys.stdout = self.stdout

    @mock.patch('tutumcli.commands.tutum.Container.get_all_attributes')
    @mock.patch('tutumcli.commands.utils.fetch_remote_container')
    def test_container_inspect(self, mock_fetch_remote_container, mock_get_all_attributes):
        output = '''{
  "key": [
    {
      "name": "test",
      "id": "1"
    }
  ]
}'''
        uuid = '7A4CFE51-03BB-42D6-825E-3B533888D8CD'
        container = tutumcli.commands.tutum.Container()
        container.uuid = uuid
        mock_fetch_remote_container.return_value = container
        mock_get_all_attributes.return_value = {'key': [{'name': 'test', 'id': '1'}]}
        container_inspect(['test_id'])

        self.assertEqual(' '.join(output.split()), ' '.join(self.buf.getvalue().strip().split()))
        self.buf.truncate(0)

    @mock.patch('tutumcli.commands.sys.exit')
    @mock.patch('tutumcli.commands.utils.fetch_remote_container', side_effect=TutumApiError)
    def test_container_inspect_with_exception(self, mock_fetch_remote_container, mock_exit):
        container = tutumcli.commands.tutum.Container()
        mock_fetch_remote_container.return_value = container
        container_inspect(['test_id', 'test_id2'])

        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)


class ContainerLogsTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()

    def tearDown(self):
        sys.stdout = self.stdout

    @mock.patch('tutumcli.commands.utils.fetch_remote_container')
    def test_container_logs(self, mock_fetch_remote_container):
        log = 'Here is the log'
        container = tutumcli.commands.tutum.Container
        container.logs = log
        mock_fetch_remote_container.return_value = container
        container_logs(['test_id'])

        self.assertEqual(log, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('tutumcli.commands.sys.exit')
    @mock.patch('tutumcli.commands.utils.fetch_remote_container', side_effect=TutumApiError)
    def test_container_logs_with_exception(self, mock_fetch_remote_container, mock_exit):
        container = tutumcli.commands.tutum.Container()
        mock_fetch_remote_container.return_value = container
        container_logs(['test_id', 'test_id2'])

        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)


class ContainerPsTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()

        container1 = tutumcli.commands.tutum.Container()
        container1.name = 'CONTAINER1'
        container1.uuid = '7A4CFE51-03BB-42D6-825E-3B533888D8CD'
        container1.image_name = 'test/container1'
        container1.public_dns = 'container1.io'
        container1.state = 'Running'
        container1.deployed_datetime = ''
        container1.run_command = '/bin/bash'
        container1.container_ports = [{'protocol': 'tcp', 'inner_port': 8080, 'outer_port': 8080}]
        container1.exit_code = 1
        container2 = tutumcli.commands.tutum.Container()
        container2.name = 'CONTAINER2'
        container2.uuid = '8B4CFE51-03BB-42D6-825E-3B533888D8CD'
        container2.image_name = 'test/container2'
        container2.public_dns = 'container2.io'
        container2.state = 'Stopped'
        container2.deployed_datetime = ''
        container2.run_command = '/bin/sh'
        container2.container_ports = [{'protocol': 'tcp', 'inner_port': 3306, 'outer_port': 3307}]
        container2.exit_code = 0
        self.containerlist = [container1, container2]

    def tearDown(self):
        sys.stdout = self.stdout


    @mock.patch('tutumcli.commands.tutum.Container.list')
    def test_container_ps(self, mock_list):
        output = u'''NAME        UUID      STATUS     IMAGE            RUN COMMAND      EXIT CODE  DEPLOYED    PORTS
CONTAINER1  7A4CFE51  ▶ Running  test/container1  /bin/bash                1              container1.io:8080->8080/tcp
CONTAINER2  8B4CFE51  ◼ Stopped  test/container2  /bin/sh                  0              container2.io:3307->3306/tcp'''
        mock_list.return_value = self.containerlist
        container_ps(None, False, 'Running', None)

        mock_list.assert_called_with(state='Running')
        self.assertEqual(output, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('tutumcli.commands.tutum.Container.list')
    def test_container_ps_quiet(self, mock_list):
        output = '''7A4CFE51-03BB-42D6-825E-3B533888D8CD
8B4CFE51-03BB-42D6-825E-3B533888D8CD'''
        mock_list.return_value = self.containerlist
        container_ps(None, True, None, None)

        self.assertEqual(output, self.buf.getvalue().strip())
        self.buf.truncate(0)


    @mock.patch('tutumcli.commands.sys.exit')
    @mock.patch('tutumcli.commands.tutum.Container.list', side_effect=TutumApiError)
    def test_container_ps_with_exception(self, mock_list, mock_exit):
        container_ps(None, None, None, None)

        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)


class ContainerStartTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()

    def tearDown(self):
        sys.stdout = self.stdout

    @mock.patch('tutumcli.commands.tutum.Container.start')
    @mock.patch('tutumcli.commands.utils.fetch_remote_container')
    def test_container_start(self, mock_fetch_remote_container, mock_start):
        container = tutumcli.commands.tutum.Container()
        container.uuid = '7A4CFE51-03BB-42D6-825E-3B533888D8CD'
        mock_fetch_remote_container.return_value = container
        mock_start.return_value = True
        container_start(['7A4CFE51-03BB-42D6-825E-3B533888D8CD'])

        self.assertEqual(container.uuid, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('tutumcli.commands.sys.exit')
    @mock.patch('tutumcli.commands.utils.fetch_remote_container', side_effect=TutumApiError)
    def test_container_start_with_exception(self, mock_fetch_remote_container, mock_exit):
        container_start(['7A4CFE51-03BB-42D6-825E-3B533888D8CD'])

        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)


class ContainerStopTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()

    def tearDown(self):
        sys.stdout = self.stdout

    @mock.patch('tutumcli.commands.tutum.Container.stop')
    @mock.patch('tutumcli.commands.utils.fetch_remote_container')
    def test_container_stop(self, mock_fetch_remote_container, mock_stop):
        container = tutumcli.commands.tutum.Container()
        container.uuid = '7A4CFE51-03BB-42D6-825E-3B533888D8CD'
        mock_fetch_remote_container.return_value = container
        mock_stop.return_value = True
        container_stop(['7A4CFE51-03BB-42D6-825E-3B533888D8CD'])

        self.assertEqual(container.uuid, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('tutumcli.commands.sys.exit')
    @mock.patch('tutumcli.commands.utils.fetch_remote_container', side_effect=TutumApiError)
    def test_container_stop_with_exception(self, mock_fetch_remote_container, mock_exit):
        container_start(['7A4CFE51-03BB-42D6-825E-3B533888D8CD'])

        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)


class ContainerTerminateTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()

    def tearDown(self):
        sys.stdout = self.stdout

    @mock.patch('tutumcli.commands.tutum.Container.delete')
    @mock.patch('tutumcli.commands.utils.fetch_remote_container')
    def test_container_teminate(self, mock_fetch_remote_container, mock_delete):
        container = tutumcli.commands.tutum.Container()
        container.uuid = '7A4CFE51-03BB-42D6-825E-3B533888D8CD'
        mock_fetch_remote_container.return_value = container
        mock_delete.return_value = True
        container_terminate(['7A4CFE51-03BB-42D6-825E-3B533888D8CD'])

        self.assertEqual(container.uuid, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('tutumcli.commands.sys.exit')
    @mock.patch('tutumcli.commands.utils.fetch_remote_container', side_effect=TutumApiError)
    def test_container_terminate_with_exception(self, mock_fetch_remote_container, mock_exit):
        container_terminate(['7A4CFE51-03BB-42D6-825E-3B533888D8CD'])

        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)


class ImageListTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()

        image1 = tutumcli.commands.tutum.Image()
        image1.name = 'image_name_1'
        image1.description = 'image_desc_1'
        image2 = tutumcli.commands.tutum.Image()
        image2.name = 'image_name_2'
        image2.description = 'image_desc_2'
        self.imagelist = [image1, image2]

    def tearDown(self):
        sys.stdout = self.stdout

    @mock.patch('tutumcli.commands.tutum.Image.list')
    def test_image_list(self, mock_list):
        output = u'''NAME          DESCRIPTION
image_name_1  image_desc_1
image_name_2  image_desc_2'''
        mock_list.return_value = self.imagelist
        image_list()

        self.assertEqual(output, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('tutumcli.commands.tutum.Image.list')
    def test_image_list_quiet(self, mock_list):
        output = 'image_name_1\nimage_name_2'
        mock_list.return_value = self.imagelist
        image_list(quiet=True)

        self.assertEqual(output, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('tutumcli.commands.tutum.Image.list', return_value=[])
    def test_image_list_parameter(self, mock_list):
        image_list(jumpstarts=True)
        mock_list.assert_called_with(starred=True)

        image_list(linux=True)
        mock_list.assert_called_with(base_image=True)

    @mock.patch('tutumcli.commands.sys.exit')
    @mock.patch('tutumcli.commands.tutum.Image.list', side_effect=TutumApiError)
    def test_image_list_with_exception(self, mock_fetch_remote_container, mock_exit):
        image_list()

        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)


class ImageRegister(unittest.TestCase):
    def setUp(self):
        self.raw_input_holder = __builtin__.raw_input
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()


    def tearDown(self):
        sys.stdout = self.stdout
        __builtin__.raw_input = self.raw_input_holder

    @mock.patch('tutumcli.commands.tutum.Image.save', return_value=True)
    @mock.patch('tutumcli.commands.tutum.Image.create')
    @mock.patch('tutumcli.commands.getpass.getpass', return_value='password')
    def test_register(self, mock_get_pass, mock_create, mock_save):
        output = '''Please input username and password of the repository:
image_name'''
        __builtin__.raw_input = lambda _: 'username'  # set username
        image = tutumcli.commands.tutum.Image()
        image.name = 'image_name'
        mock_create.return_value = image
        image_register('repository', 'descripiton')

        self.assertEqual(output, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('tutumcli.commands.sys.exit')
    @mock.patch('tutumcli.commands.tutum.Image.create', side_effect=TutumApiError)
    @mock.patch('tutumcli.commands.getpass.getpass', return_value='password')
    def test_register_with_exception(self, mock_get_pass, mock_create, mock_exit):
        __builtin__.raw_input = lambda _: 'username'  # set username
        image_register('repository', 'descripiton')

        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)


class ImageRmTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()

    def tearDown(self):
        sys.stdout = self.stdout

    @mock.patch('tutumcli.commands.tutum.Image.delete', return_value=True)
    @mock.patch('tutumcli.commands.tutum.Image.fetch')
    def test_image_rm(self, mock_fetch, mock_delete):
        image_rm(['repo1', 'repo2'])

        self.assertEqual('repo1\nrepo2', self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('tutumcli.commands.sys.exit')
    @mock.patch('tutumcli.commands.tutum.Image.delete', return_value=True)
    @mock.patch('tutumcli.commands.tutum.Image.fetch')
    def test_image_rm_with_exception(self, mock_fetch, mock_delete, mock_exit):
        mock_fetch.side_effect = [tutumcli.commands.tutum.Image(), TutumApiError]
        image_rm(['repo1', 'repo2'])

        self.assertEqual('repo1', self.buf.getvalue().strip())
        self.buf.truncate(0)
        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)


class ImageSearchTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()

    def tearDown(self):
        sys.stdout = self.stdout

    @mock.patch.object(tutumcli.commands.utils.docker.Client, 'search')
    @mock.patch('tutumcli.utils.get_docker_client')
    def test_image_search(self, mock_get_docker_client, mock_search):
        mock_get_docker_client.return_value = docker.Client()
        mock_search.return_value = [
            {
                "description": "1st image",
                "is_official": True,
                "is_trusted": False,
                "name": "wma55/u1210sshd",
                "star_count": 0
            },
            {
                "description": "2nd image",
                "is_official": False,
                "is_trusted": True,
                "name": "jdswinbank/sshd",
                "star_count": 0
            },
            {
                "description": "3rd image",
                "is_official": True,
                "is_trusted": True,
                "name": "vgauthier/sshd",
                "star_count": 0
            }]
        output = u'''NAME             DESCRIPTION      STARS  OFFICIAL    TRUSTED
wma55/u1210sshd  1st image            0  ✓
jdswinbank/sshd  2nd image            0              ✓
vgauthier/sshd   3rd image            0  ✓           ✓'''
        image_search('keyword')
        self.assertEqual(output, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('tutumcli.commands.sys.exit')
    @mock.patch.object(tutumcli.commands.utils.docker.Client, 'search', side_effect=TutumApiError)
    @mock.patch('tutumcli.utils.get_docker_client')
    def test_image_search_with_exception(self, mock_get_docker_client, mock_search, mock_exit):
        mock_get_docker_client.return_value = docker.Client()
        image_search('keyword')

        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)


class ImageUpdateTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()

    def tearDown(self):
        sys.stdout = self.stdout

    @mock.patch('tutumcli.commands.tutum.Image.save', return_value=True)
    @mock.patch('tutumcli.commands.tutum.Image.fetch')
    def test_image_update(self, mock_fetch, mock_save):
        image = tutumcli.commands.tutum.Image()
        image.name = 'name'
        mock_fetch.return_value = image
        mock_save.return_value = True
        image_update(['repo'], 'username', 'password', 'description')
        self.assertEqual('username', image.username)
        self.assertEqual('password', image.password)
        self.assertEqual('description', image.description)
        self.assertEqual('name', self.buf.getvalue().strip())

    @mock.patch('tutumcli.commands.sys.exit')
    @mock.patch('tutumcli.commands.tutum.Image.fetch')
    def test_image_update_with_exception(self, mock_fetch, mock_exit):
        mock_fetch.side_effect = TutumApiError
        image_update(['repo'], 'username', 'password', 'description')

        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)


class NodeListTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()
        node1 = tutumcli.commands.tutum.Node()
        node1.uuid = '19303d01-3564-437b-ac54-e7f8d17003f6'
        node1.external_fqdn = '19303d01-tifayuki.node.tutum.io'
        node1.state = 'Deployed'
        node1.last_seen = None
        node1.node_cluster = '/api/v1/nodecluster/b0374cc2-4003-4270-b131-25fc494ea2be/'
        node2 = tutumcli.commands.tutum.Node()
        node2.uuid = 'bd276db4-cd35-4311-8110-1c82885c33d2'
        node2.external_fqdn = 'bd276db4-tifayuki.node.tutum.io"'
        node2.state = 'Deploying'
        node2.last_seen = None
        node2.node_cluster = '/api/v1/nodecluster/b0374cc2-4003-4270-b131-25fc494ea2be/'
        self.nodeklist = [node1, node2]

    def tearDown(self):
        sys.stdout = self.stdout

    @mock.patch('tutumcli.commands.tutum.NodeCluster.fetch')
    @mock.patch('tutumcli.commands.tutum.Node.list')
    def test_node_list(self, mock_list, mock_fetch):
        output = u'''UUID      FQDN                              LASTSEEN    STATUS       CLUSTER
19303d01  19303d01-tifayuki.node.tutum.io               ▶ Deployed   test_nodecluster
bd276db4  bd276db4-tifayuki.node.tutum.io"              ⚙ Deploying  test_nodecluster'''
        mock_list.return_value = self.nodeklist
        nodecluster = tutumcli.commands.tutum.NodeCluster()
        nodecluster.name = 'test_nodecluster'
        mock_fetch.return_value = nodecluster
        node_list(quiet=False)

        self.assertEqual(output, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('tutumcli.commands.tutum.NodeCluster.fetch')
    @mock.patch('tutumcli.commands.tutum.Node.list')
    def test_node_list(self, mock_list, mock_fetch):
        output = '''19303d01-3564-437b-ac54-e7f8d17003f6
bd276db4-cd35-4311-8110-1c82885c33d2'''
        mock_list.return_value = self.nodeklist
        nodecluster = tutumcli.commands.tutum.NodeCluster()
        nodecluster.name = 'test_nodecluster'
        mock_fetch.return_value = nodecluster
        node_list(quiet=True)

        self.assertEqual(output, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('tutumcli.commands.sys.exit')
    @mock.patch('tutumcli.commands.tutum.Node.list', side_effect=TutumApiError)
    def test_node_list(self, mock_list, mock_exit):
        node_list()

        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)


class NodeInspectTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()

    def tearDown(self):
        sys.stdout = self.stdout

    @mock.patch('tutumcli.commands.tutum.Node.get_all_attributes')
    @mock.patch('tutumcli.commands.tutum.Node.fetch')
    @mock.patch('tutumcli.commands.utils.fetch_remote_node')
    def test_node_inspect(self, mock_fetch_remote_node, mock_fetch, mock_get_all_attributes):
        output = '''{
  "key": [
    {
      "name": "test",
      "id": "1"
    }
  ]
}'''
        uuid = '7A4CFE51-03BB-42D6-825E-3B533888D8CD'
        node = tutumcli.commands.tutum.Node()
        node.uuid = uuid
        mock_fetch.return_value = node
        mock_fetch_remote_node.return_value = node
        mock_get_all_attributes.return_value = {'key': [{'name': 'test', 'id': '1'}]}
        node_inspect(['test_id'])

        mock_fetch.assert_called_with(uuid)
        self.assertEqual(' '.join(output.split()), ' '.join(self.buf.getvalue().strip().split()))
        self.buf.truncate(0)

    @mock.patch('tutumcli.commands.sys.exit')
    @mock.patch('tutumcli.commands.utils.fetch_remote_node', side_effect=TutumApiError)
    def test_node_inspect_with_exception(self, mock_fetch_remote_node, mock_exit):
        node = tutumcli.commands.tutum.Node()
        mock_fetch_remote_node.return_value = node
        node_inspect(['test_id', 'test_id2'])

        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)


class NodeRmTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()

    def tearDown(self):
        sys.stdout = self.stdout

    @mock.patch('tutumcli.commands.tutum.Node.delete')
    @mock.patch('tutumcli.commands.utils.fetch_remote_node')
    def test_node_teminate(self, mock_fetch_remote_node, mock_delete):
        node = tutumcli.commands.tutum.Node()
        node.uuid = '7A4CFE51-03BB-42D6-825E-3B533888D8CD'
        mock_fetch_remote_node.return_value = node
        mock_delete.return_value = True
        node_rm(['7A4CFE51-03BB-42D6-825E-3B533888D8CD'])

        self.assertEqual(node.uuid, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('tutumcli.commands.sys.exit')
    @mock.patch('tutumcli.commands.utils.fetch_remote_node', side_effect=TutumApiError)
    def test_node_terminate_with_exception(self, mock_fetch_remote_node, mock_exit):
        node_rm(['7A4CFE51-03BB-42D6-825E-3B533888D8CD'])

        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)


class NodeClusterListTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()
        nodecluster1 = tutumcli.commands.tutum.NodeCluster()
        nodecluster1.name = 'test_sfo'
        nodecluster1.uuid = 'b0374cc2-4003-4270-b131-25fc494ea2be'
        nodecluster1.region = '/api/v1/region/digitalocean/sfo1/'
        nodecluster1.node_type = '/api/v1/nodetype/digitalocean/512mb/'
        nodecluster1.deployed_datetime = None
        nodecluster1.state = 'Deployed'
        nodecluster1.current_num_nodes = 2
        nodecluster1.target_num_nodes = 2
        nodecluster2 = tutumcli.commands.tutum.NodeCluster()
        nodecluster2.name = 'newyork3'
        nodecluster2.uuid = 'a4c1e712-ca26-4547-adb7-8da1057b964b'
        nodecluster2.region = '/api/v1/region/digitalocean/nyc3/'
        nodecluster2.node_type = '/api/v1/nodetype/digitalocean/512mb/'
        nodecluster2.deployed_datetime = None
        nodecluster2.state = 'Provisioning'
        nodecluster2.current_num_nodes = 1
        nodecluster2.target_num_nodes = 1
        self.nodeclusterlist = [nodecluster1, nodecluster2]

        region1 = tutumcli.commands.tutum.Region()
        region1.label = 'New York 3'
        region2 = tutumcli.commands.tutum.Region()
        region2.label = 'San Francisco 1'
        self.regionlist = [region1, region2]

        nodetype1 = tutumcli.commands.tutum.NodeType()
        nodetype1.label = '512MB'
        nodetype2 = tutumcli.commands.tutum.NodeType()
        nodetype2.label = '512MB'
        self.nodetypelist = [nodetype1, nodetype2]


    def tearDown(self):
        sys.stdout = self.stdout

    @mock.patch('tutumcli.commands.tutum.Region.fetch')
    @mock.patch('tutumcli.commands.tutum.NodeType.fetch')
    @mock.patch('tutumcli.commands.tutum.NodeCluster.list')
    def test_clusternode_list(self, mock_list, mock_nodetype_fetch, mock_region_fetch):
        mock_list.return_value = self.nodeclusterlist
        mock_nodetype_fetch.side_effect = self.nodetypelist
        mock_region_fetch.side_effect = self.regionlist
        output = '''NAME      UUID      REGION           TYPE    DEPLOYED    STATUS          CURRENT#NODES    TARGET#NODES
test_sfo  b0374cc2  New York 3       512MB               Deployed                    2               2
newyork3  a4c1e712  San Francisco 1  512MB               Provisioning                1               1'''
        nodecluster_list(quiet=False)

        self.assertEqual(output, self.buf.getvalue().strip())
        self.buf.truncate(0)


    @mock.patch('tutumcli.commands.tutum.Region.fetch')
    @mock.patch('tutumcli.commands.tutum.NodeType.fetch')
    @mock.patch('tutumcli.commands.tutum.NodeCluster.list')
    def test_clusternode_list_quiet(self, mock_list, mock_nodetype_fetch, mock_region_fetch):
        mock_list.return_value = self.nodeclusterlist
        mock_nodetype_fetch.side_effect = self.nodetypelist
        mock_region_fetch.side_effect = self.regionlist
        output = 'b0374cc2-4003-4270-b131-25fc494ea2be\na4c1e712-ca26-4547-adb7-8da1057b964b'
        nodecluster_list(quiet=True)

        self.assertEqual(output, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('tutumcli.commands.sys.exit')
    @mock.patch('tutumcli.commands.tutum.NodeCluster.list', side_effect=TutumApiError)
    def test_clusternode_list_with_excepiton(self, mock_list, mock_exit):
        nodecluster_list(quiet=True)

        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)


class NodeClusterInspectTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()

    def tearDown(self):
        sys.stdout = self.stdout

    @mock.patch('tutumcli.commands.tutum.NodeCluster.get_all_attributes')
    @mock.patch('tutumcli.commands.tutum.NodeCluster.fetch')
    @mock.patch('tutumcli.commands.utils.fetch_remote_nodecluster')
    def test_nodecluster_inspect(self, mock_fetch_remote_node_cluster, mock_fetch, mock_get_all_attributes):
        output = '''{
  "key": [
    {
      "name": "test",
      "id": "1"
    }
  ]
}'''
        uuid = '7A4CFE51-03BB-42D6-825E-3B533888D8CD'
        nodecluster = tutumcli.commands.tutum.NodeCluster()
        nodecluster.uuid = uuid
        mock_fetch.return_value = nodecluster
        mock_fetch_remote_node_cluster.return_value = nodecluster
        mock_get_all_attributes.return_value = {'key': [{'name': 'test', 'id': '1'}]}
        nodecluster_inspect(['test_id'])

        mock_fetch.assert_called_with(uuid)
        self.assertEqual(' '.join(output.split()), ' '.join(self.buf.getvalue().strip().split()))
        self.buf.truncate(0)

    @mock.patch('tutumcli.commands.sys.exit')
    @mock.patch('tutumcli.commands.utils.fetch_remote_nodecluster', side_effect=TutumApiError)
    def test_nodecluster_inspect_with_exception(self, mock_fetch_remote_nodecluster, mock_exit):
        nodecluster = tutumcli.commands.tutum.NodeCluster()
        mock_fetch_remote_nodecluster.return_value = nodecluster
        nodecluster_inspect(['test_id', 'test_id2'])

        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)


class NodeClusterRmTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()

    def tearDown(self):
        sys.stdout = self.stdout

    @mock.patch('tutumcli.commands.tutum.NodeCluster.delete')
    @mock.patch('tutumcli.commands.utils.fetch_remote_nodecluster')
    def test_nodecluster_rm(self, mock_fetch_remote_nodecluster, mock_delete):
        nodecluster = tutumcli.commands.tutum.NodeCluster()
        nodecluster.uuid = '7A4CFE51-03BB-42D6-825E-3B533888D8CD'
        mock_fetch_remote_nodecluster.return_value = nodecluster
        mock_delete.return_value = True
        nodecluster_rm(['7A4CFE51-03BB-42D6-825E-3B533888D8CD'])

        self.assertEqual(nodecluster.uuid, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('tutumcli.commands.sys.exit')
    @mock.patch('tutumcli.commands.utils.fetch_remote_nodecluster', side_effect=TutumApiError)
    def test_nodecluster_rm_with_exception(self, mock_fetch_remote_nodecluster, mock_exit):
        nodecluster_rm(['7A4CFE51-03BB-42D6-825E-3B533888D8CD'])

        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)


class NodeClusterScaleTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()

    def tearDown(self):
        sys.stdout = self.stdout

    @mock.patch('tutumcli.commands.tutum.NodeCluster.save')
    @mock.patch('tutumcli.commands.utils.fetch_remote_nodecluster')
    def test_nodecluster_scale(self, mock_fetch_remote_nodecluster, mock_save):
        nodecluster = tutumcli.commands.tutum.NodeCluster()
        nodecluster.uuid = '7A4CFE51-03BB-42D6-825E-3B533888D8CD'
        mock_fetch_remote_nodecluster.return_value = nodecluster
        nodecluster_scale(['7A4CFE51-03BB-42D6-825E-3B533888D8CD'], 3)

        mock_save.assert_called()
        self.assertEqual(3, nodecluster.target_num_nodes)
        self.assertEqual(nodecluster.uuid, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('tutumcli.commands.sys.exit')
    @mock.patch('tutumcli.commands.utils.fetch_remote_nodecluster', side_effect=TutumApiError)
    def test_nodecluster_scale_with_exception(self, mock_fetch_remote_nodecluster, mock_exit):
        nodecluster_scale(['test_id'], 3)

        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)


class NodeClusterShowProviderTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()

        provider = tutumcli.commands.tutum.Provider()
        provider.name = 'digitalocean'
        provider.label = 'Digital Ocean'
        provider.regions = [
            "/api/v1/region/digitalocean/ams1/",
            "/api/v1/region/digitalocean/ams2/",
            "/api/v1/region/digitalocean/ams3/",
            "/api/v1/region/digitalocean/lon1/",
            "/api/v1/region/digitalocean/nyc1/",
            "/api/v1/region/digitalocean/nyc2/",
            "/api/v1/region/digitalocean/nyc3/",
            "/api/v1/region/digitalocean/sfo1/",
            "/api/v1/region/digitalocean/sgp1/"
        ]
        self.providerlist = [provider]

    def tearDown(self):
        sys.stdout = self.stdout

    @mock.patch('tutumcli.commands.tutum.Provider.list')
    def test_nodecluster_show_providers(self, mock_list):
        output = '''NAME          LABEL          REGIONS
digitalocean  Digital Ocean  ams1, ams2, ams3, lon1, nyc1, nyc2, nyc3, sfo1, sgp1'''
        mock_list.return_value = self.providerlist
        nodecluster_show_providers(quiet=False)

        self.assertEqual(output, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('tutumcli.commands.tutum.Provider.list')
    def test_nodecluster_show_providers_quiet(self, mock_list):
        output = 'digitalocean'
        mock_list.return_value = self.providerlist
        nodecluster_show_providers(quiet=True)

        self.assertEqual(output, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('tutumcli.commands.sys.exit')
    @mock.patch('tutumcli.commands.tutum.Provider.list', side_effect=TutumApiError)
    def test_nodecluster_show_providers_with_exception(self, mock_list, mock_exit):
        nodecluster_show_providers(quiet=True)

        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)


class NodeClusterShowRegionsTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()
        region1 = tutumcli.commands.tutum.Region()
        region1.name = 'ams1'
        region1.label = 'Amsterdam 1'
        region1.resource_uri = '/api/v1/region/digitalocean/ams1/'
        region1.node_types = ["/api/v1/nodetype/digitalocean/512mb/",
                              "/api/v1/nodetype/digitalocean/1gb/",
                              "/api/v1/nodetype/digitalocean/2gb/",
                              "/api/v1/nodetype/digitalocean/4gb/",
                              "/api/v1/nodetype/digitalocean/8gb/",
                              "/api/v1/nodetype/digitalocean/16gb/"]
        region2 = tutumcli.commands.tutum.Region()
        region2.name = 'sfo1'
        region2.label = 'San Francisco 1'
        region2.resource_uri = '/api/v1/region/digitalocean/sfo1/'
        region2.node_types = ["/api/v1/nodetype/digitalocean/512mb/",
                              "/api/v1/nodetype/digitalocean/1gb/",
                              "/api/v1/nodetype/digitalocean/2gb/",
                              "/api/v1/nodetype/digitalocean/4gb/",
                              "/api/v1/nodetype/digitalocean/8gb/",
                              "/api/v1/nodetype/digitalocean/16gb/",
                              "/api/v1/nodetype/digitalocean/32gb/",
                              "/api/v1/nodetype/digitalocean/48gb/",
                              "/api/v1/nodetype/digitalocean/64gb/"]
        region3 = tutumcli.commands.tutum.Region()
        region3.name = 'jap1'
        region3.label = 'Japan 1'
        region3.resource_uri = '/api/v1/region/aws/jap1/'
        region3.node_types = ["/api/v1/nodetype/aws/512mb/",
                              "/api/v1/nodetype/aws/1gb/",
                              "/api/v1/nodetype/aws/2gb/",
                              "/api/v1/nodetype/aws/4gb/",
                              "/api/v1/nodetype/aws/8gb/"]
        self.regionlist = [region1, region2, region3]

    def tearDown(self):
        sys.stdout = self.stdout

    @mock.patch('tutumcli.commands.tutum.Region.list')
    def test_nodecluster_show_regions(self, mock_list):
        output = '''NAME    LABEL            PROVIDER      TYPE
ams1    Amsterdam 1      digitalocean  512mb, 1gb, 2gb, 4gb, 8gb, 16gb
sfo1    San Francisco 1  digitalocean  512mb, 1gb, 2gb, 4gb, 8gb, 16gb, 32gb, 48gb, 64gb
jap1    Japan 1          aws           512mb, 1gb, 2gb, 4gb, 8gb'''
        mock_list.return_value = self.regionlist
        nodecluster_show_regions('')

        self.assertEqual(output, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('tutumcli.commands.tutum.Region.list')
    def test_nodecluster_show_regions_with_filter(self, mock_list):
        output = '''NAME    LABEL            PROVIDER      TYPE
ams1    Amsterdam 1      digitalocean  512mb, 1gb, 2gb, 4gb, 8gb, 16gb
sfo1    San Francisco 1  digitalocean  512mb, 1gb, 2gb, 4gb, 8gb, 16gb, 32gb, 48gb, 64gb'''
        mock_list.return_value = self.regionlist
        nodecluster_show_regions('digitalocean')

        self.assertEqual(output, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('tutumcli.commands.sys.exit')
    @mock.patch('tutumcli.commands.tutum.Region.list', side_effect=TutumApiError)
    def test_nodecluster_show_regions_with_exception(self, mock_list, mock_exit):
        nodecluster_show_regions('')

        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)


class NodeClusterShowTypesTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()
        nodetype1 = tutumcli.commands.tutum.NodeType()
        nodetype1.name = '512mb'
        nodetype1.label = '512MB'
        nodetype1.resource_uri = '/api/v1/nodetype/digitalocean/512mb/'
        nodetype1.regions = ["/api/v1/region/digitalocean/ams1/",
                             "/api/v1/region/digitalocean/sfo1/",
                             "/api/v1/region/digitalocean/nyc2/",
                             "/api/v1/region/digitalocean/ams2/",
                             "/api/v1/region/digitalocean/sgp1/",
                             "/api/v1/region/digitalocean/lon1/",
                             "/api/v1/region/digitalocean/nyc3/",
                             "/api/v1/region/digitalocean/nyc1/"]
        nodetype2 = tutumcli.commands.tutum.NodeType()
        nodetype2.name = '1gb'
        nodetype2.label = '1GB'
        nodetype2.resource_uri = '/api/v1/nodetype/digitalocean/1gb/'
        nodetype2.regions = ["/api/v1/region/digitalocean/ams1/",
                             "/api/v1/region/digitalocean/sfo1/",
                             "/api/v1/region/digitalocean/nyc2/",
                             "/api/v1/region/digitalocean/ams2/",
                             "/api/v1/region/digitalocean/sgp1/",
                             "/api/v1/region/digitalocean/lon1/",
                             "/api/v1/region/digitalocean/nyc3/",
                             "/api/v1/region/digitalocean/nyc1/"]
        nodetype3 = tutumcli.commands.tutum.NodeType()
        nodetype3.name = '3gb'
        nodetype3.label = '3GB'
        nodetype3.resource_uri = '/api/v1/region/aws/3gb/'
        nodetype3.regions = ["/api/v1/nodetype/aws/tokyo/",
                             "/api/v1/nodetype/aws/kyoto/",
                             "/api/v1/nodetype/aws/shibuya/",
                             "/api/v1/nodetype/aws/ueno/",
                             "/api/v1/nodetype/aws/akiba/"]
        self.nodetypelist = [nodetype1, nodetype2, nodetype3]

    def tearDown(self):
        sys.stdout = self.stdout

    @mock.patch('tutumcli.commands.tutum.NodeType.list')
    def test_nodecluster_show_types(self, mock_list):
        output = '''NAME    LABEL    PROVIDER      REGIONS
512mb   512MB    digitalocean  ams1, sfo1, nyc2, ams2, sgp1, lon1, nyc3, nyc1
1gb     1GB      digitalocean  ams1, sfo1, nyc2, ams2, sgp1, lon1, nyc3, nyc1
3gb     3GB      aws           tokyo, kyoto, shibuya, ueno, akiba'''
        mock_list.return_value = self.nodetypelist
        nodecluster_show_types('', '')

        self.assertEqual(output, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('tutumcli.commands.tutum.NodeType.list')
    def test_nodecluster_show_types_with_provider_filter(self, mock_list):
        output = '''NAME    LABEL    PROVIDER    REGIONS
3gb     3GB      aws         tokyo, kyoto, shibuya, ueno, akiba'''
        mock_list.return_value = self.nodetypelist
        nodecluster_show_types('aws', '')

        self.assertEqual(output, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('tutumcli.commands.tutum.NodeType.list')
    def test_nodecluster_show_types_with_region_filter(self, mock_list):
        output = '''NAME    LABEL    PROVIDER      REGIONS
512mb   512MB    digitalocean  ams1, sfo1, nyc2, ams2, sgp1, lon1, nyc3, nyc1
1gb     1GB      digitalocean  ams1, sfo1, nyc2, ams2, sgp1, lon1, nyc3, nyc1'''
        mock_list.return_value = self.nodetypelist
        nodecluster_show_types(output, 'nyc3')

    @mock.patch('tutumcli.commands.tutum.NodeType.list')
    def test_nodecluster_show_types_with_filters(self, mock_list):
        mock_list.return_value = self.nodetypelist
        nodecluster_show_types('aws', 'nyc3')

        self.assertEqual('NAME    LABEL    PROVIDER    REGIONS', self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('tutumcli.commands.sys.exit')
    @mock.patch('tutumcli.commands.tutum.NodeType.list', side_effect=TutumApiError)
    def test_nodecluster_show_types_with_exception(self, mock_list, mock_exit):
        nodecluster_show_types('', '')

        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)


class NodeClusterCreateTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()

    def tearDown(self):
        sys.stdout = self.stdout


    @mock.patch('tutumcli.commands.tutum.NodeCluster.deploy')
    @mock.patch('tutumcli.commands.tutum.NodeCluster.save')
    @mock.patch('tutumcli.commands.tutum.NodeCluster.create')
    def test_nodecluster_create(self, mock_create, mock_save, mock_deploy):
        provider_name = 'digitalocean'
        region_name = 'lon1'
        nodetype_name = '1gb'
        region_uri = "/api/v1/region/%s/%s/" % (provider_name, region_name)
        nodetype_uri = "/api/v1/nodetype/%s/%s/" % (provider_name, nodetype_name)
        nodecluster = tutumcli.commands.tutum.NodeCluster()
        nodecluster.uuid = '7A4CFE51-03BB-42D6-825E-3B533888D8CD'
        mock_create.return_value = nodecluster
        nodecluster_create(3, 'name', provider_name, region_name, nodetype_name)

        mock_create.assert_called_with(name='name', target_num_nodes=3, region=region_uri,
                                       node_type=nodetype_uri)
        self.assertEqual(nodecluster.uuid, self.buf.getvalue().strip())
        self.buf.truncate(0)


    @mock.patch('tutumcli.commands.sys.exit')
    @mock.patch('tutumcli.commands.tutum.NodeCluster.create', side_effect=TutumApiError)
    def test_nodecluster_create_with_exception(self, mock_create, mock_exit):
        nodecluster_create(3, 'name', 'provider', 'region', 'nodetype')

        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)
