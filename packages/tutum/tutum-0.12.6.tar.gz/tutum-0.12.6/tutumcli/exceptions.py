class NonUniqueIdentifier(RuntimeError):
    pass


class ObjectNotFound(RuntimeError):
    pass


class BadParameter(RuntimeError):
    pass


class DockerNotFound(RuntimeError):
    pass


class PublicImageNotFound(RuntimeError):
    pass


class StreamOutputError(Exception):
    pass


class InternalError(RuntimeError):
    pass