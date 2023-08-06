from __future__ import print_function
import getpass
import ConfigParser
import json
import sys
import os
import distutils
import logging
from os.path import join, expanduser, abspath

import tutum
import docker
from tutum.api import auth
from tutum.api import exceptions

from exceptions import StreamOutputError, ObjectNotFound
from tutumcli import utils


TUTUM_FILE = '.tutum'
AUTH_SECTION = 'auth'
USER_OPTION = "user"
APIKEY_OPTION = 'apikey'
AUTH_ERROR = 'auth_error'
NO_ERROR = 'no_error'

TUTUM_AUTH_ERROR_EXIT_CODE = 2
EXCEPTION_EXIT_CODE = 3

cli_log = logging.getLogger("cli")


def login():
    username = raw_input("Username: ")
    password = getpass.getpass()
    try:
        user, api_key = auth.get_auth(username, password)
        if api_key is not None:
            config = ConfigParser.ConfigParser()
            config.add_section(AUTH_SECTION)
            config.set(AUTH_SECTION, USER_OPTION, user)
            config.set(AUTH_SECTION, APIKEY_OPTION, api_key)
            with open(join(expanduser('~'), TUTUM_FILE), 'w') as cfgfile:
                config.write(cfgfile)
            print("Login succeeded!")
    except exceptions.TutumAuthError:
        registered, text = utils.try_register(username, password)
        if registered:
            print(text)
        else:
            if 'username: A user with that username already exists.' in text:
                print("Wrong username and/or password. Please try to login again", file=sys.stderr)
                sys.exit(TUTUM_AUTH_ERROR_EXIT_CODE)
            else:
                text = text.replace('password1', 'password')
                text = text.replace('password2', 'password')
                text = text.replace('\npassword: This field is required.', '', 1)
                print(text, file=sys.stderr)
                sys.exit(TUTUM_AUTH_ERROR_EXIT_CODE)
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(EXCEPTION_EXIT_CODE)


def verify_auth(args):
    def _login():
        username = raw_input("Username: ")
        password = getpass.getpass()
        try:
            user, api_key = auth.get_auth(username, password)
            if api_key is not None:
                config = ConfigParser.ConfigParser()
                config.add_section(AUTH_SECTION)
                config.set(AUTH_SECTION, USER_OPTION, user)
                config.set(AUTH_SECTION, APIKEY_OPTION, api_key)
                with open(join(expanduser('~'), TUTUM_FILE), 'w') as cfgfile:
                    config.write(cfgfile)
                return True
        except tutum.TutumAuthError:
            return False
        except Exception as e:
            print(e, file=sys.stderr)
            sys.exit(EXCEPTION_EXIT_CODE)

    if args.cmd != 'login':
        try:
            tutum.api.http.send_request("GET", "/auth")
        except tutum.TutumAuthError:
            print("Not Authorized, Please login:", file=sys.stderr)
            while True:
                success = _login()
                if success:
                    print("Login succeeded!")
                    # Update user and apikey for SDK
                    tutum.user = auth.load_from_file()[0] or os.environ.get('TUTUM_USER', None)
                    tutum.apikey = auth.load_from_file()[1] or os.environ.get('TUTUM_APIKEY', None)
                    break
                else:
                    print("Not Authorized, Please login:", file=sys.stderr)


def build(tag, working_directory):
    directory = abspath(working_directory)
    try:
        work_dir = abspath(working_directory)
        dockercfg_dir = expanduser("~/.dockercfg")
        docker_path = distutils.spawn.find_executable("docker")

        if not docker_path:
            print("Cannot find docker locally", file=sys.stderr)
            sys.exit(EXCEPTION_EXIT_CODE)

        if os.path.exists(dockercfg_dir):
            cmd = "docker run -ti --rm --privileged " \
                  "-v %s:/app -v" \
                  "-v %s:/usr/bin/docker:r " \
                  " %s:/.dockercfg:r " \
                  "-e IMAGE_NAME=%s " % (work_dir, docker_path, dockercfg_dir, tag)
        else:
            cmd = "docker run -ti --rm --privileged " \
                  "-v %s:/app " \
                  "-v %s:/usr/bin/docker:r " \
                  "-e USERNAME=%s " \
                  "-e PASSWORD=%s " \
                  "-e IMAGE_NAME=%s " \
                  % (work_dir, docker_path, tutum.user, tutum.apikey, tag)

        if os.path.exists("/var/run/docker.sock"):
            cmd += "-v /var/run/docker.sock:/var/run/docker.sock:rw "

        if os.getenv("DOCKER_HOST"):
            cmd += "-e DOCKER_HOST=%s " % os.getenv("DOCKER_HOST")

        if os.getenv("DOCKER_CERT_PATH"):
            cmd += "-e DOCKER_CERT_PATH=%s " % os.getenv("DOCKER_CERT_PATH")

        if os.getenv("DOCKER_HOST"):
            cmd += "-e DOCKER_TLS_VERIFY=%s " % os.getenv("DOCKER_TLS_VERIFY")

        cmd += "tutum/builder"

        cli_log.debug("tutum build:%s" % cmd)

        os.system(cmd)
    except Exception as e:
        print(e, file=sys.stderr)


