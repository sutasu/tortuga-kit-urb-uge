 
#############################################################################
#
# This code is the Property, a Trade Secret and the Confidential Information
# of Univa Corporation.
#
# Copyright 2008-2018 Univa Corporation. All Rights Reserved. Access is Restricted.
#
# It is provided to you under the terms of the
# Univa Term Software License Agreement.
#
# If you have any questions, please contact our Support Department.
#
# http://www.univa.com
#
#############################################################################

import logging
import socket
from typing import Iterator, List, Optional

from tortuga.db.models.node import Node
from tortuga.db.nodesDbHandler import NodesDbHandler
from tortuga.db.softwareProfileDbApi import SoftwareProfileDbApi
from tortuga.db.softwareProfilesDbHandler import SoftwareProfilesDbHandler
from tortuga.exceptions.configurationError import ConfigurationError
from tortuga.exceptions.resourceNotFound import ResourceNotFound
from tortuga.kit.installer import ComponentInstallerBase
from tortuga.kit.installer import KitInstallerBase
from tortuga.kit.registry import get_all_kit_installers
from tortuga.logging import KIT_NAMESPACE
from tortuga.os_utility import osUtility
from tortuga.utility.helper import str2bool

#from ..web_service.uge_mgmt_api import Uge_mgmt_api


URB_VERSION = '3.1.1'

URB_PUPPET_MODULE_PATH = ('/etc/puppetlabs/code/environments/production'
                          '/modules/tortuga_kit_urb_uge')


class UrbComponentInstaller(ComponentInstallerBase):
    version = URB_VERSION
    os_list = [
        {'family': 'rhel', 'version': '7', 'arch': 'x86_64'},
    ]

    #
    # List of puppet arguments, taken from tortuga_kit_uge::config
    #
    allowed_puppet_args: List[str] = [
        'cluster_name',
        'manage_user',
        'managed_install',
        'sge_qmaster_port',
        'sge_execd_port',
        'shared_install',
        'uge_gid',
        'uge_group',
        'uge_user',
        'uge_uid',
    ]

    def __init__(self, kit_installer):
        super().__init__(kit_installer)
        os_object_factory = osUtility.getOsObjectFactory()
        self._os_service_manager = os_object_factory.getOsServiceManager()
        self._software_profile_db_api = SoftwareProfileDbApi()
#        self._uge_mgmt_api = Uge_mgmt_api()
        self._node_api = NodesDbHandler()

        self.installer_hostname = socket.getfqdn()

        self._logger = logging.getLogger(
            '{}.{}'.format(KIT_NAMESPACE, kit_installer.name))

    def __get_uge_kit(self) -> Optional[KitInstallerBase]:
        """
        Return KitInstallerBase for first found UGE kit
        """
        for kit_installer in get_all_kit_installers():
            if kit_installer.name == 'uge':
                return kit_installer
        return None

    def filter_puppet_args(self, args: dict) -> dict:
        filtered_args: dict = {}
        for k, v in args.items():
            if k in self.allowed_puppet_args:
                filtered_args[k] = v
        return filtered_args

    def _normalize_cluster_config_dict(self, cluster) -> dict:
        cluster_configuration = {}

        # Convert cluster software profiles to human-readable
        cluster_configuration['qmaster_swprofiles'] = \
            [swprofile['name'] for swprofile in cluster['qmaster_swprofiles']]

        cluster_configuration['execd_swprofiles'] = \
            [swprofile['name'] for swprofile in cluster['execd_swprofiles']]

        cluster_configuration['submithost_swprofiles'] = \
            [swprofile['name']
             for swprofile in cluster['submithost_swprofiles']]

        settings = {}

        # 'name' is a reserved keyword in Puppet, so we change it to
        # 'cell_name'
        settings['cell_name'] = cluster['name']

        for setting in cluster['settings']:
            settings[setting['key']] = setting['value']

        # Use global default, if undefined
        if 'sge_root' not in settings:
            settings['sge_root'] = self.kit_installer.DEFAULT_UGE_ROOT

        if 'manage_nfs' in settings:
            settings['manage_nfs'] = \
                settings['manage_nfs'].lower() == 'true'

        if 'tarballs' in settings:
            settings['tarballs'] = {
            'common': [self.kit_installer.tarballs['common']],
            'binaries': self.kit_installer.tarballs['binaries'],
        }

        # Normalize values
        if 'uge_uid' in settings:
            settings['uge_uid'] = int(settings['uge_uid'])

        if 'uge_gid' in settings:
            settings['uge_gid'] = int(settings['uge_gid'])

        cluster_configuration['settings'] = settings
        self._logger.debug('normalized cluster config: {}'.format(cluster_configuration))
        return cluster_configuration

    def get_cluster_by_swprofilename(self, name: str) -> dict:
        """
        Raises:
            ConfigurationError
        """

        # check if UGE is installed
        Uge_kit_installer = self.__get_uge_kit()
        if Uge_kit_installer is None:
            self._logger.info('Cannot get uge kit installer')
            return

        uge_mgmt_api = Uge_kit_installer.get_uge_mgmt_api()
        clusters = uge_mgmt_api.get(self.session, swprofilename=name)
        self._logger.info('clusters: {}'.format(clusters))
        if not clusters:
            raise ConfigurationError(
                'Software profile [{}] is not part of a UGE cluster'.format(
                    name))
        return clusters
