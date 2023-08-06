# -*- coding: utf-8 -*-
import unittest
import __builtin__

import mock
from tutum.api.exceptions import *

import tutumcli
from tutumcli.utils import *
from tutumcli.exceptions import *


class TabulateResultTestCase(unittest.TestCase):
    @mock.patch('tutumcli.utils.tabulate')
    def test_tabulate_result(self, mock_tabulate):
        data_list = None
        headers = None
        tabulate_result(data_list, headers)
        mock_tabulate.assert_called_with(data_list, headers, stralign="left", tablefmt="plain")


class DateTimeConversionTestCase(unittest.TestCase):
    def test_from_utc_string_to_utc_datetime(self):
        # test None
        self.assertIsNone(from_utc_string_to_utc_datetime(None))

        # test mal-formatted string
        self.assertRaises(Exception, from_utc_string_to_utc_datetime, 'abc')

        # test normal case
        utc_datetime = from_utc_string_to_utc_datetime('Sun, 6 Apr 2014 18:11:17 +0000')
        self.assertEqual(str(utc_datetime), '2014-04-06 18:11:17')

    def test_get_humanize_local_datetime_from_utc_datetime_string(self):
        # test None
        self.assertEqual(get_humanize_local_datetime_from_utc_datetime_string(None), '')

        # test mal-formatted string
        self.assertRaises(Exception, get_humanize_local_datetime_from_utc_datetime_string, 'abc')

        # test normal case
        utc_datetime = get_humanize_local_datetime_from_utc_datetime_string('Sun, 6 Apr 2014 18:11:17 +0000')
        self.assertRegexpMatches(utc_datetime, r".* ago")

        # test future
        utc_datetime = get_humanize_local_datetime_from_utc_datetime_string('Sun, 6 Apr 3014 18:11:17 +0000')
        self.assertNotRegexpMatches(utc_datetime, r".* ago")


class IsUuidTestCase(unittest.TestCase):
    def test_is_uuid4(self):
        self.assertTrue(is_uuid4('7a4cfe51-038b-42d6-825e-3b533888d8cd'))
        self.assertTrue(is_uuid4('7A4CFE51-03BB-42D6-825E-3B533888D8CD'))

        self.assertFalse(is_uuid4('not_uuid'))
        self.assertFalse(is_uuid4(''))
        self.assertRaises(Exception, is_uuid4, None)
        self.assertRaises(Exception, is_uuid4, 12345)


class AddUnicodeSymbolToStateTestCase(unittest.TestCase):
    def test_add_unicode_symbol_to_state(self):
        for state in ['Running', 'Partly running']:
            self.assertEqual(' '.join([u'▶', state]), add_unicode_symbol_to_state(state))
        for state in ['Init', 'Stopped']:
            self.assertEqual(' '.join([u'◼', state]), add_unicode_symbol_to_state(state))
        for state in ['Starting', 'Stopping', 'Scaling', 'Terminating']:
            self.assertEqual(' '.join([u'⚙', state]), add_unicode_symbol_to_state(state))
        for state in ['Start failed', 'Stopped with errors']:
            self.assertEqual(' '.join([u'!', state]), add_unicode_symbol_to_state(state))
        for state in ['Terminated']:
            self.assertEqual(' '.join([u'✘', state]), add_unicode_symbol_to_state(state))


class GetDockerClientTestCase(unittest.TestCase):
    @mock.patch('tutumcli.utils.os.getenv')
    def test_get_docker_client_exception(self, mock_getenv):
        mock_getenv.return_value = '/run/mock.docker.sock'
        self.assertRaises(DockerNotFound, get_docker_client)