def service_inspect(identifiers):
    has_exception = False
    for identifier in identifiers:
        try:
            service = utils.fetch_remote_service(identifier)
            print(json.dumps(service.get_all_attributes(), indent=2))
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def service_logs(identifiers):
    has_exception = False
    for identifier in identifiers:
        try:
            service = utils.fetch_remote_service(identifier)
            print(service.logs)
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def service_ps(quiet=False, status=None):
    try:
        headers = ["NAME", "UUID", "STATUS", "#CONTAINERS", "IMAGE", "DEPLOYED", "PUBLIC DNS"]
        service_list = tutum.Service.list(state=status)
        data_list = []
        long_uuid_list = []
        has_unsynchronized_service = False
        for service in service_list:
            service_state = utils.add_unicode_symbol_to_state(service.state)
            if not service.synchronized and service.state != "Redeploying":
                service_state += "(*)"
                has_unsynchronized_service = True
            data_list.append([service.name, service.uuid[:8],
                              service_state,
                              service.current_num_containers,
                              service.image_name,
                              utils.get_humanize_local_datetime_from_utc_datetime_string(service.deployed_datetime),
                              service.public_dns])
            long_uuid_list.append(service.uuid)
        if len(data_list) == 0:
            data_list.append(["", "", "", "", "", ""])

        if quiet:
            for uuid in long_uuid_list:
                print(uuid)
        else:
            utils.tabulate_result(data_list, headers)
            if has_unsynchronized_service:
                print(
                    "\n(*) Please note that this service needs to be redeployed to have its configuration changes applied")

    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(EXCEPTION_EXIT_CODE)


def service_redeploy(identifiers):
    has_exception = False
    for identifier in identifiers:
        try:
            service = utils.fetch_remote_service(identifier)
            result = service.redeploy()
            if result:
                print(service.uuid)
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def service_create(image, name, cpu_shares, memory, privileged, target_num_containers, run_command, entrypoint,
                   expose, publish, envvars, envfiles, tag, linked_to_service, autorestart, autodestroy, autoredeploy,
                   roles, sequential, volume, volumes_from, deployment_strategy):
    try:
        ports = utils.parse_published_ports(publish)

        # Add exposed_port to ports, excluding whose inner_port that has been defined in published ports
        exposed_ports = utils.parse_exposed_ports(expose)
        for exposed_port in exposed_ports:
            existed = False
            for port in ports:
                if exposed_port.get('inner_port', '') == port.get('inner_port', ''):
                    existed = True
                    break
            if not existed:
                ports.append(exposed_port)

        envvars = utils.parse_envvars(envvars, envfiles)
        links_service = utils.parse_links(linked_to_service, 'to_service')

        tags = []
        if tag:
            if isinstance(tag, list):
                for t in tag:
                    tags.append({"name": t})
            else:
                tags.append({"name": tag})

        bindings = utils.parse_volume(volume)
        bindings.extend(utils.parse_volumes_from(volumes_from))

        service = tutum.Service.create(image=image, name=name, cpu_shares=cpu_shares,
                                       memory=memory, privileged=privileged,
                                       target_num_containers=target_num_containers, run_command=run_command,
                                       entrypoint=entrypoint, container_ports=ports, container_envvars=envvars,
                                       linked_to_service=links_service,
                                       autorestart=autorestart, autodestroy=autodestroy, autoredeploy=autoredeploy,
                                       roles=roles, sequential_deployment=sequential, tags=tags, bindings=bindings,
                                       deployment_strategy=deployment_strategy)
        result = service.save()
        if result:
            print(service.uuid)
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(EXCEPTION_EXIT_CODE)


def service_run(image, name, cpu_shares, memory, privileged, target_num_containers, run_command, entrypoint,
                expose, publish, envvars, envfiles, tag, linked_to_service, autorestart, autodestroy, autoredeploy,
                roles, sequential, volume, volumes_from, deployment_strategy):
    try:
        ports = utils.parse_published_ports(publish)

        # Add exposed_port to ports, excluding whose inner_port that has been defined in published ports
        exposed_ports = utils.parse_exposed_ports(expose)
        for exposed_port in exposed_ports:
            existed = False
            for port in ports:
                if exposed_port.get('inner_port', '') == port.get('inner_port', ''):
                    existed = True
                    break
            if not existed:
                ports.append(exposed_port)

        envvars = utils.parse_envvars(envvars, envfiles)
        links_service = utils.parse_links(linked_to_service, 'to_service')

        tags = []
        if tag:
            if isinstance(tag, list):
                for t in tag:
                    tags.append({"name": t})
            else:
                tags.append({"name": tag})

        bindings = utils.parse_volume(volume)
        bindings.extend(utils.parse_volumes_from(volumes_from))

        service = tutum.Service.create(image=image, name=name, cpu_shares=cpu_shares,
                                       memory=memory, privileged=privileged,
                                       target_num_containers=target_num_containers, run_command=run_command,
                                       entrypoint=entrypoint, container_ports=ports, container_envvars=envvars,
                                       linked_to_service=links_service,
                                       autorestart=autorestart, autodestroy=autodestroy, autoredeploy=autoredeploy,
                                       roles=roles, sequential_deployment=sequential, tags=tags, bindings=bindings,
                                       deployment_strategy=deployment_strategy)
        service.save()
        result = service.start()
        if result:
            print(service.uuid)
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(EXCEPTION_EXIT_CODE)


