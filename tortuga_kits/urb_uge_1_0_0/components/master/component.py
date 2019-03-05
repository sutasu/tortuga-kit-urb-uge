# Copyright 2008-2018 Univa Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import os
#from logging import getLogger
from typing import Any, Dict, List, Optional

from tortuga.kit.installer import ComponentInstallerBase, KitInstallerBase
from tortuga.logging import KIT_NAMESPACE
from tortuga.exceptions.configurationError import ConfigurationError
#from tortuga.kit.registry import get_all_kit_installers
from tortuga.db.softwareProfilesDbHandler import SoftwareProfilesDbHandler
from tortuga.os_utility.tortugaSubprocess import executeCommand
from ..base import URB_PUPPET_MODULE_PATH, URB_VERSION, UrbComponentInstaller

#
# All component installer classes must be named ComponentInstaller in order
# to be automatically detected by the kits component detection logic.
#


class ComponentInstaller(UrbComponentInstaller):
    name = 'master'
    version = URB_VERSION
    os_list = [
        {'family': 'rhel', 'version': '7', 'arch': 'x86_64'},
    ]
    #
    # If this component is only designed to be enabled on installer nodes,
    # set this to True.
    #
    installer_only = False

    #
    # If this component is only designed to be enabled on compute nodes,
    # set this to True.
    #
    compute_only = False

    def __init__(self, kit_installer):
        super().__init__(kit_installer)    
        self._logger = logging.getLogger('{}.{}'.format(KIT_NAMESPACE,
                                                        kit_installer.name))
        #self.kit_installer
        self._logger.info('__init__ urb master component')


    def _is_component_enabled(self, software_profile_name: str) -> bool:
        """
        Returns True if this component is enabled on the specified software
        profile.
        """

        try:
            swprofiles = \
                SoftwareProfilesDbHandler().\
                get_software_profiles_with_component(
                    self.session, 'urb_uge', self.name)

            return software_profile_name in \
                [swprofile.name for swprofile in swprofiles]
        except ResourceNotFound:
            return False



    def action_get_puppet_args(self, db_software_profile,
                               db_hardware_profile,
                               *args, **kwargs):
        self._logger.debug('urb master: action_get_puppet_args')
        params = {}
        clusters = self.get_cluster_by_swprofilename(db_software_profile.name)
        self._logger.debug('urb master: action_get_puppet_args: clusters={}'.format(clusters))
        cluster = self._normalize_cluster_config_dict(clusters[0])
        self._logger.debug('urb master: action_get_puppet_args: cluster={}'.format(cluster))
        params['sge_root'] = cluster['settings']['sge_root']
        params['sge_cell'] = cluster['settings']['cell_name']
        params['uge_user'] = cluster['settings']['uge_user']
        params['uge_group'] = cluster['settings']['uge_group']
        return params

    def action_pre_enable(self, software_profile_name, *args, **kwargs):
        """
        This hook is invoked on the installer prior to enabling the
        component on a software profile.

        :param software_profile_name: the name of the software profile on
                                      which the component is being enabled.
        :param args:
        :param kwargs:

        """
        pass

    def action_enable(self, software_profile_name, *args, **kwargs):
        """
        This hook is invoked on the installer when the component is enabled
        on a software profile.

        :param software_profile_name: the name of the software profile on
                                      which the component is being enabled.
        :param args:
        :param kwargs:

        """
        self._logger.debug('urb_uge: action_enable')

    def action_post_enable(self, software_profile_name, *args, **kwargs):
        """
        This hook is invoked on the installer after the component has been
        enabled on a software profile.

        :param software_profile_name: the name of the software profile on
                                      which the component is being enabled.
        :param args:
        :param kwargs:

        """
        pass

    def action_pre_disable(self, software_profile_name, *args, **kwargs):
        """
        This hook is invoked on the installer prior to disabling it on a
        software profile.

        :param software_profile_name: the name of the software profile on
                                      which the component is being disabled.
        :param args:
        :param kwargs:

        """
        pass

    def action_disable(self, software_profile_name, *args, **kwargs):
        """
        This hook is invoked on the installer prior to disabling it on a
        software profile.

        :param software_profile_name: the name of the software profile on
                                      which the component is being disabled.
        :param args:
        :param kwargs:

        """
        pass

    def action_post_disable(self, software_profile_name, *args, **kwargs):
        """
        This hook is invoked on the installer after disabling it on a
        software profile.

        :param software_profile_name: the name of the software profile on
                                      which the component was disabled.
        :param args:
        :param kwargs:

        """
        pass

    def action_pre_add_host(self, hardware_profile, software_profile,
                            hostname, ip, *args, **kwargs):
        """
        This hook is invoked on the installer prior to adding a host with
        a software profile that has this component enabled.

        :param hardware_profile: the hardware profile of the host being added
        :param software_profile: the software profile of the host being added
        :param hostname:         the hostname of the host being added
        :param ip:               the ip address of the host being added
        :param args:
        :param kwargs:

        """
        pass

    def action_add_host(self, hardware_profile_name, software_profile_name,
                        nodes, *args, **kwargs):
        """
        This hook is invoked on the installer when adding a host with
        a software profile that has this component enabled.

        :param hardware_profile_name: the name of the hosts hardware profile
        :param software_profile_name: the name of the hosts software profile
        :param nodes:                 the nodes (hosts) added
        :param args:
        :param kwargs:

        """
        self._logger.debug('urb_uge: action_add_host, nodes='.format(nodes))

    def action_pre_delete_host(self, hardware_profile, software_profile,
                               nodes, *args, **kwargs):
        """
        This hook is invoked on the installer piror to deleting a host with
        a software profile that has this component enabled.

        :param hardware_profile: the hardware profile
        :param software_profile: the software profile
        :param nodes:            the nodes (hosts) deleted
        :param args:
        :param kwargs:

        """
        pass

    def action_delete_host(self, hardware_profile_name, software_profile_name,
                           nodes, *args, **kwargs):
        """
        This hook is invoked on the installer when deleting a host with
        a software profile that has this component enabled.

        :param hardware_profile_name: the name of the hosts hardware profile
        :param software_profile_name: the name of the hosts software profile
        :param nodes:                 the nodes (hosts) deleted
        :param args:
        :param kwargs:

        """
        pass
