import unittest
import copy
import StringIO
import sys

import mock

from tutumcli.tutum_cli import patch_help_option, dispatch_cmds, initialize_parser
from tutumcli.exceptions import InternalError
import tutumcli


class PatchHelpOptionTestCase(unittest.TestCase):
    def setUp(self):
        self.add_help_argv_list = [
            ['tutum'],
            ['tutum', 'service'],
            ['tutum', 'service', 'create'],
            ['tutum', 'service', 'inspect'],
            ['tutum', 'service', 'logs'],
            ['tutum', 'service', 'redeploy'],
            ['tutum', 'service', 'run'],
            ['tutum', 'service', 'scale'],
            ['tutum', 'service', 'set'],
            ['tutum', 'service', 'start'],
            ['tutum', 'service', 'stop'],
            ['tutum', 'service', 'terminate'],
            ['tutum', 'build'],
            ['tutum', 'container'],
            ['tutum', 'container', 'inspect'],
            ['tutum', 'container', 'logs'],
            ['tutum', 'container', 'start'],
            ['tutum', 'container', 'stop'],
            ['tutum', 'container', 'terminate'],
            ['tutum', 'image'],
            ['tutum', 'image', 'register'],
            ['tutum', 'image', 'push'],
            ['tutum', 'image', 'rm'],
            ['tutum', 'image', 'search'],
            ['tutum', 'image', 'update'],
            ['tutum', 'node'],
            ['tutum', 'node', 'inspect'],
            ['tutum', 'node', 'rm'],
            ['tutum', 'node', 'upgrade'],
            ['tutum', 'nodecluster'],
            ['tutum', 'nodecluster', 'create'],
            ['tutum', 'nodecluster', 'inspect'],
            ['tutum', 'nodecluster', 'rm'],
            ['tutum', 'nodecluster', 'scale'],
            ['tutum', 'tag', 'add'],
            ['tutum', 'tag', 'list'],
            ['tutum', 'tag', 'rm'],
            ['tutum', 'tag', 'set'],
        ]
        self.not_add_help_argv_list = [
            ["tutum", "service", "ps"],
            ["tutum", "container", "ps"],
            ["tutum", "image", "list"],
            ["tutum", "node", "list"],
            ["tutum", "nodecluster", "list"],
            ["tutum", "nodecluster", "provider"],
            ["tutum", "nodecluster", "region"],
            ['tutum', 'nodecluster', 'nodetype'],
            ["tutum", "container", "run", "-p", "80:80", "tutum/wordpress"],
        ]

    def test_parser_with_empty_args(self):
        args = []
        self.assertRaises(InternalError, patch_help_option, args)

    def test_help_append(self):
        for argv in self.add_help_argv_list:
            args = patch_help_option(argv)
            target = copy.copy(argv[1:])
            target.append('-h')
            self.assertEqual(target, args, "Help option not patch correctly: %s" % argv)

    def test_help_not_append(self):
        for argv in self.not_add_help_argv_list:
            args = patch_help_option(argv)
            self.assertEqual(argv[1:], args, "Should not patch help option correctly: %s" % argv)

    def test_help_append_with_debug_option(self):
        argvlist = copy.copy(self.add_help_argv_list)
        for argv in argvlist:
            argv.insert(1, "--debug")
            args = patch_help_option(argv)
            target = copy.copy(argv[1:])
            target.append('-h')
            self.assertEqual(target, args, "Help option not patch correctly: %s" % argv)

    def test_help_not_append_with_debug_option(self):
        argvlist = copy.copy(self.not_add_help_argv_list)
        for argv in argvlist:
            argv.insert(1, "--debug")
            args = patch_help_option(argv)
            self.assertEqual(argv[1:], args, "Should not patch help option correctly: %s" % argv)


