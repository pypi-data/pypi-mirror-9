TUTUM = '''usage: tutum [-h] [-v]
             {build,container,image,login,node,nodecluster,service,tag,webhook-handler}
             ...

Tutum's CLI

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit

Tutum's CLI commands:
  {build,container,image,login,node,nodecluster,service,tag,webhook-handler}
    build               Build an image using an existing Dockerfile, or create
                        one using buildstep
    container           Container-related operations
    image               Image-related operations
    login               Login into Tutum
    node                Node-related operations
    nodecluster         NodeCluster-related operations
    service             Service-related operations
    tag                 Tag-related operations
    webhook-handler     Webhook-handler-related operations'''

# ##################################################

TUTUM_BUILD = '''usage: tutum build [-h] [-q] [--no-cache] [-t TAG] directory

Build an image using an existing Dockerfile, or create one using buildstep

positional arguments:
  directory          working directory

optional arguments:
  -h, --help         show this help message and exit
  -q, --quiet        print minimum information
  --no-cache         do not use the cache when building the image
  -t TAG, --tag TAG  repository name (and optionally a tag) to be applied to
                     the resulting image in case of success'''

# ##################################################

TUTUM_CONTAINER = '''usage: tutum container [-h]
                       {inspect,logs,ps,start,stop,terminate} ...

Container-related operations

optional arguments:
  -h, --help            show this help message and exit

tutum container commands:
  {inspect,logs,ps,start,stop,terminate}
    inspect             Inspect a container
    logs                Get logs from a container
    ps                  List containers
    start               Start a container
    stop                Stop a container
    terminate           Terminate a container'''

# ##################################################

TUTUM_CONTAINER_INSPECT = '''usage: tutum container inspect [-h] identifier [identifier ...]

Inspect a container

positional arguments:
  identifier  container's UUID (either long or short) or name

optional arguments:
  -h, --help  show this help message and exit'''

# ##################################################

TUTUM_CONTAINER_LOGS = '''usage: tutum container logs [-h] identifier [identifier ...]

Get logs from a container

positional arguments:
  identifier  container's UUID (either long or short) or name

optional arguments:
  -h, --help  show this help message and exit'''

# ##################################################

TUTUM_CONTAINER_PS = '''usage: tutum container ps [-h] [-i IDENTIFIER] [-q]
                          [-s {Init,Stopped,Starting,Running,Stopping,Terminating,Terminated}]

List containers

optional arguments:
  -h, --help            show this help message and exit
  -i IDENTIFIER, --identifier IDENTIFIER
                        container's UUID (either long or short) or name
  -q, --quiet           print only long UUIDs
  -s {Init,Stopped,Starting,Running,Stopping,Terminating,Terminated}, --status {Init,Stopped,Starting,Running,Stopping,Terminating,Terminated}
                        filter containers by status'''

# ##################################################

TUTUM_CONTAINER_START = '''usage: tutum container start [-h] identifier [identifier ...]

Start a container

positional arguments:
  identifier  container's UUID (either long or short) or name

optional arguments:
  -h, --help  show this help message and exit'''

# ##################################################

TUTUM_CONTAINER_STOP = '''usage: tutum container stop [-h] identifier [identifier ...]

Stop a container

positional arguments:
  identifier  container's UUID (either long or short) or name

optional arguments:
  -h, --help  show this help message and exit'''

# ##################################################

TUTUM_CONTAINER_TERMINATE = '''usage: tutum container terminate [-h] identifier [identifier ...]

Terminate a container

positional arguments:
  identifier  container's UUID (either long or short) or name

optional arguments:
  -h, --help  show this help message and exit'''

# ##################################################

TUTUM_SERVICE = '''usage: tutum service [-h]
                     {create,inspect,logs,ps,redeploy,run,scale,set,start,stop,terminate}
                     ...

Service-related operations

optional arguments:
  -h, --help            show this help message and exit

tutum service commands:
  {create,inspect,logs,ps,redeploy,run,scale,set,start,stop,terminate}
    create              Create a new service
    inspect             Get all details from a service
    logs                Get logs from a service
    ps                  List services
    redeploy            Redeploy a running service with a new version/tag
    run                 Create and run a new service
    scale               Scale a running service
    set                 Change service properties
    start               Start a stopped service
    stop                Stop a running service
    terminate           Terminate a service'''

