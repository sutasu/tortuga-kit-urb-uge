# tortuga-kit-urb-uge

## Overview

This repository contains the requisite files to build a kit to enable support
to install and manage URB (Universal Resource Broker) with Univa Grid Engine as a backend scheduler
on nodes in a [Tortuga][] environment.

Please see [urb-core](https://github.com/UnivaCorporation/urb-core), [urb-uge](https://github.com/UnivaCorporation/urb-uge), [urb-k8s](https://github.com/UnivaCorporation/urb-k8s) for more details on Universal Resource Broker.


## Building the kit

Change to subdirectory containing cloned Git repository.
Copy URB release archive from [urb-uge project](https://github.com/UnivaCorporation/urb-uge/releases) to
`tortuga_kits/urb_uge_1_0_0/puppet_modules/tortuga_kit_urb_uge/files` directory. Make sure that proper version
of the release archive is used in [params.pp](tortuga_kits/urb_uge_1_0_0/puppet_modules/tortuga_kit_urb_uge/manifests/params.pp)

Run `build-kit`.

`build-kit` is provided by the `tortuga-core` package in the [Tortuga][] source.
Be sure you have activated the tortuga virtual environment as suggested in the [Tortuga build instructions](https://github.com/UnivaCorporation/tortuga#build-instructions) before executing `build-kit`.

## Installation

Install the kit:

```shell
install-kit kit-urb_uge-*.tar.bz2
```

## Usage

Enable URB `master` kit component (typically on Installer software profile) to install URB service:

```shell
enable-component --software-profile Installer urb_uge master
puppet agent -t
```

Enable URB `exec` kit component on existing Univa Grid Engine compute software profile:

```shell
enable-component --software-profile Compute urb_uge exec
```

Add compute node[s] to the cluster (on existing Univa Grid Engine compute software and hardware profiles):

```shell
add-nodes --count 2 --software-profile Compute --hardware-profile AWS
```

Wait for the new compute nodes to be fully provisioned and ready to accept Grid Engine jobs.

Run URB example framework:

```shell
. $SGE_ROOT/$SGE_CELL/common/settings.sh
$URB_ROOT/share/examples/frameworks/linux-x86_64/example_framework.test
```

See `$URB_ROOT/share/doc/Universal_Resource_Broker_Manual.pdf` (also can be obtained from
[urb-uge project releases](https://github.com/UnivaCorporation/urb-uge/releases)) for full URB documentation including
details on how to run [Mesos](http://mesos.apache.org) compatible frameworks ([Spark](https://spark.apache.org), [Chronos](https://mesos.github.io/chronos), etc.).


See the [Tortuga Installation and Administration Guide](https://github.com/UnivaCorporation/tortuga/blob/master/doc/tortuga-7-admin-guide.md) for Tortuga configuration
details.


[Tortuga]: https://github.com/UnivaCorporation/tortuga "Tortuga"