class CommandsDispatchTestCase(unittest.TestCase):
    def setUp(self):
        self.parser = tutumcli.tutum_cli.initialize_parser()

    @mock.patch('tutumcli.tutum_cli.commands')
    def test_login_dispatch(self, mock_cmds):
        args = self.parser.parse_args(['login'])
        dispatch_cmds(args)
        mock_cmds.login.assert_called_with()

    @mock.patch('tutumcli.tutum_cli.commands')
    def test_build_dispatch(self, mock_cmds):
        args = self.parser.parse_args(['build', '-t', 'mysql', '.'])
        dispatch_cmds(args)
        mock_cmds.build.assert_called_with(args.tag, args.directory)

    @mock.patch('tutumcli.tutum_cli.commands')
    def test_service_dispatch(self, mock_cmds):
        args = self.parser.parse_args(['service', 'create', 'mysql'])
        dispatch_cmds(args)
        mock_cmds.service_create.assert_called_with(image=args.image, name=args.name, cpu_shares=args.cpushares,
                                                    memory=args.memory,
                                                    target_num_containers=args.target_num_containers,
                                                    privileged=args.privileged,
                                                    run_command=args.run_command,
                                                    entrypoint=args.entrypoint, expose=args.expose,
                                                    publish=args.publish,
                                                    envvars=args.env, envfiles=args.env_file, tag=args.tag,
                                                    linked_to_service=args.link_service,
                                                    autorestart=args.autorestart, autodestroy=args.autodestroy,
                                                    autoredeploy=args.autoredeploy, roles=args.role,
                                                    sequential=args.sequential,
                                                    volume=args.volume, volumes_from=args.volumes_from,
                                                    deployment_strategy=args.deployment_strategy)

        args = self.parser.parse_args(['service', 'inspect', 'id'])
        dispatch_cmds(args)
        mock_cmds.service_inspect.assert_called_with(args.identifier)

        args = self.parser.parse_args(['service', 'logs', 'id'])
        dispatch_cmds(args)
        mock_cmds.service_logs.assert_called_with(args.identifier)

        args = self.parser.parse_args(['service', 'ps'])
        dispatch_cmds(args)
        mock_cmds.service_ps.assert_called_with(args.quiet, args.status)

        args = self.parser.parse_args(['service', 'redeploy', 'mysql'])
        dispatch_cmds(args)
        mock_cmds.service_redeploy.assert_called_with(args.identifier)

        args = self.parser.parse_args(['service', 'run', 'mysql'])
        dispatch_cmds(args)
        mock_cmds.service_run.assert_called_with(image=args.image, name=args.name, cpu_shares=args.cpushares,
                                                 memory=args.memory, target_num_containers=args.target_num_containers,
                                                 privileged=args.privileged,
                                                 run_command=args.run_command,
                                                 entrypoint=args.entrypoint, expose=args.expose, publish=args.publish,
                                                 envvars=args.env, envfiles=args.env_file, tag=args.tag,
                                                 linked_to_service=args.link_service,
                                                 autorestart=args.autorestart, autodestroy=args.autodestroy,
                                                 autoredeploy=args.autoredeploy, roles=args.role,
                                                 sequential=args.sequential,
                                                 volume=args.volume, volumes_from=args.volumes_from,
                                                 deployment_strategy=args.deployment_strategy)

        args = self.parser.parse_args(['service', 'scale', 'id', '3'])
        dispatch_cmds(args)
        mock_cmds.service_scale.assert_called_with(args.identifier, args.target_num_containers)

        args = self.parser.parse_args(['service', 'set', 'id'])
        dispatch_cmds(args)
        mock_cmds.service_set.assert_called_with(args.identifier, image=args.image, cpu_shares=args.cpushares,
                                                 memory=args.memory, privileged=args.privileged,
                                                 target_num_containers=args.target_num_containers,
                                                 run_command=args.run_command,
                                                 entrypoint=args.entrypoint, expose=args.expose, publish=args.publish,
                                                 envvars=args.env, envfiles=args.env_file,
                                                 tag=args.tag, linked_to_service=args.link_service,
                                                 autorestart=args.autorestart, autodestroy=args.autodestroy,
                                                 autoredeploy=args.autoredeploy, roles=args.role,
                                                 sequential=args.sequential, redeploy=args.redeploy,
                                                 volume=args.volume, volumes_from=args.volumes_from,
                                                 deployment_strategy=args.deployment_strategy)

        args = self.parser.parse_args(['service', 'start', 'id'])
        dispatch_cmds(args)
        mock_cmds.service_start.assert_called_with(args.identifier)

        args = self.parser.parse_args(['service', 'stop', 'id'])
        dispatch_cmds(args)
        mock_cmds.service_stop.assert_called_with(args.identifier)

        args = self.parser.parse_args(['service', 'terminate', 'id'])
        dispatch_cmds(args)
        mock_cmds.service_terminate.assert_called_with(args.identifier)

    @mock.patch('tutumcli.tutum_cli.commands')
    def test_container_dispatch(self, mock_cmds):
        args = self.parser.parse_args(['container', 'inspect', 'id'])
        dispatch_cmds(args)
        mock_cmds.container_inspect.assert_called_with(args.identifier)

        args = self.parser.parse_args(['container', 'logs', 'id'])
        dispatch_cmds(args)
        mock_cmds.container_logs.assert_called_with(args.identifier)

        args = self.parser.parse_args(['container', 'ps'])
        dispatch_cmds(args)
        mock_cmds.container_ps.assert_called_with(args.identifier, args.quiet, args.status, args.service)

        args = self.parser.parse_args(['container', 'start', 'id'])
        dispatch_cmds(args)
        mock_cmds.container_start.assert_called_with(args.identifier)

        args = self.parser.parse_args(['container', 'stop', 'id'])
        dispatch_cmds(args)
        mock_cmds.container_stop.assert_called_with(args.identifier)

        args = self.parser.parse_args(['container', 'terminate', 'id'])
        dispatch_cmds(args)
        mock_cmds.container_terminate.assert_called_with(args.identifier)

    @mock.patch('tutumcli.tutum_cli.commands')
    def test_image_dispatch(self, mock_cmds):
        args = self.parser.parse_args(['image', 'list'])
        dispatch_cmds(args)
        mock_cmds.image_list.assert_called_with(args.quiet, args.jumpstarts, args.linux)

        args = self.parser.parse_args(['image', 'register', 'name'])
        dispatch_cmds(args)
        mock_cmds.image_register(args.image_name, args.description)

        args = self.parser.parse_args(['image', 'push', 'name'])
        dispatch_cmds(args)
        mock_cmds.image_push(args.name, args.public)

        args = self.parser.parse_args(['image', 'rm', 'name'])
        dispatch_cmds(args)
        mock_cmds.image_rm(args.image_name)

        args = self.parser.parse_args(['image', 'search', 'name'])
        dispatch_cmds(args)
        mock_cmds.image_search(args.query)

        args = self.parser.parse_args(['image', 'update', 'name'])
        dispatch_cmds(args)
        mock_cmds.image_update(args.image_name, args.username, args.password, args.description)

    @mock.patch('tutumcli.tutum_cli.commands')
    def test_node_dispatch(self, mock_cmds):
        args = self.parser.parse_args(['node', 'inspect', 'id'])
        dispatch_cmds(args)
        mock_cmds.node_inspect.assert_called_with(args.identifier)

        args = self.parser.parse_args(['node', 'list'])
        dispatch_cmds(args)
        mock_cmds.node_list(args.quiet)

        args = self.parser.parse_args(['node', 'rm', 'id'])
        dispatch_cmds(args)
        mock_cmds.node_rm(args.identifier)

        args = self.parser.parse_args(['node', 'upgrade', 'id'])
        dispatch_cmds(args)
        mock_cmds.node_rm(args.identifier)

    @mock.patch('tutumcli.tutum_cli.commands')
    def test_nodecluster_dispatch(self, mock_cmds):
        args = self.parser.parse_args(['nodecluster', 'create', 'name', '1', '2', '3'])
        dispatch_cmds(args)
        mock_cmds.nodecluster_create(args.target_num_nodes, args.name,
                                     args.provider, args.region, args.nodetype)

        args = self.parser.parse_args(['nodecluster', 'inspect', 'id'])
        dispatch_cmds(args)
        mock_cmds.nodecluster_inspect(args.identifier)

        args = self.parser.parse_args(['nodecluster', 'list'])
        dispatch_cmds(args)
        mock_cmds.nodecluster_list(args.quiet)

        args = self.parser.parse_args(['nodecluster', 'provider'])
        dispatch_cmds(args)
        mock_cmds.nodecluster_show_providers(args.quiet)

        args = self.parser.parse_args(['nodecluster', 'region', '-p', 'digitalocean'])
        dispatch_cmds(args)
        mock_cmds.nodecluster_show_regions(args.provider)

        args = self.parser.parse_args(['nodecluster', 'nodetype', '-r', 'ams1', '-p', 'digitalocean'])
        dispatch_cmds(args)
        mock_cmds.nodecluster_show_types(args.provider, args.region)

        args = self.parser.parse_args(['nodecluster', 'rm', 'id'])
        dispatch_cmds(args)
        mock_cmds.nodecluster_rm(args.identifier)

        args = self.parser.parse_args(['nodecluster', 'scale', 'id', '3'])
        dispatch_cmds(args)
        mock_cmds.nodecluster_scale(args.identifier, args.target_num_nodes)

    @mock.patch('tutumcli.tutum_cli.commands')
    def test_tag_dispatch(self, mock_cmds):
        args = self.parser.parse_args(['tag', 'add', '-t', 'abc', 'id'])
        dispatch_cmds(args)
        mock_cmds.tag_add.assert_called_with(args.identifier, args.tag)

        args = self.parser.parse_args(['tag', 'list', 'abc', 'id'])
        dispatch_cmds(args)
        mock_cmds.tag_list.assert_called_with(args.identifier, args.quiet)

        args = self.parser.parse_args(['tag', 'rm', '-t', 'abc', 'id'])
        dispatch_cmds(args)
        mock_cmds.tag_rm.assert_called_with(args.identifier, args.tag)

        args = self.parser.parse_args(['tag', 'set', '-t', 'abc', 'id'])
        dispatch_cmds(args)
        mock_cmds.tag_set.assert_called_with(args.identifier, args.tag)


class ParserTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()

    def tearDown(self):
        sys.stdout = self.stdout

    def compare_output(self, output, args):
        parser = initialize_parser()
        argv = patch_help_option(args)

        parser.parse_args(argv)

        out = self.buf.getvalue()
        self.buf.truncate(0)

        self.assertEqual(' '.join(output.split()), ' '.join(out.split()))

    @mock.patch('tutumcli.tutum_cli.argparse.ArgumentParser.add_argument')
    @mock.patch('tutumcli.tutum_cli.argparse.ArgumentParser.exit')
    def test_tutum_version(self, mock_exit, mock_add_arg):
        initialize_parser()
        mock_add_arg.assert_any_call('-v', '--version', action='version', version='%(prog)s ' + tutumcli.__version__)