# ##################################################

TUTUM_SERVICE_CREATE = '''usage: tutum service inspect [-h] identifier [identifier ...]

Get all details from a service

positional arguments:
  identifier  service's UUID (either long or short) or name

optional arguments:
  -h, --help  show this help message and exit'''

# ##################################################

TUTUM_SERVICE_INSPECT = '''usage: tutum service inspect [-h] identifier [identifier ...]

Get all details from a service

positional arguments:
  identifier  service's UUID (either long or short) or name

optional arguments:
  -h, --help  show this help message and exit'''

# ##################################################

TUTUM_SERVICE_LOGS = '''usage: tutum service logs [-h] identifier [identifier ...]

Get logs from a service

positional arguments:
  identifier  service's UUID (either long or short) or name

optional arguments:
  -h, --help  show this help message and exit'''


# ##################################################

TUTUM_SERVICE_PS = '''usage: tutum service ps [-h] [-q]
                        [-s {Init,Stopped,Starting,Running,Stopping,Terminating,Terminated,Scaling,Partly running,Not running,Redeploying}]

List services

optional arguments:
  -h, --help            show this help message and exit
  -q, --quiet           print only long UUIDs
  -s {Init,Stopped,Starting,Running,Stopping,Terminating,Terminated,Scaling,Partly running,Not running,Redeploying}, --status {Init,Stopped,Starting,Running,Stopping,Terminating,Terminated,Scaling,Partly running,Not running,Redeploying}
                        filter services by status'''

# ##################################################

TUTUM_SERVICE_REDEPLOY = '''usage: tutum service redeploy [-h] [-t TAG] identifier [identifier ...]

Redeploy a running service with a new version/tag

positional arguments:
  identifier         service's UUID (either long or short) or name

optional arguments:
  -h, --help         show this help message and exit
  -t TAG, --tag TAG  tag of the image to redeploy'''

# ##################################################

TUTUM_SERVICE_RUN = '''usage: tutum service run [-h] [-n NAME] [--cpushares CPUSHARES]
                         [--memory MEMORY] [--privileged]
                         [-t TARGET_NUM_CONTAINERS] [-r RUN_COMMAND]
                         [--entrypoint ENTRYPOINT] [-p PUBLISH]
                         [--expose EXPOSE] [-e ENV] [--tag TAG]
                         [--link-service LINK_SERVICE]
                         [--autorestart {OFF,ON_FAILURE,ALWAYS}]
                         [--autodestroy {OFF,ON_FAILURE,ALWAYS}] [--role ROLE]
                         [--sequential]
                         image

Create and run a new service

positional arguments:
  image                 the name of the image used to deploy this service

optional arguments:
  -h, --help            show this help message and exit
  -n NAME, --name NAME  a human-readable name for the service (default:
                        image_tag without namespace)
  --cpushares CPUSHARES
                        Relative weight for CPU Shares
  --memory MEMORY       RAM memory hard limit in MB
  --privileged          Give extended privileges to this container
  -t TARGET_NUM_CONTAINERS, --target-num-containers TARGET_NUM_CONTAINERS
                        the number of containers to run for this service
                        (default: 1)
  -r RUN_COMMAND, --run-command RUN_COMMAND
                        the command used to start the service containers
                        (default: as defined in the image)
  --entrypoint ENTRYPOINT
                        the command prefix used to start the service
                        containers (default: as defined in the image)
  -p PUBLISH, --publish PUBLISH
                        Publish a container's port to the host. Format:
                        [hostPort:]containerPort[/protocol], i.e. "80:80/tcp"
  --expose EXPOSE       Expose a port from the container without publishing it
                        to your host
  -e ENV, --env ENV     set environment variables i.e. "ENVVAR=foo" (default:
                        as defined in the image, plus any link- or role-
                        generated variables)
  --tag TAG             the tag name being added to the service
  --link-service LINK_SERVICE
                        Add link to another service (name:alias) or
                        (uuid:alias)
  --autorestart {OFF,ON_FAILURE,ALWAYS}
                        whether the containers should be restarted if they
                        stop (default: OFF)
  --autodestroy {OFF,ON_FAILURE,ALWAYS}
                        whether the containers should be terminated if they
                        stop (default: OFF)
  --role ROLE           Tutum API roles to grant the service, i.e. "global"
                        (default: none, possible values: "global")
  --sequential          whether the containers should be launched and scaled
                        sequentially'''