def service_scale(identifiers, target_num_containers):
    has_exception = False
    for identifier in identifiers:
        try:
            service = utils.fetch_remote_service(identifier)
            service.target_num_containers = target_num_containers
            result = service.save()
            if result:
                print(service.uuid)
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def service_set(identifiers, image, cpu_shares, memory, privileged, target_num_containers, run_command, entrypoint,
                expose, publish, envvars, envfiles, tag, linked_to_service, autorestart, autodestroy, autoredeploy,
                roles, sequential, redeploy, volume, volumes_from, deployment_strategy):
    has_exception = False
    for identifier in identifiers:
        try:
            service = utils.fetch_remote_service(identifier, raise_exceptions=True)
            if service is not None:
                if image:
                    service.image = image
                if cpu_shares:
                    service.cpu_shares = cpu_shares
                if memory:
                    service.memory = memory
                if privileged:
                    service.privileged = privileged
                if target_num_containers:
                    service.target_num_containers = target_num_containers
                if run_command:
                    service.run_command = run_command
                if entrypoint:
                    service.entrypoint = entrypoint

                ports = utils.parse_published_ports(publish)
                # Add exposed_port to ports, excluding whose inner_port that has been defined in published ports
                exposed_ports = utils.parse_exposed_ports(expose)
                for exposed_port in exposed_ports:
                    existed = False
                    for port in ports:
                        if exposed_port.get('inner_port', '') == port.get('inner_port', ''):
                            existed = True
                            break
                    if not existed:
                        ports.append(exposed_port)
                if ports:
                    service.container_ports = ports

                envvars = utils.parse_envvars(envvars, envfiles)
                if envvars:
                    service.container_envvars = envvars

                if tag:
                    service.tags = []
                    for t in tag:
                        new_tag = {"name": t}
                        if new_tag not in service.tags:
                            service.tags.append(new_tag)
                    service.__addchanges__("tags")

                links_service = utils.parse_links(linked_to_service, 'to_service')
                if linked_to_service:
                    service.linked_to_service = links_service

                if autorestart:
                    service.autorestart = autorestart

                if autodestroy:
                    service.autodestroy = autodestroy

                if autoredeploy:
                    service.autoredeploy = autoredeploy

                if roles:
                    service.roles = roles

                if sequential:
                    service.sequential_deployment = sequential

                bindings = utils.parse_volume(volume)
                bindings.extend(utils.parse_volumes_from(volumes_from))
                if bindings:
                    service.bindings = bindings

                if deployment_strategy:
                    service.deployment_strategy = deployment_strategy

                result = service.save()
                if result:
                    if redeploy:
                        print("Redeploying Service ...")
                        result2 = service.redeploy()
                        if result2:
                            print(service.uuid)
                    else:
                        print(service.uuid)
                        print("Service must be redeployed to have its configuration changes applied.")
                        print("To redeploy execute: $ tutum service redeploy", identifier)
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def service_start(identifiers):
    has_exception = False
    for identifier in identifiers:
        try:
            service = utils.fetch_remote_service(identifier)
            result = service.start()
            if result:
                print(service.uuid)
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def service_stop(identifiers):
    has_exception = False
    for identifier in identifiers:
        try:
            service = utils.fetch_remote_service(identifier)
            result = service.stop()
            if result:
                print(service.uuid)
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def service_terminate(identifiers):
    has_exception = False
    for identifier in identifiers:
        try:
            service = utils.fetch_remote_service(identifier)
            result = service.delete()
            if result:
                print(service.uuid)
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def container_inspect(identifiers):
    has_exception = False
    for identifier in identifiers:
        try:
            container = utils.fetch_remote_container(identifier)
            print(json.dumps(container.get_all_attributes(), indent=2))
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def container_logs(identifiers):
    has_exception = False
    for identifier in identifiers:
        try:
            container = utils.fetch_remote_container(identifier)
            print(container.logs)
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def container_ps(identifier, quiet, status, service):
    try:
        headers = ["NAME", "UUID", "STATUS", "IMAGE", "RUN COMMAND", "EXIT CODE", "DEPLOYED", "PORTS"]

        if identifier is None:
            containers = tutum.Container.list(state=status)
        elif utils.is_uuid4(identifier):
            containers = tutum.Container.list(uuid=identifier, state=status)
        else:
            containers = tutum.Container.list(name=identifier, state=status) + \
                         tutum.Container.list(uuid__startswith=identifier, state=status)

        data_list = []
        long_uuid_list = []

        if service:
            service_obj = utils.fetch_remote_service(service, raise_exceptions=False)
            if isinstance(service_obj, ObjectNotFound):
                raise ObjectNotFound("Identifier '%s' does not match any service" % service)

        for container in containers:
            if service:
                if container.service != service_obj.resource_uri:
                    continue

            ports = []
            for index, port in enumerate(container.container_ports):
                ports_string = ""
                if port['outer_port'] is not None:
                    ports_string += "%s:%d->" % (container.public_dns, port['outer_port'])
                ports_string += "%d/%s" % (port['inner_port'], port['protocol'])
                ports.append(ports_string)

            ports_string = ", ".join(ports)
            data_list.append([container.name,
                              container.uuid[:8],
                              utils.add_unicode_symbol_to_state(container.state),
                              container.image_name,
                              container.run_command,
                              container.exit_code,
                              utils.get_humanize_local_datetime_from_utc_datetime_string(container.deployed_datetime),
                              ports_string])
            long_uuid_list.append(container.uuid)
        if len(data_list) == 0:
            data_list.append(["", "", "", "", "", "", "", ""])
        if quiet:
            for uuid in long_uuid_list:
                print(uuid)
        else:
            utils.tabulate_result(data_list, headers)
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(EXCEPTION_EXIT_CODE)


