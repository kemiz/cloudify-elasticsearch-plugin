# Cloudify Imports
from cloudify import ctx
from cloudify import exceptions
from cloudify.decorators import operation


@operation
def configure(elasticsearch_config, **_):

    raise exceptions.NonRecoverableError('Not Implemented')