class FetchRemoteObjectTestCase(unittest.TestCase):
    @mock.patch('tutumcli.utils.tutum.Container.list')
    @mock.patch('tutumcli.utils.tutum.Container.fetch')
    def test_fetch_remote_container(self, mock_fetch, mock_list):
        # test container exist queried with uuid4
        mock_fetch.return_value = 'returned'
        self.assertEqual(fetch_remote_container('7A4CFE51-03BB-42D6-825E-3B533888D8CD', True), 'returned')
        self.assertEqual(fetch_remote_container('7A4CFE51-03BB-42D6-825E-3B533888D8CD', False), 'returned')

        # test container doesn't exist queried with uuid4
        mock_fetch.side_effect = ObjectNotFound
        self.assertRaises(ObjectNotFound, fetch_remote_container, '7A4CFE51-03BB-42D6-825E-3B533888D8CD', True)
        self.assertIsInstance(fetch_remote_container('7A4CFE51-03BB-42D6-825E-3B533888D8CD', False), ObjectNotFound)

        # test unique container found queried with short uuid
        container = tutum.Container.create()
        container.uuid = 'uuid'
        mock_list.side_effect = [[container], []]
        mock_fetch.side_effect = [container]
        self.assertEquals(fetch_remote_container('shortuuid', True), container)
        mock_list.side_effect = [[container], []]
        mock_fetch.side_effect = [container]
        self.assertEquals(fetch_remote_container('shortuuid', False), container)

        # test unique container found queried with name
        mock_list.side_effect = [[], [container]]
        mock_fetch.side_effect = [container]
        self.assertEquals(fetch_remote_container('name', True), container)
        mock_list.side_effect = [[], [container]]
        mock_fetch.side_effect = [container]
        self.assertEquals(fetch_remote_container('name', False), container)

        # test no container found
        mock_list.side_effect = [[], []]
        self.assertRaises(ObjectNotFound, fetch_remote_container, 'uuid_or_name', True)
        mock_list.side_effect = [[], []]
        self.assertIsInstance(fetch_remote_container('uuid_or_name', False), ObjectNotFound)

        # test multi-container found
        mock_list.side_effect = [['container1', 'container2'], []]
        self.assertRaises(NonUniqueIdentifier, fetch_remote_container, 'uuid_or_name', True)
        mock_list.side_effect = [['container1', 'container2'], []]
        self.assertIsInstance(fetch_remote_container('uuid_or_name', False), NonUniqueIdentifier)
        mock_list.side_effect = [[], ['container1', 'container2']]
        self.assertRaises(NonUniqueIdentifier, fetch_remote_container, 'uuid_or_name', True)
        mock_list.side_effect = [[], ['container1', 'container2']]
        self.assertIsInstance(fetch_remote_container('uuid_or_name', False), NonUniqueIdentifier)

        # test api error
        mock_list.side_effect = [TutumApiError, TutumApiError]
        self.assertRaises(TutumApiError, fetch_remote_container, 'uuid_or_name', True)
        self.assertRaises(TutumApiError, fetch_remote_container, 'uuid_or_name', False)

    @mock.patch('tutumcli.utils.tutum.Service.list')
    @mock.patch('tutumcli.utils.tutum.Service.fetch')
    def test_fetch_remote_service(self, mock_fetch, mock_list):
        # test cluster exist queried with uuid4
        mock_fetch.return_value = 'returned'
        self.assertEqual(fetch_remote_service('7A4CFE51-03BB-42D6-825E-3B533888D8CD', True), 'returned')
        self.assertEqual(fetch_remote_service('7A4CFE51-03BB-42D6-825E-3B533888D8CD', False), 'returned')

        # test cluster doesn't exist queried with uuid4
        mock_fetch.side_effect = ObjectNotFound
        self.assertRaises(ObjectNotFound, fetch_remote_service, '7A4CFE51-03BB-42D6-825E-3B533888D8CD', True)
        self.assertIsInstance(fetch_remote_service('7A4CFE51-03BB-42D6-825E-3B533888D8CD', False), ObjectNotFound)

        # test unique cluster found queried with short uuid
        service = tutum.Service.create()
        service.uuid = 'uuid'
        mock_list.side_effect = [[service], []]
        mock_fetch.side_effect = [service]
        self.assertEquals(fetch_remote_service('shortuuid', True), service)
        mock_list.side_effect = [[service], []]
        mock_fetch.side_effect = [service]
        self.assertEquals(fetch_remote_service('shortuuid', False), service)

        # test unique cluster found queried with name
        mock_list.side_effect = [[], [service]]
        mock_fetch.side_effect = [service]
        self.assertEquals(fetch_remote_service('name', True), service)
        mock_list.side_effect = [[], [service]]
        mock_fetch.side_effect = [service]
        self.assertEquals(fetch_remote_service('name', False), service)

        # test no cluster found
        mock_list.side_effect = [[], []]
        self.assertRaises(ObjectNotFound, fetch_remote_service, 'uuid_or_name', True)
        mock_list.side_effect = [[], []]
        self.assertIsInstance(fetch_remote_service('uuid_or_name', False), ObjectNotFound)

        # test multi-cluster found
        mock_list.side_effect = [['cluster1', 'cluster2'], []]
        self.assertRaises(NonUniqueIdentifier, fetch_remote_service, 'uuid_or_name', True)
        mock_list.side_effect = [['cluster1', 'cluster2'], []]
        self.assertIsInstance(fetch_remote_service('uuid_or_name', False), NonUniqueIdentifier)
        mock_list.side_effect = [[], ['cluster1', 'cluster2']]
        self.assertRaises(NonUniqueIdentifier, fetch_remote_service, 'uuid_or_name', True)
        mock_list.side_effect = [[], ['cluster1', 'cluster2']]
        self.assertIsInstance(fetch_remote_service('uuid_or_name', False), NonUniqueIdentifier)

        # test api error
        mock_list.side_effect = [TutumApiError, TutumApiError]
        self.assertRaises(TutumApiError, fetch_remote_service, 'uuid_or_name', True)
        self.assertRaises(TutumApiError, fetch_remote_service, 'uuid_or_name', False)

    @mock.patch('tutumcli.utils.tutum.Node.list')
    @mock.patch('tutumcli.utils.tutum.Node.fetch')
    def test_fetch_remote_node(self, mock_fetch, mock_list):
        # test node exist queried with uuid4
        mock_fetch.return_value = 'returned'
        self.assertEqual(fetch_remote_node('7A4CFE51-03BB-42D6-825E-3B533888D8CD', True), 'returned')
        self.assertEqual(fetch_remote_node('7A4CFE51-03BB-42D6-825E-3B533888D8CD', False), 'returned')

        # test node doesn't exist queried with uuid4
        mock_fetch.side_effect = ObjectNotFound
        self.assertRaises(ObjectNotFound, fetch_remote_node, '7A4CFE51-03BB-42D6-825E-3B533888D8CD', True)
        self.assertIsInstance(fetch_remote_node('7A4CFE51-03BB-42D6-825E-3B533888D8CD', False), ObjectNotFound)


        # test unique node found queried with short uuid
        node = tutum.Node.create()
        node.uuid = 'uuid'
        mock_list.side_effect = [[node]]
        mock_fetch.side_effect = [node]
        self.assertEquals(fetch_remote_node('uuid', True), node)
        mock_list.side_effect = [[node]]
        mock_fetch.side_effect = [node]
        self.assertEquals(fetch_remote_node('uuid', False), node)

        # test no node found
        mock_list.side_effect = [[]]
        self.assertRaises(ObjectNotFound, fetch_remote_node, 'uuid', True)
        mock_list.side_effect = [[]]
        self.assertIsInstance(fetch_remote_node('uuid', False), ObjectNotFound)

        # test multi-node found
        mock_list.side_effect = [['node1', 'node2']]
        self.assertRaises(NonUniqueIdentifier, fetch_remote_node, 'uuid', True)
        mock_list.side_effect = [['node1', 'node2']]
        self.assertIsInstance(fetch_remote_node('uuid', False), NonUniqueIdentifier)

        # test api error
        mock_list.side_effect = [TutumApiError, TutumApiError]
        self.assertRaises(TutumApiError, fetch_remote_node, 'uuid', True)
        self.assertRaises(TutumApiError, fetch_remote_node, 'uuid', False)

    @mock.patch('tutumcli.utils.tutum.NodeCluster.list')
    @mock.patch('tutumcli.utils.tutum.NodeCluster.fetch')
    def test_fetch_remote_nodecluster(self, mock_fetch, mock_list):
        # test nodecluster exist queried with uuid4
        mock_fetch.return_value = 'returned'
        self.assertEqual(fetch_remote_nodecluster('7A4CFE51-03BB-42D6-825E-3B533888D8CD', True), 'returned')
        self.assertEqual(fetch_remote_nodecluster('7A4CFE51-03BB-42D6-825E-3B533888D8CD', False), 'returned')

        # test nodecluster doesn't exist queried with uuid4
        mock_fetch.side_effect = ObjectNotFound
        self.assertRaises(ObjectNotFound, fetch_remote_nodecluster, '7A4CFE51-03BB-42D6-825E-3B533888D8CD', True)
        self.assertIsInstance(fetch_remote_nodecluster('7A4CFE51-03BB-42D6-825E-3B533888D8CD', False), ObjectNotFound)

        # test unique nodecluster found queried with short uuid
        nodecluster = tutum.NodeCluster.create()
        nodecluster.uuid = 'uuid'
        mock_list.side_effect = [[nodecluster], []]
        mock_fetch.side_effect = [nodecluster]
        self.assertEquals(fetch_remote_nodecluster('shortuuid', True), nodecluster)
        mock_list.side_effect = [[nodecluster], []]
        mock_fetch.side_effect = [nodecluster]
        self.assertEquals(fetch_remote_nodecluster('shortuuid', False), nodecluster)

        # test unique nodecluster found queried with name
        mock_list.side_effect = [[], [nodecluster]]
        mock_fetch.side_effect = [nodecluster]
        self.assertEquals(fetch_remote_nodecluster('name', True), nodecluster)
        mock_list.side_effect = [[], [nodecluster]]
        mock_fetch.side_effect = [nodecluster]
        self.assertEquals(fetch_remote_nodecluster('name', False), nodecluster)

        # test no nodecluster found
        mock_list.side_effect = [[], []]
        self.assertRaises(ObjectNotFound, fetch_remote_nodecluster, 'uuid_or_name', True)
        mock_list.side_effect = [[], []]
        self.assertIsInstance(fetch_remote_nodecluster('uuid_or_name', False), ObjectNotFound)

        # test multi-nodecluster found
        mock_list.side_effect = [['nodecluster1', 'nodecluster2'], []]
        self.assertRaises(NonUniqueIdentifier, fetch_remote_nodecluster, 'uuid_or_name', True)
        mock_list.side_effect = [['nodecluster1', 'nodecluster2'], []]
        self.assertIsInstance(fetch_remote_nodecluster('uuid_or_name', False), NonUniqueIdentifier)
        mock_list.side_effect = [[], ['nodecluster1', 'nodecluster2']]
        self.assertRaises(NonUniqueIdentifier, fetch_remote_nodecluster, 'uuid_or_name', True)
        mock_list.side_effect = [[], ['nodecluster1', 'nodecluster2']]
        self.assertIsInstance(fetch_remote_nodecluster('uuid_or_name', False), NonUniqueIdentifier)

        # test api error
        mock_list.side_effect = [TutumApiError, TutumApiError]
        self.assertRaises(TutumApiError, fetch_remote_nodecluster, 'uuid_or_name', True)
        self.assertRaises(TutumApiError, fetch_remote_nodecluster, 'uuid_or_name', False)