def container_start(identifiers):
    has_exception = False
    for identifier in identifiers:
        try:
            container = utils.fetch_remote_container(identifier)
            result = container.start()
            if result:
                print(container.uuid)
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def container_stop(identifiers):
    has_exception = False
    for identifier in identifiers:
        try:
            container = utils.fetch_remote_container(identifier)
            result = container.stop()
            if result:
                print(container.uuid)
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def container_terminate(identifiers):
    has_exception = False
    for identifier in identifiers:
        try:
            container = utils.fetch_remote_container(identifier)
            result = container.delete()
            if result:
                print(container.uuid)
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def image_list(quiet=False, jumpstarts=False, linux=False):
    try:
        headers = ["NAME", "DESCRIPTION"]
        data_list = []
        name_list = []
        if jumpstarts:
            image_list = tutum.Image.list(starred=True)
        elif linux:
            image_list = tutum.Image.list(base_image=True)
        else:
            image_list = tutum.Image.list(is_private_image=True)
        if len(image_list) != 0:
            for image in image_list:
                data_list.append([image.name, image.description])
                name_list.append(image.name)
        else:
            data_list.append(["", ""])

        if quiet:
            for name in name_list:
                print(name)
        else:
            utils.tabulate_result(data_list, headers)

    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(EXCEPTION_EXIT_CODE)


def image_register(repository, description):
    print('Please input username and password of the repository:')
    username = raw_input('Username: ')
    password = getpass.getpass()
    try:
        image = tutum.Image.create(name=repository, username=username, password=password, description=description)
        result = image.save()
        if result:
            print(image.name)
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(EXCEPTION_EXIT_CODE)


def image_push(name, public):
    def push_to_public(repository):
        print('Pushing %s to public registry ...' % repository)

        output_status = NO_ERROR
        # tag a image to its name to check if the images exists
        try:
            docker_client.tag(name, name)
        except Exception as e:
            print(e, file=sys.stderr)
            sys.exit(EXCEPTION_EXIT_CODE)
        try:
            stream = docker_client.push(repository, stream=True)
            utils.stream_output(stream, sys.stdout)
        except StreamOutputError as e:
            if 'status 401' in e.message.lower():
                output_status = AUTH_ERROR
            else:
                print(e, file=sys.stderr)
                sys.exit(EXCEPTION_EXIT_CODE)
        except Exception as e:
            print(e.message, file=sys.stderr)
            sys.exit(EXCEPTION_EXIT_CODE)

        if output_status == NO_ERROR:
            print('')
            sys.exit()

        if output_status == AUTH_ERROR:
            print('Please login prior to push:')
            username = raw_input('Username: ')
            password = getpass.getpass()
            email = raw_input('Email: ')
            try:
                result = docker_client.login(username, password=password, email=email)
                if isinstance(result, dict):
                    print(result.get('Status', None))
            except Exception as e:
                print(e, file=sys.stderr)
                sys.exit(TUTUM_AUTH_ERROR_EXIT_CODE)
            push_to_public(repository)

    def push_to_tutum(repository):
        print('Pushing %s to Tutum private registry ...' % repository)

        user = tutum.user
        apikey = tutum.apikey
        if user is None or apikey is None:
            print('Not authorized')
            sys.exit(TUTUM_AUTH_ERROR_EXIT_CODE)

        try:
            registry = os.getenv('TUTUM_REGISTRY_URL') or 'https://tutum.co/v1/'
            docker_client.login(user, apikey, registry=registry)
        except Exception as e:
            print(e, file=sys.stderr)
            sys.exit(TUTUM_AUTH_ERROR_EXIT_CODE)

        if repository:
            repository = filter(None, repository.split('/'))[-1]
        tag = None
        if ':' in repository:
            tag = repository.split(':')[-1]
            repository = repository.replace(':%s' % tag, '')
        repository = '%s/%s/%s' % (registry.split('//')[-1].split('/')[0], user, repository)

        if tag:
            print('Tagging %s as %s:%s ...' % (name, repository, tag))
        else:
            print('Tagging %s as %s ...' % (name, repository))

        try:
            docker_client.tag(name, repository, tag=tag, force=True)
        except Exception as e:
            print(e, file=sys.stderr)
            sys.exit(EXCEPTION_EXIT_CODE)

        stream = docker_client.push(repository, stream=True)
        try:
            utils.stream_output(stream, sys.stdout)
        except docker.errors.APIError as e:
            print(e.explanation, file=sys.stderr)
            sys.exit(EXCEPTION_EXIT_CODE)
        except Exception as e:
            print(e.message, file=sys.stderr)
            sys.exit(EXCEPTION_EXIT_CODE)
        print('')

    docker_client = utils.get_docker_client()
    if public:
        push_to_public(name)
    else:
        push_to_tutum(name)


