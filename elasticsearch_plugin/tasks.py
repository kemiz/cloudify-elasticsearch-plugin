########
# Copyright (c) 2015 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#    * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the License.

# Built in Imports
import requests
import platform
import tempfile

# Cloudify Imports
from utils import run
from cloudify import ctx
from cloudify import exceptions
from cloudify.decorators import operation
from constants import (
    ELASTIC_CO_BASE_URL,
    DEFAULT_DEB_URL,
    DEFAULT_RPM_URL,
    INSTALLED_UBUNTU,
    INSTALLED_CENTOS
)


# @operation
# def configure(conf, **_):
#     """ Configure Elasticsearch """
# TODO: Add passing of configuration file


def generate_static_config(template_conf):

    ctx.logger.info('Generating static conf from template')

    raise NotImplementedError


def upload_static_config(static_conf, conf_path):
    """ Upload the static config to the service. """

    ctx.logger.info('Copying config to {0}'.format(conf_path))

    try:
        downloaded_file = \
            ctx.download_resource(static_conf, tempfile.mktemp())
    except Exception as e:
        raise exceptions.NonRecoverableError(
            'failed to download. Error: {0}.'.format(str(e)))

    run('sudo cp {0} {1}'.format(downloaded_file, conf_path))


@operation
def start(command, **_):
    """starts logstash daemon"""

    ctx.logger.debug('Attempting to start Elasticsearch...')

    output = run(command)

    if output.returncode != 0:
        raise exceptions.NonRecoverableError(
            'Unable to start Elasticsearch: {0}'.format(output))


@operation
def stop(command, **_):
    """stops Elasticsearch daemon"""

    ctx.logger.debug('Attempting to stop Elasticsearch...')

    output = run(command)

    if output.returncode != 0:
        raise exceptions.NonRecoverableError(
            'Unable to stop Elasticsearch: {0}'.format(output))


@operation
def install(install_java, package_url, **_):
    """ Installs Elasticsearch """

    ctx.logger.info('Attempting to install Elasticsearch...')
    distro = platform.linux_distribution(full_distribution_name=False)
    ctx.logger.info(distro)
    ctx.logger.info(package_url)
    distro_lower = [x.lower() for x in distro]

    if install_java is True:
        _install_java(distro_lower)

    _install(distro_lower, package_url)

def _install_java(platform):
    """ installs Java """

    if 'ubuntu' in platform:
        install_command = 'sudo apt-get -qq --no-upgrade install openjdk-7-jdk'
    elif 'centos' in platform:
        install_command = 'sudo yum -y -q install java-1.7.0-openjdk'
    else:
        raise exceptions.NonRecoverableError('Only Centos and Ubuntu supported.')

    run(install_command)

def _install(platform, url):
    """ installs Elasticsearch from package """

    _, package_file = tempfile.mkstemp()

    if 'ubuntu' in platform:
        install_command = 'sudo dpkg -i {0}'.format(package_file)
        # if 'install' in run(INSTALLED_UBUNTU):
        #     ctx.logger.info('Elasticsearch already installed.')
        #     return
        if not url:
            url = ELASTIC_CO_BASE_URL \
                + DEFAULT_DEB_URL
    elif 'centos' in platform:
        install_command = 'sudo yum install -y {0}'.format(package_file)
        # if 'not installed' not in run(INSTALLED_CENTOS):
        #     ctx.logger.info('Elasticsearch already installed.')
        #     return
        if not url:
            url = ELASTIC_CO_BASE_URL \
                + DEFAULT_RPM_URL
    else:
        raise exceptions.NonRecoverableError(
            'Only Centos and Ubuntu supported.')

    _download_package(package_file, url)

    run(install_command)


def _download_package(package_file, url):
    """ Downloads package from url to tempfile """

    ctx.logger.debug('Downloading: {0}'.format(url))
    package = requests.get(url, stream=True)

    with open(package_file, 'wb') as f:
        for chunk in package.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                f.flush()