class ParseLinksTestCase(unittest.TestCase):
    def test_parse_links(self):
        output = [{'to_service': 'mysql', 'name': 'db1'}, {'to_service': 'mariadb', 'name': 'db2'}]
        self.assertEqual(output, parse_links(['mysql:db1', 'mariadb:db2'], 'to_service'))

    def test_parse_links_bad_format(self):
        self.assertRaises(BadParameter, parse_links, ['mysql', 'mariadb'], 'to_service')
        self.assertRaises(BadParameter, parse_links, ['mysql:mysql:mysql', 'mariadb:maria:maria'], 'to_service')
        self.assertRaises(BadParameter, parse_links, [''], 'to_service')


class ParsePublishedPortsTestCase(unittest.TestCase):
    def test_parse_published_ports(self):
        output = [{'protocol': 'tcp', 'inner_port': '80', 'published': True},
                  {'protocol': 'udp', 'inner_port': '53', 'published': True},
                  {'protocol': 'tcp', 'inner_port': '3306', 'outer_port': '3307', 'published': True},
                  {'protocol': 'udp', 'inner_port': '8080', 'outer_port': '8083', 'published': True}]
        self.assertEqual(output, parse_published_ports(['80', '53/udp', '3307:3306', '8083:8080/udp']))

    def test_parse_published_ports_bad_format(self):
        self.assertRaises(BadParameter, parse_published_ports, ['abc'])
        self.assertRaises(BadParameter, parse_published_ports, ['abc:80'])
        self.assertRaises(BadParameter, parse_published_ports, ['80:abc'])
        self.assertRaises(BadParameter, parse_published_ports, ['80:80:abc'])
        self.assertRaises(BadParameter, parse_published_ports, ['80:80/abc'])
        self.assertRaises(BadParameter, parse_published_ports, ['80/80:tcp'])
        self.assertRaises(BadParameter, parse_published_ports, [''])