def image_rm(repositories):
    has_exception = False
    for repository in repositories:
        try:
            image = tutum.Image.fetch(repository)
            result = image.delete()
            if result:
                print(repository)
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def image_search(text):
    try:
        docker_client = utils.get_docker_client()
        results = docker_client.search(text)
        headers = ["NAME", "DESCRIPTION", "STARS", "OFFICIAL", "TRUSTED"]
        data_list = []
        if len(results) != 0:
            for result in results:
                description = result["description"].replace("\n", "\\n")
                description = description[:80] + " [...]" if len(result["description"]) > 80 else description
                data_list.append([result["name"], description, str(result["star_count"]),
                                  u"\u2713" if result["is_official"] else "",
                                  u"\u2713" if result["is_trusted"] else ""])
        else:
            data_list.append(["", "", "", "", ""])
        utils.tabulate_result(data_list, headers)
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(EXCEPTION_EXIT_CODE)


def image_update(repositories, username, password, description):
    has_exception = False
    for repository in repositories:
        try:
            image = tutum.Image.fetch(repository)
            if username is not None:
                image.username = username
            if password is not None:
                image.password = password
            if description is not None:
                image.description = description
            result = image.save()
            if result:
                print(image.name)
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def node_list(quiet=False):
    try:
        headers = ["UUID", "FQDN", "LASTSEEN", "STATUS", "CLUSTER", "DOCKER_VER"]
        node_list = tutum.Node.list()
        data_list = []
        long_uuid_list = []
        for node in node_list:
            cluster_name = node.node_cluster
            try:
                cluster_name = tutum.NodeCluster.fetch(node.node_cluster.strip("/").split("/")[-1]).name
            except:
                pass

            data_list.append([node.uuid[:8],
                              node.external_fqdn,
                              utils.get_humanize_local_datetime_from_utc_datetime_string(node.last_seen),
                              utils.add_unicode_symbol_to_state(node.state),
                              cluster_name, node.docker_version])
            long_uuid_list.append(node.uuid)
        if len(data_list) == 0:
            data_list.append(["", "", "", "", "", ""])
        if quiet:
            for uuid in long_uuid_list:
                print(uuid)
        else:
            utils.tabulate_result(data_list, headers)
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(EXCEPTION_EXIT_CODE)


def node_inspect(identifiers):
    has_exception = False
    for identifier in identifiers:
        try:
            node = utils.fetch_remote_node(identifier)
            print(json.dumps(tutum.Node.fetch(node.uuid).get_all_attributes(), indent=2))
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def node_rm(identifiers):
    has_exception = False
    for identifier in identifiers:
        try:
            node = utils.fetch_remote_node(identifier)
            result = node.delete()
            if result:
                print(node.uuid)
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def node_upgrade(identifiers):
    has_exception = False
    for identifier in identifiers:
        try:
            node = utils.fetch_remote_node(identifier)
            result = node.upgrade_docker()
            if result:
                print(node.uuid)
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def node_byo():
    token = ""
    try:
        json = tutum.api.http.send_request("POST", "token")
        if json:
            token = json.get("token", "")
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(EXCEPTION_EXIT_CODE)

    print("Tutum lets you use your own servers as nodes to run containers. For this you have to install our agent.")
    print("Run the following command on your server:")
    print()
    print("\tcurl -Ls https://files.tutum.co/scripts/install-agent.sh | sudo -H sh -s", token)
    print()