# ##################################################

TUTUM_SERVICE_SCALE = '''usage: tutum service scale [-h]
                           identifier [identifier ...] target-num-containers

Scale a running service

positional arguments:
  identifier            service's UUID (either long or short) or name
  target-num-containers
                        target number of containers to scale this service to

optional arguments:
  -h, --help            show this help message and exit'''

# ##################################################

TUTUM_SERVICE_SET = '''usage: tutum service set [-h] [--autorestart {OFF,ON_FAILURE,ALWAYS}]
                         [--autodestroy {OFF,ON_FAILURE,ALWAYS}]
                         identifier [identifier ...]

Change service properties

positional arguments:
  identifier            service's UUID (either long or short) or name

optional arguments:
  -h, --help            show this help message and exit
  --autorestart {OFF,ON_FAILURE,ALWAYS}
                        whether the containers should be restarted if they
                        stop (default: OFF)
  --autodestroy {OFF,ON_FAILURE,ALWAYS}
                        whether the containers should be terminated if they
                        stop (default: OFF)'''

# ##################################################

TUTUM_SERVICE_START = '''usage: tutum service start [-h] identifier [identifier ...]

Start a stopped service

positional arguments:
  identifier  service's UUID (either long or short) or name

optional arguments:
  -h, --help  show this help message and exit'''

# ##################################################

TUTUM_SERVICE_STOP = '''usage: tutum service stop [-h] identifier [identifier ...]

Stop a running service

positional arguments:
  identifier  service's UUID (either long or short) or name

optional arguments:
  -h, --help  show this help message and exit'''

# ##################################################

TUTUM_SERVICE_TERMINATE = '''usage: tutum service terminate [-h] identifier [identifier ...]

Terminate a service

positional arguments:
  identifier  service's UUID (either long or short) or name

optional arguments:
  -h, --help  show this help message and exit'''

# ##################################################

TUTUM_IMAGE = '''usage: tutum image [-h] {list,register,push,rm,search,update} ...

Image-related operations

optional arguments:
  -h, --help            show this help message and exit

tutum image commands:
  {list,register,push,rm,search,update}
    list                List private images
    register            Register an image from a private repository in Tutum
    push                Push a local image to Tutum private registry
    rm                  Deregister a private image from Tutum
    search              Search for images in the Docker Index
    update              Update a private image'''

# ##################################################

TUTUM_IMAGE_LIST = '''usage: tutum image list [-h] [-q] [-j | -l]

List private images

optional arguments:
  -h, --help        show this help message and exit
  -q, --quiet       print only image names
  -j, --jumpstarts  list jumpstart images
  -l, --linux       list linux images'''

# ##################################################

TUTUM_IMAGE_REGISTER = '''usage: tutum image register [-h] [-d DESCRIPTION] image_name

Register an image from a private repository in Tutum

positional arguments:
  image_name            full image name, i.e. quay.io/tutum/test-repo

optional arguments:
  -h, --help            show this help message and exit
  -d DESCRIPTION, --description DESCRIPTION
                        Image description'''

# ##################################################

TUTUM_IMAGE_PUSH = '''usage: tutum image push [-h] [--public] name

Push a local image to Tutum private registry

positional arguments:
  name        name of the image to push

optional arguments:
  -h, --help  show this help message and exit
  --public    push image to public registry'''

# ##################################################