class ParseExposedPortsTestCase(unittest.TestCase):
    def test_parse_exposed_ports(self):
        output = [{'protocol': 'tcp', 'inner_port': '80', 'published': False},
                  {'protocol': 'tcp', 'inner_port': '8080', 'published': False}]
        self.assertEqual(output, parse_exposed_ports([80, 8080]))

    def test_parse_exposed_ports_bad_format(self):
        self.assertRaises(BadParameter, parse_exposed_ports, ['abc'])
        self.assertRaises(BadParameter, parse_exposed_ports, ['abc'])
        self.assertRaises(BadParameter, parse_exposed_ports, ['-1'])
        self.assertRaises(BadParameter, parse_exposed_ports, ['999999'])


class ParseEnvironmentVariablesTestCase(unittest.TestCase):
    def test_parse_envvars(self):
        output = [{'key': 'MYSQL_PASS', 'value': 'mypass'}, {'key': 'MYSQL_USER', 'value': 'admin'}]
        self.assertEqual(output, parse_envvars(['MYSQL_USER=admin', 'MYSQL_PASS=mypass'], []))


class TryRegisterTestCase(unittest.TestCase):
    def setUp(self):
        self.raw_input_holder = __builtin__.raw_input

    def tearDown(self):
        __builtin__.raw_input = self.raw_input_holder


    @mock.patch('tutumcli.utils.requests.post')
    def test_try_register_success(self, mock_post):
        username = 'test_username'
        password = 'test_password'
        __builtin__.raw_input = lambda _: 'test@email.com'  # set email
        response = mock.MagicMock()
        response.status_code = 201
        mock_post.return_value = response
        url = urlparse.urljoin(tutum.base_url, "register/")
        headers = {'Content-Type': "application/json", "User-Agent": "tutum/%s" % tutumcli.__version__}
        data = json.dumps({'username': 'test_username', "password1": 'test_password', "password2": 'test_password',
                           "email": 'test@email.com'})

        ret, text = try_register(username, password)
        mock_post.assert_called_with(url, headers=headers, data=data)
        self.assertEqual((True, ('Account created. Please check your email for activation instructions.')), (ret, text))

    @mock.patch('tutumcli.utils.requests.post')
    def test_try_register_too_many_retries(self, mock_post):
        username = 'test_username'
        password = 'test_password'
        __builtin__.raw_input = lambda _: 'test@email.com'  # set email
        response = mock.MagicMock()
        response.status_code = 429
        mock_post.return_value = response
        ret, text = try_register(username, password)
        self.assertEqual((False, "Too many retries. Please login again later."), (ret, text))

    @mock.patch('tutumcli.utils.requests.post')
    def test_try_register_failed(self, mock_post):
        username = 'test_username'
        password = 'test_password'
        __builtin__.raw_input = lambda _: 'test@email.com'  # set email
        response = mock.Mock()
        response.status_code = 400
        response.json.return_value = {u'register': {u'username': [u'A user with that username already exists.'],
                                                    u'email': [
                                                        u'This email address is already in use. Please supply a different email address.']}}
        mock_post.return_value = response

        ret, text = try_register(username, password)
        self.assertEqual((False,
                          u'username: A user with that username already exists.\nemail: This email address is already in use. Please supply a different email address.'),
                         (ret, text))