def nodecluster_list(quiet):
    try:
        headers = ["NAME", "UUID", "REGION", "TYPE", "DEPLOYED", "STATUS", "CURRENT#NODES", "TARGET#NODES"]
        nodecluster_list = tutum.NodeCluster.list()
        data_list = []
        long_uuid_list = []
        for nodecluster in nodecluster_list:
            if quiet:
                long_uuid_list.append(nodecluster.uuid)
                continue

            node_type = nodecluster.node_type
            region = nodecluster.region
            try:
                node_type = tutum.NodeType.fetch(nodecluster.node_type.strip("/").split("api/v1/nodetype/")[-1]).label
                region = tutum.Region.fetch(nodecluster.region.strip("/").split("api/v1/region/")[-1]).label
            except Exception as e:
                pass

            data_list.append([nodecluster.name,
                              nodecluster.uuid[:8],
                              region,
                              node_type,
                              utils.get_humanize_local_datetime_from_utc_datetime_string(nodecluster.deployed_datetime),
                              nodecluster.state,
                              nodecluster.current_num_nodes,
                              nodecluster.target_num_nodes])
            long_uuid_list.append(nodecluster.uuid)
        if len(data_list) == 0:
            data_list.append(["", "", "", "", "", "", "", ""])
        if quiet:
            for uuid in long_uuid_list:
                print(uuid)
        else:
            utils.tabulate_result(data_list, headers)
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(EXCEPTION_EXIT_CODE)


def nodecluster_inspect(identifiers):
    has_exception = False
    for identifier in identifiers:
        try:
            nodecluster = utils.fetch_remote_nodecluster(identifier)
            print(json.dumps(tutum.NodeCluster.fetch(nodecluster.uuid).get_all_attributes(), indent=2))
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def nodecluster_show_providers(quiet):
    try:
        headers = ["NAME", "LABEL", "REGIONS"]
        data_list = []
        name_list = []
        provider_list = tutum.Provider.list()
        for provider in provider_list:
            if quiet:
                name_list.append(provider.name)
                continue

            data_list.append([provider.name, provider.label,
                              ", ".join([region.strip("/").split("/")[-1] for region in provider.regions])])

        if len(data_list) == 0:
            data_list.append(["", "", ""])
        if quiet:
            for name in name_list:
                print(name)
        else:
            utils.tabulate_result(data_list, headers)
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(EXCEPTION_EXIT_CODE)


def nodecluster_show_regions(provider):
    try:
        headers = ["NAME", "LABEL", "PROVIDER", "TYPE"]
        data_list = []
        region_list = tutum.Region.list()
        for region in region_list:
            provider_name = region.resource_uri.strip("/").split("/")[-2]
            if provider and provider != provider_name:
                continue
            data_list.append([region.name, region.label, provider_name,
                              ", ".join([nodetype.strip("/").split("/")[-1] for nodetype in region.node_types])])

        if len(data_list) == 0:
            data_list.append(["", "", "", ""])
        utils.tabulate_result(data_list, headers)
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(EXCEPTION_EXIT_CODE)


def nodecluster_show_types(provider, region):
    try:
        headers = ["NAME", "LABEL", "PROVIDER", "REGIONS"]
        data_list = []
        nodetype_list = tutum.NodeType.list()
        for nodetype in nodetype_list:
            provider_name = nodetype.resource_uri.strip("/").split("/")[-2]
            regions = [region_uri.strip("/").split("/")[-1] for region_uri in nodetype.regions]
            if provider and provider != provider_name:
                continue

            if region and region not in regions:
                continue
            data_list.append([nodetype.name, nodetype.label, provider_name,
                              ", ".join(regions)])

        if len(data_list) == 0:
            data_list.append(["", "", "", ""])
        utils.tabulate_result(data_list, headers)
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(EXCEPTION_EXIT_CODE)


def nodecluster_create(target_num_nodes, name, provider, region, nodetype):
    region_uri = "/api/v1/region/%s/%s/" % (provider, region)
    nodetype_uri = "/api/v1/nodetype/%s/%s/" % (provider, nodetype)

    try:
        nodecluster = tutum.NodeCluster.create(name=name, target_num_nodes=target_num_nodes,
                                               region=region_uri, node_type=nodetype_uri)
        nodecluster.save()
        result = nodecluster.deploy()
        if result:
            print(nodecluster.uuid)
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(EXCEPTION_EXIT_CODE)