TUTUM_IMAGE_RM = '''usage: tutum image rm [-h] image_name [image_name ...]

Deregister a private image from Tutum

positional arguments:
  image_name  full image name, i.e. quay.io/tutum/test-repo

optional arguments:
  -h, --help  show this help message and exit'''

# ##################################################

TUTUM_IMAGE_SEARCH = '''usage: tutum image search [-h] query

Search for images in the Docker Index

positional arguments:
  query       query to search

optional arguments:
  -h, --help  show this help message and exit'''

# ##################################################

TUTUM_IMAGE_UPDATE = '''usage: tutum image update [-h] [-u USERNAME] [-p PASSWORD] [-d DESCRIPTION]
                          image_name [image_name ...]

Update a private image

positional arguments:
  image_name            full image name, i.e. quay.io/tutum/test-repo

optional arguments:
  -h, --help            show this help message and exit
  -u USERNAME, --username USERNAME
                        new username to authenticate with the registry
  -p PASSWORD, --password PASSWORD
                        new password to authenticate with the registry
  -d DESCRIPTION, --description DESCRIPTION
                        new image description'''

# ##################################################

TUTUM_LOGIN = '''usage: tutum login [-h]

Login into Tutum

optional arguments:
  -h, --help  show this help message and exit'''

# ##################################################

TUTUM_NODE = '''usage: tutum node [-h] {byo,inspect,list,rm,upgrade} ...

Node-related operations

optional arguments:
  -h, --help            show this help message and exit

tutum node commands:
  {byo,inspect,list,rm,upgrade}
    byo                 Instructions on how to Bring Your Own server to Tutum
    inspect             Inspect a node
    list                List nodes
    rm                  Remove a node
    upgrade             Upgrade docker daemon on the node'''

# ##################################################

TUTUM_NODE_INSPECT = '''usage: tutum node inspect [-h] identifier [identifier ...]

Inspect a node

positional arguments:
  identifier  node's UUID (either long or short)

optional arguments:
  -h, --help  show this help message and exit'''

# ##################################################

TUTUM_NODE_LIST = '''usage: tutum node list [-h] [-q]

List nodes

optional arguments:
  -h, --help   show this help message and exit
  -q, --quiet  print only node uuid'''

# ##################################################

TUTUM_NODE_RM = '''usage: tutum node rm [-h] identifier [identifier ...]

Remove a container

positional arguments:
  identifier  node's UUID (either long or short)

optional arguments:
  -h, --help  show this help message and exit'''

# ##################################################

TUTUM_NODE_UPGRADE = '''usage: tutum node upgrade [-h] identifier [identifier ...]

Upgrade docker daemon to the latest version on the node

positional arguments:
  identifier  node's UUID (either long or short)

optional arguments:
  -h, --help  show this help message and exit'''

# ##################################################

TUTUM_NODECLUSTER = '''usage: tutum nodecluster [-h]

                         {create,inspect,list,rm,scale,provider,region,nodetype}
                         ...

NodeCluster-related operations

optional arguments:
  -h, --help            show this help message and exit

tutum node commands:
  {create,inspect,list,rm,scale,provider,region,nodetype}
    create              Create a nodecluster
    inspect             Inspect a nodecluster
    list                List node clusters
    rm                  Remove node clusters
    scale               Scale a running node cluster
    provider            Show all available infrastructure providers
    region              Show all available regions
    nodetype            Show all available types'''

# ##################################################

TUTUM_NODECLUSTER_CREATE = '''usage: tutum nodecluster create [-h] [-t TARGET_NUM_NODES]
                                name provider region nodetype

Create a nodecluster

positional arguments:
  name                  name of the node cluster to create
  provider              name of the provider
  region                name of the region
  nodetype              name of the node type

optional arguments:
  -h, --help            show this help message and exit
  -t TARGET_NUM_NODES, --target-num-nodes TARGET_NUM_NODES
                        the target number of nodes to run for this cluster
                        (default: 1)'''

# ##################################################

