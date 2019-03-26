 
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
  String $uge_user = $tortuga_kit_urb_uge::config::uge_user,
  String $uge_group = $tortuga_kit_urb_uge::config::uge_group,
  String $sge_root = $tortuga_kit_urb_uge::config::sge_root,
  String $sge_cell = $tortuga_kit_urb_uge::config::sge_cell,
  String $urb_dist_file = $tortuga_kit_urb_uge::config::urb_dist_file,
#  String $uge_manager_user = $tortuga_kit_urb_uge::config::uge_manager_user,
  String $python = $tortuga_kit_urb_uge::config::python,
  String $redis_port = $tortuga_kit_urb_uge::config::redis_port,
  Boolean $no_mongo = $tortuga_kit_urb_uge::config::no_mongo,
#  Booleal $retrieve_from_web = $tortuga_kit_urb_uge::config::retrieve_from_web,
) inherits tortuga_kit_urb_uge::config {
  $uge_manager_user = $uge_user
#  if $retrieve_from_web {
#    # Set location of distribution tarballs for installation
#    $unisight_dist_srcdir = '/opt/dist'
#    $unisight_tarball_url = "http://${::primary_installer_hostname}:8008/urb/${urb_dist_file}"
#  } else {
#    # Set location of distribution tarballs for installation
#    # These files are put here during the kit enable component workflow
#    $unisight_dist_srcdir = '/opt/tortuga/www_int/unisight'
#  }

  $urb_parent_dir = "${sge_root}/${sge_cell}"
  file { "${urb_parent_dir}/${urb_dist_file}":
    ensure => file,
    source => "puppet:///modules/tortuga_kit_urb_uge/${urb_dist_file}",
  }
#  $urb_root = join([$urb_parent_dir, $urb_dist.match([/.*(\/urb-[0-9]*\.[0-9]*\.[0-9]*)\.tar\.gz/,1])[1]])
#  tortuga_kit_urb_uge::install_tarball { $urb_tarball:
#    destdir  => $urb_root,
#    testdir  => "${urb_root}/etc",
##    user     => $uge_user,
#  }

  $urb_base = basename($urb_dist_file, '.tar.gz')
  $urb_root = "${urb_parent_dir}/${urb_base}"
#  archive { $urb_dist_file:
#    source => "puppet:///modules/tortuga_kit_urb_uge/${urb_dist_file}",
#    extract => true,
#    extract_path => $urb_parent_dir,
#    creates => "${urb_root}/etc",
#    require => Exec['is_uge_manager'],
#  }
  
  if $no_mongo {
    $no_modules = "--no-mongo --no-webui"
  } else {
    $no_modules = ""
  }
  
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

#  exec { "is_sudoer":
#    command => "/usr/bin/sudo -k && /usr/bin/sudo -n echo",
#    user    => $uge_manager_user
#  }

#  file { $urb_root:
#    ensure => "directory",
#    owner =>  $uge_manager_user,
#    require => [Exec["is_uge_manager"], Exec["is_sudoer"]]
#  }

#  exec { "change_group":
#    command => "/usr/bin/chown $uge_manager_user.$(/usr/bin/id -gn $uge_manager_user) $urb_root",
#    require => File[$urb_root]
#  }

  exec { "urb_extract":
    path    => ['/bin', '/usr/bin'],
    cwd     => $urb_parent_dir,
    command => "tar zxf ${urb_dist_file} && chown -R root.root ${urb_root}",
    creates => "${urb_root}/etc",
#    user    => $user,
    require => File["${urb_parent_dir}/${urb_dist_file}"]
  }

#  exec { "urb_extract":
#    cwd     => $urb_parent_dir,
#    command => "/usr/bin/tar xzf $urb_dist && /usr/bin/chown -R $uge_manager_user.$(/usr/bin/id -gn) $urb_root/*",
#    user    => $uge_manager_user,
#    creates => "$urb_root/etc",
#    require => Exec["change_group"]
#  }

  exec { "urb_master_install":
    cwd     => $urb_root,
    command => "/bin/bash -c '. ${sge_root}/${sge_cell}/common/settings.sh && cd $urb_root; ${urb_root}/inst_urb --uge-manager ${uge_manager_user} --usedefaults ${no_modules} --set-python ${python} --redis-port ${redis_port} --skip-exec-hosts'",
    unless  => "/bin/pgrep -fc 'urb-service'",
#    user    => $uge_manager_user,
#    logoutput => true,
    require => [Package["libev"], Package["libuuid"], Package["zlib"], Exec["urb_extract"], Exec["is_uge_manager"]]
#    require => [Package["libev"], Package["libuuid"], Package["zlib"], Exec["urb_extract"]]
  }

  exec { "add_uge_urb_complex":
    command => "/bin/bash -c '. ${sge_root}/${sge_cell}/common/settings.sh && qconf -sc > /tmp/urb_sc.tmp; echo \"urb urb BOOL == YES NO FALSE 0 NO\" >> /tmp/urb_sc.tmp; qconf -Mc /tmp/urb_sc.tmp'",
    user    => $uge_manager_user,
    unless => "/bin/bash -c '. ${sge_root}/${sge_cell}/common/settings.sh && qconf -sc | grep urb'",
    require => Exec["urb_master_install"]
  }

  exec { "modify_urb_job_class":
    command => "/bin/bash -c '. ${sge_root}/${sge_cell}/common/settings.sh && qconf -sjc URBDefault > /tmp/urb_jc.tmp; sed -ie \"s/^l_hard[ ]*.*$/l_hard urb=TRUE/\"  /tmp/urb_jc.tmp; qconf -Mjc /tmp/urb_jc.tmp'",
    user    => $uge_manager_user,
    unless => "/bin/bash -c '. ${sge_root}/${sge_cell}/common/settings.sh && qconf -sjc URBDefault | grep urb=TRUE'",
    require => Exec["add_uge_urb_complex"]
  }

}