def nodecluster_rm(identifiers):
    has_exception = False
    for identifier in identifiers:
        try:
            nodecluster = utils.fetch_remote_nodecluster(identifier)
            result = nodecluster.delete()
            if result:
                print(nodecluster.uuid)
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def nodecluster_scale(identifiers, target_num_nodes):
    has_exception = False
    for identifier in identifiers:
        try:
            nodecluster = utils.fetch_remote_nodecluster(identifier)
            nodecluster.target_num_nodes = target_num_nodes
            result = nodecluster.save()
            if result:
                print(nodecluster.uuid)
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def tag_add(identifiers, tags):
    has_exception = False
    for identifier in identifiers:
        try:
            try:
                obj = utils.fetch_remote_service(identifier)
            except ObjectNotFound:
                try:
                    obj = utils.fetch_remote_nodecluster(identifier)
                except ObjectNotFound:
                    try:
                        obj = utils.fetch_remote_node(identifier)
                    except ObjectNotFound:
                        raise ObjectNotFound(
                            "Identifier '%s' does not match any service, node or nodecluster" % identifier)

            tag = tutum.Tag.fetch(obj)
            tag.add(tags)
            tag.save()
            print(obj.uuid)
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def tag_list(identifiers, quiet):
    has_exception = False

    headers = ["IDENTIFIER", "TYPE", "TAGS"]
    data_list = []
    tags_list = []
    for identifier in identifiers:
        try:
            obj = utils.fetch_remote_service(identifier, raise_exceptions=False)
            if isinstance(obj, ObjectNotFound):
                obj = utils.fetch_remote_nodecluster(identifier, raise_exceptions=False)
                if isinstance(obj, ObjectNotFound):
                    obj = utils.fetch_remote_node(identifier, raise_exceptions=False)
                    if isinstance(obj, ObjectNotFound):
                        raise ObjectNotFound(
                            "Identifier '%s' does not match any service, node or nodecluster" % identifier)
                    else:
                        obj_type = 'Node'
                else:
                    obj_type = 'NodeCluster'
            else:
                obj_type = 'Service'

            tagnames = []
            for tags in tutum.Tag.fetch(obj).list():
                tagname = tags.get('name', '')
                if tagname:
                    tagnames.append(tagname)

            data_list.append([identifier, obj_type, ' '.join(tagnames)])
            tags_list.append(' '.join(tagnames))
        except Exception as e:
            if isinstance(e, ObjectNotFound):
                data_list.append([identifier, 'None', ''])
            else:
                data_list.append([identifier, '', ''])
            tags_list.append('')
            print(e, file=sys.stderr)
            has_exception = True
    if quiet:
        for tags in tags_list:
            print(tags)
    else:
        utils.tabulate_result(data_list, headers)
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def tag_rm(identifiers, tags):
    has_exception = False
    for identifier in identifiers:
        try:
            try:
                obj = utils.fetch_remote_service(identifier)
            except ObjectNotFound:
                try:
                    obj = utils.fetch_remote_nodecluster(identifier)
                except ObjectNotFound:
                    try:
                        obj = utils.fetch_remote_node(identifier)
                    except ObjectNotFound:
                        raise ObjectNotFound(
                            "Identifier '%s' does not match any service, node or nodecluster" % identifier)

            tag = tutum.Tag.fetch(obj)
            for t in tags:
                try:
                    tag.delete(t)
                except Exception as e:
                    print(e, file=sys.stderr)
                    has_exception = True
            print(obj.uuid)
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def tag_set(identifiers, tags):
    has_exception = False
    for identifier in identifiers:
        try:
            try:
                obj = utils.fetch_remote_service(identifier)
            except ObjectNotFound:
                try:
                    obj = utils.fetch_remote_nodecluster(identifier)
                except ObjectNotFound:
                    try:
                        obj = utils.fetch_remote_node(identifier)
                    except ObjectNotFound:
                        raise ObjectNotFound(
                            "Identifier '%s' does not match any service, node or nodecluster" % identifier)

            obj.tags = []
            for t in tags:
                new_tag = {"name": t}
                if new_tag not in obj.tags:
                    obj.tags.append(new_tag)
            obj.__addchanges__("tags")
            obj.save()

            print(obj.uuid)
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def volume_list(quiet):
    try:
        headers = ["UUID", "STATE", "NODE", "VOLUMEGROUP"]
        data_list = []
        uuid_list = []
        volume_list = tutum.Volume.list()
        for volume in volume_list:
            if quiet:
                uuid_list.append(volume.uuid)
                continue

            data_list.append([volume.uuid, volume.state,
                              volume.node.strip("/").split("/")[-1],
                              volume.volume_group.strip("/").split("/")[-1]])

        if len(data_list) == 0:
            data_list.append(["", "", "", ""])
        if quiet:
            for uuid in uuid_list:
                print(uuid)
        else:
            utils.tabulate_result(data_list, headers)
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(EXCEPTION_EXIT_CODE)


def volume_inspect(identifiers):
    has_exception = False
    for identifier in identifiers:
        try:
            volume = utils.fetch_remote_volume(identifier)
            print(json.dumps(volume.get_all_attributes(), indent=2))
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def volumegroup_list(quiet):
    try:
        headers = ["NAME", "UUID", "STATE"]
        data_list = []
        uuid_list = []
        volumegroup_list = tutum.VolumeGroup.list()
        for volumegroup in volumegroup_list:
            if quiet:
                uuid_list.append(volumegroup.uuid)
                continue

            data_list.append([volumegroup.name, volumegroup.uuid, volumegroup.state])

        if len(data_list) == 0:
            data_list.append(["", "", ""])
        if quiet:
            for uuid in uuid_list:
                print(uuid)
        else:
            utils.tabulate_result(data_list, headers)
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(EXCEPTION_EXIT_CODE)


