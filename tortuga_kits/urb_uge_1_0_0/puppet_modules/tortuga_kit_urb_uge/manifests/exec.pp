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


class tortuga_kit_urb_uge::master (
  String $uge_user = $tortuga_kit_urb_uge::config::sge_user,
  String $uge_group = $tortuga_kit_urb_uge::config::sge_group,
  String $sge_root = $tortuga_kit_urb_uge::config::sge_root,
  String $sge_cell = $tortuga_kit_urb_uge::config::sge_cell,
  String $urb_dist_file = $tortuga_kit_urb_uge::config::urb_dist_file,
#  String $uge_manager_user = $tortuga_kit_urb_uge::config::uge_manager_user,
  String $python = $tortuga_kit_urb_uge::config::python,
) inherits tortuga_kit_urb_uge::config {
  $uge_manager_user = $uge_user
  $urb_parent_dir = "${sge_root}/${sge_cell}"
  $urb_root = "${urb_parent_dir}/" + basename($urb_dist_file, '.tar.gz')

  package { "libev":
    ensure  => "installed",
  }

  package { "libuuid":
    ensure  => "installed",
  }
 
  package { "zlib":
    ensure  => "installed"
  }

  exec { "is_uge_manager":
    command => "/bin/bash -c '. ${sge_root}/${sge_cell}/common/settings.sh && qconf -sm | grep $uge_manager_user'",
    user    => $uge_manager_user
  }

  exec { "urb_exec_install":
    cwd     => $urb_root,
    command => "/bin/bash -c '. ${uge_root}/${uge_cell}/common/settings.sh && cd $urb_root; ${urb_root}/inst_urb --uge-manager ${uge_manager_user} --usedefaults --set-python ${python} --remote --modules virtualenv,urb'",
#    user    => $uge_manager_user,
    unless  => "/usr/bin/test -d ${urb_root}/venv/`${python} -c \"import platform; import sys; print('%s/%s' % (platform.platform(),'_'.join([str(e) for e in sys.version_info])))\"`",
    require => [Package['libev'], Package['libuuid'], Package['zlib'], Exec["is_uge_manager"]]
  }
}