TUTUM_NODECLUSTER_INSPECT = '''usage: tutum nodecluster inspect [-h] identifier [identifier ...]

Inspect a nodecluster

positional arguments:
  identifier  node's UUID (either long or short)

optional arguments:
  -h, --help  show this help message and exit'''

# ##################################################

TUTUM_NODECLUSTER_LIST = '''usage: tutum nodecluster list [-h] [-q]

List node clusters

optional arguments:
  -h, --help   show this help message and exit
  -q, --quiet  print only node uuid'''

# ##################################################

TUTUM_NODECLUSTER_RM = '''usage: tutum nodecluster rm [-h] identifier [identifier ...]

Remove node clusters

positional arguments:
  identifier  node's UUID (either long or short)

optional arguments:
  -h, --help  show this help message and exit'''

# ##################################################

TUTUM_NODECLUSTER_SCALE = '''usage: tutum nodecluster scale [-h]
                               identifier [identifier ...] target-num-nodes

Scale a running node cluster

positional arguments:
  identifier        node cluster's UUID (either long or short) or name
  target-num-nodes  target number of nodes to scale this node cluster to

optional arguments:
  -h, --help        show this help message and exit'''

# ##################################################

TUTUM_NODECLUSTER_PROVIDER = '''usage: tutum nodecluster provider [-h] [-q]

Show all available infrastructure providers

optional arguments:
  -h, --help   show this help message and exit
  -q, --quiet  print only provider name'''

# ##################################################

TUTUM_NODECLUSTER_REGION = '''usage: tutum nodecluster region [-h] [-p PROVIDER]

optional arguments:
  -h, --help            show this help message and exit
  -p PROVIDER, --provider PROVIDER
                        filtered by provider name (e.g. digitalocean)'''

# ##################################################

TUTUM_NODECLUSTER_NODETYPE = '''usage: tutum nodecluster nodetype [-h] [-p PROVIDER] [-r REGION]

optional arguments:
  -h, --help            show this help message and exit
  -p PROVIDER, --provider PROVIDER
                        filtered by provider name (e.g. digitalocean)
  -r REGION, --region REGION
                        filtered by region name (e.g. ams1)'''

# ##################################################

TUTUM_TAG = '''usage: tutum tag [-h] {add,list,rm,set} ...

Tag-related operations

optional arguments:
  -h, --help         show this help message and exit

tutum tag commands:
  {add,list,rm,set}
    add              Add tags to services, nodes or nodeclusters
    list             List all tags associated with services, nodes or
                     nodeclusters
    rm               Remove tags from services, nodes or nodeclusters
    set              Set tags from services, nodes or nodeclusters'''

# ##################################################

TUTUM_TAG_ADD = '''usage: tutum tag add [-h] -t TAG identifier [identifier ...]

Add tags to services, nodes or nodeclusters

positional arguments:
  identifier         UUID or name of services, nodes or nodeclusters

optional arguments:
  -h, --help         show this help message and exit
  -t TAG, --tag TAG  name of the tag
'''

# ##################################################

TUTUM_TAG_LIST = '''usage: tutum tag list [-h] [-q] identifier [identifier ...]

List all tags associated with services, nodes or nodeclusters

positional arguments:
  identifier   UUID or name of services, nodes or nodeclusters

optional arguments:
  -h, --help   show this help message and exit
  -q, --quiet  print only tag names'''

# ##################################################

TUTUM_TAG_RM = '''usage: tutum tag rm [-h] -t TAG identifier [identifier ...]

Remove tags from services, nodes or nodeclusters

positional arguments:
  identifier         UUID or name of services, nodes or nodeclusters

optional arguments:
  -h, --help         show this help message and exit
  -t TAG, --tag TAG  name of the tag'''

# ##################################################

TUTUM_TAG_SET = '''usage: tutum tag set [-h] -t TAG identifier [identifier ...]

Set tags from services, nodes or nodeclusters. This will remove all the
existing tags

positional arguments:
  identifier         UUID or name of services, nodes or nodeclusters

optional arguments:
  -h, --help         show this help message and exit
  -t TAG, --tag TAG  name of the tag'''