def volumegroup_inspect(identifiers):
    has_exception = False
    for identifier in identifiers:
        try:
            volumegroup = utils.fetch_remote_volumegroup(identifier)
            print(json.dumps(volumegroup.get_all_attributes(), indent=2))
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def webhookhandler_create(identifiers, names):
    has_exception = False
    for identifier in identifiers:
        try:
            service = utils.fetch_remote_service(identifier)
            webhookhandler = tutum.WebhookHandler.fetch(service)
            webhookhandler.add(names)
            webhookhandler.save()
            print(service.uuid)
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def webhookhandler_list(identifiers, quiet):
    has_exception = False

    headers = ["IDENTIFIER", "NAME", "UUID"]
    data_list = []
    uuid_list = []
    for identifier in identifiers:
        try:
            service = utils.fetch_remote_service(identifier)
            webhookhandler = tutum.WebhookHandler.fetch(service)
            handlers = webhookhandler.list()
            for handler in handlers:
                data_list.append([identifier, handler.get('name', ''), handler.get('uuid', '')])
                uuid_list.append(handler.get('uuid', ''))
        except Exception as e:
            print(e, file=sys.stderr)
            data_list.append([identifier, '', ''])
            uuid_list.append('')
            has_exception = True
    if quiet:
        for uuid in uuid_list:
            print(uuid)
    else:
        utils.tabulate_result(data_list, headers)
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def webhookhandler_rm(identifier, webhook_identifiers):
    has_exception = False
    try:
        service = utils.fetch_remote_service(identifier)
        webhookhandler = tutum.WebhookHandler.fetch(service)
        uuid_list = utils.get_uuids_of_webhookhandler(webhookhandler, webhook_identifiers)
        try:
            for uuid in uuid_list:
                webhookhandler.delete(uuid)
                print(uuid)
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    except Exception as e:
        print(e, file=sys.stderr)
        has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def stack_up(name, stackfile):
    try:
        stack = utils.loadStackFile(name=name, stackfile=stackfile)
        stack.save()
        result = stack.start()
        if result:
            print(stack.uuid)
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(EXCEPTION_EXIT_CODE)


def stack_create(name, stackfile):
    try:
        stack = utils.loadStackFile(name=name, stackfile=stackfile)
        result = stack.save()
        if result:
            print(stack.uuid)
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(EXCEPTION_EXIT_CODE)


def stack_inspect(identifiers):
    has_exception = False
    for identifier in identifiers:
        try:
            stack = utils.fetch_remote_stack(identifier)
            print(json.dumps(stack.get_all_attributes(), indent=2))
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def stack_list(quiet):
    try:
        headers = ["NAME", "UUID", "STATUS", "DEPLOYED", "DESTROYED"]
        stack_list = tutum.Stack.list()
        data_list = []
        long_uuid_list = []
        for stack in stack_list:
            data_list.append([stack.name,
                              stack.uuid[:8],
                              utils.add_unicode_symbol_to_state(stack.state),
                              utils.get_humanize_local_datetime_from_utc_datetime_string(stack.deployed_datetime),
                              utils.get_humanize_local_datetime_from_utc_datetime_string(stack.destroyed_datetime)])
            long_uuid_list.append(stack.uuid)

        if len(data_list) == 0:
            data_list.append(["", "", "", "", ""])

        if quiet:
            for uuid in long_uuid_list:
                print(uuid)
        else:
            utils.tabulate_result(data_list, headers)
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(EXCEPTION_EXIT_CODE)


def stack_redeploy(identifiers):
    has_exception = False
    for identifier in identifiers:
        try:
            stack = utils.fetch_remote_stack(identifier)
            result = stack.redeploy()
            if result:
                print(stack.uuid)
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def stack_start(identifiers):
    has_exception = False
    for identifier in identifiers:
        try:
            stack = utils.fetch_remote_stack(identifier)
            result = stack.start()
            if result:
                print(stack.uuid)
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def stack_stop(identifiers):
    has_exception = False
    for identifier in identifiers:
        try:
            stack = utils.fetch_remote_stack(identifier)
            result = stack.stop()
            if result:
                print(stack.uuid)
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def stack_terminate(identifiers):
    has_exception = False
    for identifier in identifiers:
        try:
            stack = utils.fetch_remote_stack(identifier)
            result = stack.delete()
            if result:
                print(stack.uuid)
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def stack_update(identifier, stackfile):
    try:
        stack = utils.loadStackFile(name=None, stackfile=stackfile, stack=utils.fetch_remote_stack(identifier))
        result = stack.save()
        if result:
            print(stack.uuid)
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(EXCEPTION_EXIT_CODE)
