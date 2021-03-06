# Copyright (c) 2017 StackHPC Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import json
import sys

from cliff.command import Command

from java_role import ansible
from java_role import lordoftheflies_ansible
from java_role import utils
from java_role import vault


def _build_playbook_list(*playbooks):
    """Return a list of names of playbook files given their basenames."""
    return ["ansible/%s.yml" % playbook for playbook in playbooks]


class VaultMixin(object):
    """Mixin class for commands requiring Ansible vault."""

    def get_parser(self, prog_name):
        parser = super(VaultMixin, self).get_parser(prog_name)
        group = parser.add_argument_group("Ansible vault")
        vault.add_args(group)
        return parser


class JavaRoleAnsibleMixin(object):
    """Mixin class for commands running JavaRole Ansible playbooks."""

    def get_parser(self, prog_name):
        parser = super(JavaRoleAnsibleMixin, self).get_parser(prog_name)
        group = parser.add_argument_group("JavaRole Ansible")
        self.add_java_role_ansible_args(group)
        return parser

    def add_java_role_ansible_args(self, group):
        ansible.add_args(group)

    def _get_verbosity_args(self):
        """Add quietness and verbosity level arguments."""
        # Cliff's default verbosity level is 1, 0 means quiet.
        verbosity_args = {}
        if self.app.options.verbose_level:
            ansible_verbose_level = self.app.options.verbose_level - 1
            verbosity_args["verbose_level"] = ansible_verbose_level
        else:
            verbosity_args["quiet"] = True
        return verbosity_args

    def run_java_role_playbooks(self, *args, **kwargs):
        kwargs.update(self._get_verbosity_args())
        return ansible.run_playbooks(*args, **kwargs)

    def run_java_role_playbook(self, *args, **kwargs):
        kwargs.update(self._get_verbosity_args())
        return ansible.run_playbook(*args, **kwargs)

    def run_java_role_config_dump(self, *args, **kwargs):
        kwargs.update(self._get_verbosity_args())
        return ansible.config_dump(*args, **kwargs)


class KollaAnsibleMixin(object):
    """Mixin class for commands running Kolla Ansible."""

    def get_parser(self, prog_name):
        parser = super(KollaAnsibleMixin, self).get_parser(prog_name)
        group = parser.add_argument_group("Kolla Ansible")
        self.add_lordoftheflies_ansible_args(group)
        return parser

    def add_lordoftheflies_ansible_args(self, group):
        lordoftheflies_ansible.add_args(group)

    def _get_verbosity_args(self):
        """Add quietness and verbosity level arguments."""
        # Cliff's default verbosity level is 1, 0 means quiet.
        verbosity_args = {}
        if self.app.options.verbose_level:
            ansible_verbose_level = self.app.options.verbose_level - 1
            verbosity_args["verbose_level"] = ansible_verbose_level
        else:
            verbosity_args["quiet"] = True
        return verbosity_args

    def run_lordoftheflies_ansible(self, *args, **kwargs):
        kwargs.update(self._get_verbosity_args())
        return lordoftheflies_ansible.run(*args, **kwargs)

    def run_lordoftheflies_ansible_overcloud(self, *args, **kwargs):
        kwargs.update(self._get_verbosity_args())
        return lordoftheflies_ansible.run_overcloud(*args, **kwargs)

    def run_lordoftheflies_ansible_seed(self, *args, **kwargs):
        kwargs.update(self._get_verbosity_args())
        return lordoftheflies_ansible.run_seed(*args, **kwargs)


class ControlHostBootstrap(JavaRoleAnsibleMixin, VaultMixin, Command):
    """Bootstrap the JavaRole control environment.

    * Downloads and installs Ansible roles from Galaxy.
    * Generates an SSH key for the ansible control host, if one does not exist.
    * Installs lordoftheflies-ansible on the ansible control host.
    """

    def take_action(self, parsed_args):
        self.app.LOG.debug("Bootstrapping JavaRole control host")
        utils.galaxy_install("requirements.yml", "ansible/roles")
        playbooks = _build_playbook_list("bootstrap")
        self.run_java_role_playbooks(parsed_args, playbooks)
        playbooks = _build_playbook_list("lordoftheflies-ansible")
        self.run_java_role_playbooks(parsed_args, playbooks, tags="install")


class ControlHostUpgrade(JavaRoleAnsibleMixin, VaultMixin, Command):
    """Upgrade the JavaRole control environment.

    * Downloads and installs updated Ansible roles from Galaxy.
    * Generates an SSH key for the ansible control host, if one does not exist.
    * Updates lordoftheflies-ansible on the ansible control host.
    """

    def take_action(self, parsed_args):
        self.app.LOG.debug("Upgrading JavaRole control host")
        # Use force to upgrade roles.
        utils.galaxy_install("requirements.yml", "ansible/roles",
                             force=True)
        playbooks = _build_playbook_list("bootstrap")
        self.run_java_role_playbooks(parsed_args, playbooks)
        playbooks = _build_playbook_list("lordoftheflies-ansible")
        self.run_java_role_playbooks(parsed_args, playbooks, tags="install")


class ConfigurationDump(JavaRoleAnsibleMixin, VaultMixin, Command):
    """Dump JavaRole configuration.

    Dumps java_role Ansible host variables to standard output. The output may be
    filtered by selecting one or more hosts, or a specific variable.
    """

    def get_parser(self, prog_name):
        parser = super(ConfigurationDump, self).get_parser(prog_name)
        group = parser.add_argument_group("Configuration Dump")
        group.add_argument("--dump-facts", default=False,
                           help="whether to gather and dump host facts")
        group.add_argument("--host",
                           help="name of a host to dump config for")
        group.add_argument("--hosts",
                           help="name of hosts and/or groups to dump config "
                                "for")
        group.add_argument("--var-name",
                           help="name of a variable to dump")
        return parser

    def take_action(self, parsed_args):
        self.app.LOG.debug("Dumping Ansible configuration")
        hostvars = self.run_java_role_config_dump(
            parsed_args, host=parsed_args.host, hosts=parsed_args.hosts,
            facts=parsed_args.dump_facts, var_name=parsed_args.var_name)
        try:
            json.dump(hostvars, sys.stdout, sort_keys=True, indent=4)
        except TypeError as e:
            self.app.LOG.error("Failed to JSON encode configuration: %s",
                               repr(e))
            sys.exit(1)


class PlaybookRun(JavaRoleAnsibleMixin, VaultMixin, Command):
    """Run a JavaRole Ansible playbook.

    Allows a single JavaRole ansible playbook to be run. For advanced users only.
    """

    def add_java_role_ansible_args(self, group):
        super(PlaybookRun, self).add_java_role_ansible_args(group)
        group.add_argument("playbook", nargs="+",
                           help="name of the playbook(s) to run")

    def take_action(self, parsed_args):
        self.app.LOG.debug("Running JavaRole playbook(s)")
        self.run_java_role_playbooks(parsed_args, parsed_args.playbook)


class KollaAnsibleRun(KollaAnsibleMixin, VaultMixin, Command):
    """Run a Kolla Ansible command.

    Allows a single lordoftheflies-ansible command to be run. For advanced users only.
    """

    def add_lordoftheflies_ansible_args(self, group):
        super(KollaAnsibleRun, self).add_lordoftheflies_ansible_args(group)
        group.add_argument("--lordoftheflies-inventory-filename", default="overcloud",
                           choices=["seed", "overcloud"],
                           help="name of the lordoftheflies-ansible inventory file, "
                                "one of seed or overcloud (default "
                                "overcloud)")
        group.add_argument("command",
                           help="name of the lordoftheflies-ansible command to run")

    def take_action(self, parsed_args):
        self.app.LOG.debug("Running Kolla Ansible command")
        self.run_lordoftheflies_ansible(parsed_args, parsed_args.command,
                                        parsed_args.lordoftheflies_inventory_filename)


class PhysicalNetworkConfigure(JavaRoleAnsibleMixin, VaultMixin, Command):
    """Configure a set of physical network devices."""

    def get_parser(self, prog_name):
        parser = super(PhysicalNetworkConfigure, self).get_parser(
            prog_name)
        group = parser.add_argument_group("Physical Networking")
        group.add_argument("--group", required=True,
                           help="the Ansible group to apply configuration to")
        group.add_argument("--display", action="store_true",
                           help="display the candidate configuration and exit "
                                "without applying it")
        group.add_argument("--enable-discovery", action="store_true",
                           help="configure the network for hardware discovery")
        group.add_argument("--interface-limit",
                           help="limit the switch interfaces to be configured "
                                "by interface name")
        group.add_argument("--interface-description-limit",
                           help="limit the switch interfaces to be configured "
                                "by interface description")
        return parser

    def take_action(self, parsed_args):
        self.app.LOG.debug("Configuring a physical network")
        extra_vars = {}
        extra_vars["physical_network_display"] = parsed_args.display
        if parsed_args.enable_discovery:
            extra_vars["physical_network_enable_discovery"] = True
        if parsed_args.interface_limit:
            extra_vars["physical_network_interface_limit"] = (
                parsed_args.interface_limit)
        if parsed_args.interface_description_limit:
            extra_vars["physical_network_interface_description_limit"] = (
                parsed_args.interface_description_limit)
        self.run_java_role_playbook(parsed_args, "ansible/physical-network.yml",
                                    limit=parsed_args.group,
                                    extra_vars=extra_vars)


class SeedHypervisorHostConfigure(KollaAnsibleMixin, JavaRoleAnsibleMixin,
                                  VaultMixin, Command):
    """Configure the seed hypervisor node host OS and services.

    * Allocate IP addresses for all configured networks.
    * Add the host to SSH known hosts.
    * Configure a user account for use by java_role for SSH access.
    * Optionally, create a virtualenv for remote target hosts.
    * Configure user accounts, group associations, and authorised SSH keys.
    * Configure Yum repos.
    * Configure the host's network interfaces.
    * Set sysctl parameters.
    * Configure NTP.
    * Configure the host as a libvirt hypervisor.
    """

    def take_action(self, parsed_args):
        self.app.LOG.debug("Configuring seed hypervisor host OS")
        # Explicitly request the dump-config tag to ensure this play runs even
        # if the user specified tags.
        ansible_user = self.run_java_role_config_dump(
            parsed_args, host="seed-hypervisor",
            var_name="java_role_ansible_user", tags="dump-config")
        if not ansible_user:
            self.app.LOG.error("Could not determine java_role_ansible_user "
                               "variable for seed hypervisor host")
            sys.exit(1)
        playbooks = _build_playbook_list(
            "ip-allocation", "ssh-known-host", "java_role-ansible-user",
            "java_role-target-venv", "users", "yum", "dev-tools", "network",
            "sysctl", "ntp", "seed-hypervisor-libvirt-host")
        self.run_java_role_playbooks(parsed_args, playbooks,
                                     limit="seed-hypervisor")


class SeedHypervisorHostUpgrade(JavaRoleAnsibleMixin, VaultMixin, Command):
    """Upgrade the seed hypervisor host services.

    Performs the changes necessary to make the host services suitable for the
    configured OpenStack release.
    """

    def take_action(self, parsed_args):
        self.app.LOG.debug("Upgrading seed hypervisor host services")
        playbooks = _build_playbook_list(
            "java_role-target-venv", "lordoftheflies-target-venv")
        self.run_java_role_playbooks(parsed_args, playbooks,
                                     limit="seed-hypervisor")


class SeedVMProvision(KollaAnsibleMixin, JavaRoleAnsibleMixin, VaultMixin,
                      Command):
    """Provision the seed VM.

    * Allocate IP addresses for all configured networks.
    * Provision a virtual machine using libvirt.
    * Configure the lordoftheflies-ansible inventory for the seed VM.
    """

    def take_action(self, parsed_args):
        self.app.LOG.debug("Provisioning seed VM")
        self.run_java_role_playbook(parsed_args, "ansible/ip-allocation.yml",
                                    limit="seed")
        self.run_java_role_playbook(parsed_args, "ansible/seed-vm-provision.yml")
        # Now populate the Kolla Ansible inventory.
        self.run_java_role_playbook(parsed_args, "ansible/lordoftheflies-ansible.yml",
                                    tags="config")


class SeedVMDeprovision(KollaAnsibleMixin, JavaRoleAnsibleMixin, VaultMixin,
                        Command):
    """Deprovision the seed VM.

    This will destroy the seed VM and all associated volumes.
    """

    def take_action(self, parsed_args):
        self.app.LOG.debug("Deprovisioning seed VM")
        self.run_java_role_playbook(parsed_args,
                                    "ansible/seed-vm-deprovision.yml")


class SeedHostConfigure(KollaAnsibleMixin, JavaRoleAnsibleMixin, VaultMixin,
                        Command):
    """Configure the seed node host OS and services.

    * Allocate IP addresses for all configured networks.
    * Add the host to SSH known hosts.
    * Configure a user account for use by java_role for SSH access.
    * Optionally, create a virtualenv for remote target hosts.
    * Optionally, wipe unmounted disk partitions (--wipe-disks).
    * Configure user accounts, group associations, and authorised SSH keys.
    * Configure Yum repos.
    * Disable SELinux.
    * Configure the host's network interfaces.
    * Set sysctl parameters.
    * Configure IP routing and source NAT.
    * Disable bootstrap interface configuration.
    * Configure NTP.
    * Configure LVM volumes.
    * Optionally, create a virtualenv for lordoftheflies-ansible.
    * Configure a user account for lordoftheflies-ansible.
    * Configure Docker engine.
    """

    def get_parser(self, prog_name):
        parser = super(SeedHostConfigure, self).get_parser(prog_name)
        group = parser.add_argument_group("Host Configuration")
        group.add_argument("--wipe-disks", action='store_true',
                           help="wipe partition and LVM data from all disks "
                                "that are not mounted. Warning: this can "
                                "result in the loss of data")
        return parser

    def take_action(self, parsed_args):
        self.app.LOG.debug("Configuring seed host OS")

        # Query some java_role ansible variables.
        # Explicitly request the dump-config tag to ensure this play runs even
        # if the user specified tags.
        hostvars = self.run_java_role_config_dump(parsed_args, hosts="seed",
                                                  tags="dump-config")
        if not hostvars:
            self.app.LOG.error("No hosts in the seed group")
            sys.exit(1)
        hostvars = hostvars.values()[0]
        ansible_user = hostvars.get("java_role_ansible_user")
        if not ansible_user:
            self.app.LOG.error("Could not determine java_role_ansible_user "
                               "variable for seed host")
            sys.exit(1)
        python_interpreter = hostvars.get("ansible_python_interpreter")
        lordoftheflies_target_venv = hostvars.get("lordoftheflies_ansible_target_venv")

        # Run java_role playbooks.
        playbooks = _build_playbook_list(
            "ip-allocation", "ssh-known-host", "java_role-ansible-user",
            "java_role-target-venv")
        if parsed_args.wipe_disks:
            playbooks += _build_playbook_list("wipe-disks")
        playbooks += _build_playbook_list(
            "users", "yum", "dev-tools", "disable-selinux", "network",
            "sysctl", "ip-routing", "snat", "disable-glean", "ntp", "lvm")
        self.run_java_role_playbooks(parsed_args, playbooks, limit="seed")
        playbooks = _build_playbook_list("lordoftheflies-ansible")
        self.run_java_role_playbooks(parsed_args, playbooks, tags="config")

        # Run lordoftheflies-ansible bootstrap-servers.
        # This command should be run as the java_role ansible user because at this
        # point the lordoftheflies user may not exist.
        extra_vars = {"ansible_user": ansible_user}
        if python_interpreter:
            # Use the java_role virtualenv, as this is the executing user.
            extra_vars["ansible_python_interpreter"] = python_interpreter
        elif lordoftheflies_target_venv:
            # Override the lordoftheflies-ansible virtualenv, use the system python
            # instead.
            extra_vars["ansible_python_interpreter"] = "/usr/bin/python"
        if lordoftheflies_target_venv:
            # Specify a virtualenv in which to install python packages.
            extra_vars["virtualenv"] = lordoftheflies_target_venv
        self.run_lordoftheflies_ansible_seed(parsed_args, "bootstrap-servers",
                                             extra_vars=extra_vars)

        # Run final java_role playbooks.
        playbooks = _build_playbook_list(
            "lordoftheflies-target-venv", "lordoftheflies-host", "docker")
        self.run_java_role_playbooks(parsed_args, playbooks, limit="seed")


class SeedHostUpgrade(KollaAnsibleMixin, JavaRoleAnsibleMixin, VaultMixin,
                      Command):
    """Upgrade the seed host services.

    Performs the changes necessary to make the host services suitable for the
    configured OpenStack release.
    """

    def take_action(self, parsed_args):
        self.app.LOG.debug("Upgrading seed host services")
        playbooks = _build_playbook_list(
            "java_role-target-venv", "lordoftheflies-target-venv")
        self.run_java_role_playbooks(parsed_args, playbooks, limit="seed")


class SeedServiceDeploy(KollaAnsibleMixin, JavaRoleAnsibleMixin, VaultMixin,
                        Command):
    """Deploy the seed services.

    * Configures lordoftheflies-ansible.
    * Configures the bifrost service.
    * Deploys the bifrost container using lordoftheflies-ansible.
    * Builds disk images for the overcloud hosts using Diskimage Builder (DIB).
    * Performs a workaround in the overcloud host image to fix resolv.conf.
    * Configures ironic inspector introspection rules in the bifrost inspector
      service.
    * When enabled, configures a Bare Metal Provisioning (BMP) environment for
      Dell Force10 switches, hosted by the bifrost dnsmasq and nginx services.
    """

    def take_action(self, parsed_args):
        self.app.LOG.debug("Deploying seed services")
        playbooks = _build_playbook_list("lordoftheflies-ansible")
        self.run_java_role_playbooks(parsed_args, playbooks, tags="config")

        playbooks = _build_playbook_list("lordoftheflies-bifrost")
        self.run_java_role_playbooks(parsed_args, playbooks)
        self.run_lordoftheflies_ansible_seed(parsed_args, "deploy-bifrost")
        playbooks = _build_playbook_list(
            "overcloud-host-image-workaround-resolv",
            "seed-introspection-rules",
            "dell-switch-bmp")
        self.run_java_role_playbooks(parsed_args, playbooks)


class SeedContainerImageBuild(JavaRoleAnsibleMixin, VaultMixin, Command):
    """Build the seed container images.

    * Installs and configures lordoftheflies build environment on the seed.
    * Builds container images for the seed services.
    """

    def get_parser(self, prog_name):
        parser = super(SeedContainerImageBuild, self).get_parser(
            prog_name)
        group = parser.add_argument_group("Container Image Build")
        group.add_argument("--push", action="store_true",
                           help="whether to push images to a registry after "
                                "building")
        group.add_argument("regex", nargs='*',
                           help="regular expression matching names of images "
                                "to build. Builds all images if unspecified")
        return parser

    def take_action(self, parsed_args):
        self.app.LOG.debug("Building seed container images")
        playbooks = _build_playbook_list(
            "container-image-builders-check", "lordoftheflies-build",
            "container-image-build")
        extra_vars = {"push_images": parsed_args.push}
        if parsed_args.regex:
            regexes = "'%s'" % " ".join(parsed_args.regex)
            extra_vars["container_image_regexes"] = regexes
        else:
            extra_vars["container_image_sets"] = (
                "{{ seed_container_image_sets }}")
        self.run_java_role_playbooks(parsed_args, playbooks,
                                     extra_vars=extra_vars)


class SeedDeploymentImageBuild(JavaRoleAnsibleMixin, VaultMixin, Command):
    """Build the seed deployment kernel and ramdisk images.

    Builds Ironic Python Agent (IPA) deployment images using Diskimage Builder
    (DIB) for use when provisioning and inspecting the overcloud hosts.
    """

    def take_action(self, parsed_args):
        self.app.LOG.debug("Building seed deployment images")
        playbooks = _build_playbook_list("seed-ipa-build")
        self.run_java_role_playbooks(parsed_args, playbooks)


class OvercloudInventoryDiscover(JavaRoleAnsibleMixin, VaultMixin, Command):
    """Discover the overcloud inventory from the seed's Ironic service.

    * Query the ironic inventory on the seed, and use this to populate java_role's
      ansible inventory.
    * Allocate IP addresses for all configured networks.
    * Configure the bifrost service with host variables for provisioning the
      overcloud hosts.
    * Update the lordoftheflies-ansible configuration for the new overcloud hosts.
    """

    def take_action(self, parsed_args):
        self.app.LOG.debug("Discovering overcloud inventory")
        # Run the inventory discovery playbook separately, else the discovered
        # hosts will not be present in the following playbooks in which they
        # are used to populate other inventories.
        self.run_java_role_playbook(parsed_args,
                                    "ansible/overcloud-inventory-discover.yml")
        # If necessary, allocate IP addresses for the discovered hosts.
        self.run_java_role_playbook(parsed_args,
                                    "ansible/ip-allocation.yml")
        # Now populate the Kolla Ansible and Bifrost inventories.
        self.run_java_role_playbook(parsed_args,
                                    "ansible/lordoftheflies-bifrost-hostvars.yml")
        self.run_java_role_playbook(parsed_args, "ansible/lordoftheflies-ansible.yml",
                                    tags="config")


class OvercloudIntrospectionDataSave(JavaRoleAnsibleMixin, VaultMixin, Command):
    """Save hardware introspection data for the overcloud.

    Save hardware introspection data from the seed's ironic inspector service
    to the control host.
    """

    def get_parser(self, prog_name):
        parser = super(OvercloudIntrospectionDataSave, self).get_parser(
            prog_name)
        group = parser.add_argument_group("Introspection data")
        # Defaults for these are applied in the playbook.
        group.add_argument("--output-dir", type=str,
                           help="Path to directory in which to save "
                                "introspection data. Default: "
                                "$PWD/overcloud-introspection-data")
        group.add_argument("--output-format", type=str,
                           help="Format in which to save output data. One of "
                                "JSON or YAML. Default: JSON",
                           choices=["JSON", "YAML"])
        return parser

    def take_action(self, parsed_args):
        self.app.LOG.debug("Saving introspection data")
        extra_vars = {}
        if parsed_args.output_dir:
            extra_vars['output_dir'] = parsed_args.output_dir
        if parsed_args.output_format:
            extra_vars['output_format'] = parsed_args.output_format
        playbooks = _build_playbook_list("overcloud-introspection-data-save")
        self.run_java_role_playbooks(parsed_args, playbooks,
                                     extra_vars=extra_vars)


class OvercloudBIOSRAIDConfigure(JavaRoleAnsibleMixin, VaultMixin, Command):
    """Configure BIOS and RAID for the overcloud hosts."""

    def take_action(self, parsed_args):
        self.app.LOG.debug("Configure overcloud BIOS and RAID")
        playbooks = _build_playbook_list("overcloud-bios-raid")
        self.run_java_role_playbooks(parsed_args, playbooks)


class OvercloudHardwareInspect(JavaRoleAnsibleMixin, VaultMixin, Command):
    """Inspect the overcloud hardware using ironic inspector.

    Perform hardware inspection of existing ironic nodes in the seed's
    ironic inventory.
    """

    def take_action(self, parsed_args):
        self.app.LOG.debug("Inspecting overcloud")
        playbooks = _build_playbook_list("overcloud-hardware-inspect")
        self.run_java_role_playbooks(parsed_args, playbooks)


class OvercloudProvision(JavaRoleAnsibleMixin, VaultMixin, Command):
    """Provision the overcloud.

    Provision the overcloud hosts using the seed host's bifrost service. This
    will image the hosts and perform some minimal network configuration using
    glean/simple-init.
    """

    def take_action(self, parsed_args):
        self.app.LOG.debug("Provisioning overcloud")
        playbooks = _build_playbook_list("overcloud-provision")
        self.run_java_role_playbooks(parsed_args, playbooks)


class OvercloudDeprovision(JavaRoleAnsibleMixin, VaultMixin, Command):
    """Deprovision the overcloud.

    Deprovision the overcloud hosts using the seed host's bifrost service. This
    will clear the instance state of the nodes from the seed's ironic service
    and power them off.
    """

    def take_action(self, parsed_args):
        self.app.LOG.debug("Deprovisioning overcloud")
        playbooks = _build_playbook_list("overcloud-deprovision")
        self.run_java_role_playbooks(parsed_args, playbooks)


class OvercloudHostConfigure(KollaAnsibleMixin, JavaRoleAnsibleMixin, VaultMixin,
                             Command):
    """Configure the overcloud host OS and services.

    * Allocate IP addresses for all configured networks.
    * Add the host to SSH known hosts.
    * Configure a user account for use by java_role for SSH access.
    * Optionally, create a virtualenv for remote target hosts.
    * Optionally, wipe unmounted disk partitions (--wipe-disks).
    * Configure user accounts, group associations, and authorised SSH keys.
    * Configure Yum repos.
    * Disable SELinux.
    * Configure the host's network interfaces.
    * Set sysctl parameters.
    * Disable bootstrap interface configuration.
    * Configure NTP.
    * Configure LVM volumes.
    * Optionally, create a virtualenv for lordoftheflies-ansible.
    * Configure a user account for lordoftheflies-ansible.
    * Configure Docker engine.
    """

    def get_parser(self, prog_name):
        parser = super(OvercloudHostConfigure, self).get_parser(prog_name)
        group = parser.add_argument_group("Host Configuration")
        group.add_argument("--wipe-disks", action='store_true',
                           help="wipe partition and LVM data from all disks "
                                "that are not mounted. Warning: this can "
                                "result in the loss of data")
        return parser

    def take_action(self, parsed_args):
        self.app.LOG.debug("Configuring overcloud host OS")

        # Query some java_role ansible variables.
        # Explicitly request the dump-config tag to ensure this play runs even
        # if the user specified tags.
        hostvars = self.run_java_role_config_dump(parsed_args, hosts="overcloud",
                                                  tags="dump-config")
        if not hostvars:
            self.app.LOG.error("No hosts in the overcloud group")
            sys.exit(1)
        hostvars = hostvars.values()[0]
        ansible_user = hostvars.get("java_role_ansible_user")
        if not ansible_user:
            self.app.LOG.error("Could not determine java_role_ansible_user "
                               "variable for overcloud hosts")
            sys.exit(1)
        python_interpreter = hostvars.get("ansible_python_interpreter")
        lordoftheflies_target_venv = hostvars.get("lordoftheflies_ansible_target_venv")

        # JavaRole playbooks.
        playbooks = _build_playbook_list(
            "ip-allocation", "ssh-known-host", "java_role-ansible-user",
            "java_role-target-venv")
        if parsed_args.wipe_disks:
            playbooks += _build_playbook_list("wipe-disks")
        playbooks += _build_playbook_list(
            "users", "yum", "dev-tools", "disable-selinux", "network",
            "sysctl", "disable-glean", "ntp", "lvm")
        self.run_java_role_playbooks(parsed_args, playbooks, limit="overcloud")
        playbooks = _build_playbook_list("lordoftheflies-ansible")
        self.run_java_role_playbooks(parsed_args, playbooks, tags="config")

        # lordoftheflies-ansible bootstrap-servers.
        # The lordoftheflies-ansible bootstrap-servers command should be run as the
        # java_role ansible user because at this point the lordoftheflies user may not
        # exist.
        extra_vars = {"ansible_user": ansible_user}
        if python_interpreter:
            # Use the java_role virtualenv, as this is the executing user.
            extra_vars["ansible_python_interpreter"] = python_interpreter
        elif lordoftheflies_target_venv:
            # Override the lordoftheflies-ansible virtualenv, use the system python
            # instead.
            extra_vars["ansible_python_interpreter"] = "/usr/bin/python"
        if lordoftheflies_target_venv:
            # Specify a virtualenv in which to install python packages.
            extra_vars["virtualenv"] = lordoftheflies_target_venv
        self.run_lordoftheflies_ansible_overcloud(parsed_args, "bootstrap-servers",
                                                  extra_vars=extra_vars)

        # Further java_role playbooks.
        playbooks = _build_playbook_list(
            "lordoftheflies-target-venv", "lordoftheflies-host", "docker")
        self.run_java_role_playbooks(parsed_args, playbooks, limit="overcloud")


class OvercloudHostUpgrade(JavaRoleAnsibleMixin, VaultMixin, Command):
    """Upgrade the overcloud host services.

    Performs the changes necessary to make the host services suitable for the
    configured OpenStack release.
    """

    def take_action(self, parsed_args):
        self.app.LOG.debug("Upgrading overcloud host services")
        playbooks = _build_playbook_list(
            "java_role-target-venv", "lordoftheflies-target-venv",
            "overcloud-docker-sdk-upgrade", "overcloud-etc-hosts-fixup")
        self.run_java_role_playbooks(parsed_args, playbooks, limit="overcloud")


class OvercloudServiceConfigurationGenerate(JavaRoleAnsibleMixin,
                                            KollaAnsibleMixin, VaultMixin,
                                            Command):
    """Generate the overcloud service configuration files.

    Generates lordoftheflies-ansible configuration for the OpenStack control plane
    services, without pushing that configuration to the running containers.
    This can be used to generate a candidate configuration set for comparison
    with the existing configuration. It is recommended to use a directory other
    than /etc/lordoftheflies for --node-config-dir, to ensure that the running
    containers are not affected.
    """

    def get_parser(self, prog_name):
        parser = super(OvercloudServiceConfigurationGenerate,
                       self).get_parser(prog_name)
        group = parser.add_argument_group("Service Configuration")
        group.add_argument("--node-config-dir", required=True,
                           help="the directory to store the config files on "
                                "the remote node (required)")
        group.add_argument("--skip-prechecks", action='store_true',
                           help="skip the lordoftheflies-ansible prechecks command")
        return parser

    def take_action(self, parsed_args):
        self.app.LOG.debug("Generating overcloud service configuration")

        # First prepare configuration.
        playbooks = _build_playbook_list("lordoftheflies-ansible")
        self.run_java_role_playbooks(parsed_args, playbooks, tags="config")

        playbooks = _build_playbook_list("lordoftheflies-openstack", "swift-setup")
        self.run_java_role_playbooks(parsed_args, playbooks)

        # Run lordoftheflies-ansible prechecks before deployment.
        if not parsed_args.skip_prechecks:
            self.run_lordoftheflies_ansible_overcloud(parsed_args, "prechecks")

        # Generate the configuration.
        extra_vars = {}
        if parsed_args.node_config_dir:
            extra_vars["node_config_directory"] = parsed_args.node_config_dir
        self.run_lordoftheflies_ansible_overcloud(parsed_args, "genconfig",
                                                  extra_vars=extra_vars)


class OvercloudServiceConfigurationSave(JavaRoleAnsibleMixin, VaultMixin,
                                        Command):
    """Gather and save the overcloud service configuration files.

    This can be used to collect the running configuration for inspection (the
    default) or a candidate configuration generated via 'java_role overcloud
    service configuration generate', for comparision with another configuration
    set.
    """

    def get_parser(self, prog_name):
        parser = super(OvercloudServiceConfigurationSave, self).get_parser(
            prog_name)
        group = parser.add_argument_group("Service configuration")
        group.add_argument("--node-config-dir",
                           help="the directory to store the config files on "
                                "the remote node (default /etc/lordoftheflies)")
        group.add_argument("--output-dir",
                           help="path to a directory in which to save "
                                "configuration")
        return parser

    def take_action(self, parsed_args):
        self.app.LOG.debug("Saving overcloud service configuration")
        playbooks = _build_playbook_list("overcloud-service-config-save")
        extra_vars = {}
        if parsed_args.output_dir:
            extra_vars["config_save_path"] = parsed_args.output_dir
        if parsed_args.node_config_dir:
            extra_vars["node_config_directory"] = parsed_args.node_config_dir
        self.run_java_role_playbooks(parsed_args, playbooks,
                                     extra_vars=extra_vars)


class OvercloudServiceDeploy(KollaAnsibleMixin, JavaRoleAnsibleMixin, VaultMixin,
                             Command):
    """Deploy the overcloud services.

    * Configure lordoftheflies-ansible.
    * Configure overcloud services in lordoftheflies-ansible.
    * Perform lordoftheflies-ansible prechecks to verify the system state for
      deployment.
    * Perform a lordoftheflies-ansible deployment of the overcloud services.
    * Configure and deploy java_role extra services.
    * Generate openrc files for the admin user.

    This can be used in conjunction with the --tags and --lordoftheflies-tags arguments
    to deploy specific services.
    """

    def get_parser(self, prog_name):
        parser = super(OvercloudServiceDeploy, self).get_parser(prog_name)
        group = parser.add_argument_group("Service Deployment")
        group.add_argument("--skip-prechecks", action='store_true',
                           help="skip the lordoftheflies-ansible prechecks command")
        return parser

    def take_action(self, parsed_args):
        self.app.LOG.debug("Deploying overcloud services")

        # First prepare configuration.
        playbooks = _build_playbook_list("lordoftheflies-ansible")
        self.run_java_role_playbooks(parsed_args, playbooks, tags="config")

        playbooks = _build_playbook_list("lordoftheflies-openstack", "swift-setup")
        self.run_java_role_playbooks(parsed_args, playbooks)

        # Run lordoftheflies-ansible prechecks before deployment.
        if not parsed_args.skip_prechecks:
            self.run_lordoftheflies_ansible_overcloud(parsed_args, "prechecks")

        # Perform the lordoftheflies-ansible deployment.
        self.run_lordoftheflies_ansible_overcloud(parsed_args, "deploy")

        # Deploy java_role extra services.
        playbooks = _build_playbook_list("overcloud-extras")
        extra_vars = {"action": "deploy"}
        self.run_java_role_playbooks(parsed_args, playbooks,
                                     extra_vars=extra_vars)

        # Post-deployment configuration.
        # FIXME: Fudge to work around incorrect configuration path.
        extra_vars = {"node_config_directory": parsed_args.lordoftheflies_config_path}
        self.run_lordoftheflies_ansible_overcloud(parsed_args, "post-deploy",
                                                  extra_vars=extra_vars)
        # Create an environment file for accessing the public API as the admin
        # user.
        playbooks = _build_playbook_list("public-openrc")
        self.run_java_role_playbooks(parsed_args, playbooks)


class OvercloudServiceReconfigure(KollaAnsibleMixin, JavaRoleAnsibleMixin,
                                  VaultMixin, Command):
    """Reconfigure the overcloud services.

    * Configure lordoftheflies-ansible.
    * Configure overcloud services in lordoftheflies-ansible.
    * Perform lordoftheflies-ansible prechecks to verify the system state for
      deployment.
    * Perform a lordoftheflies-ansible reconfiguration of the overcloud services.
    * Configure and deploy java_role extra services.
    * Generate openrc files for the admin user.

    This can be used in conjunction with the --tags and --lordoftheflies-tags arguments
    to reconfigure specific services.
    """

    def get_parser(self, prog_name):
        parser = super(OvercloudServiceReconfigure, self).get_parser(prog_name)
        group = parser.add_argument_group("Service Reconfiguration")
        group.add_argument("--skip-prechecks", action='store_true',
                           help="skip the lordoftheflies-ansible prechecks command")
        return parser

    def take_action(self, parsed_args):
        self.app.LOG.debug("Reconfiguring overcloud services")

        # First prepare configuration.
        playbooks = _build_playbook_list("lordoftheflies-ansible")
        self.run_java_role_playbooks(parsed_args, playbooks, tags="config")

        playbooks = _build_playbook_list("lordoftheflies-openstack", "swift-setup")
        self.run_java_role_playbooks(parsed_args, playbooks)

        # Run lordoftheflies-ansible prechecks before reconfiguration.
        if not parsed_args.skip_prechecks:
            self.run_lordoftheflies_ansible_overcloud(parsed_args, "prechecks")

        # Perform the lordoftheflies-ansible reconfiguration.
        self.run_lordoftheflies_ansible_overcloud(parsed_args, "reconfigure")

        # Reconfigure java_role extra services.
        playbooks = _build_playbook_list("overcloud-extras")
        extra_vars = {"action": "reconfigure"}
        self.run_java_role_playbooks(parsed_args, playbooks,
                                     extra_vars=extra_vars)

        # Post-deployment configuration.
        # FIXME: Fudge to work around incorrect configuration path.
        extra_vars = {"node_config_directory": parsed_args.lordoftheflies_config_path}
        self.run_lordoftheflies_ansible_overcloud(parsed_args, "post-deploy",
                                                  extra_vars=extra_vars)
        # Create an environment file for accessing the public API as the admin
        # user.
        playbooks = _build_playbook_list("public-openrc")
        self.run_java_role_playbooks(parsed_args, playbooks)


class OvercloudServiceUpgrade(KollaAnsibleMixin, JavaRoleAnsibleMixin,
                              VaultMixin, Command):
    """Upgrade the overcloud services.

    * Configure lordoftheflies-ansible.
    * Configure overcloud services in lordoftheflies-ansible.
    * Perform lordoftheflies-ansible prechecks to verify the system state for
      deployment.
    * Perform a lordoftheflies-ansible upgrade of the overcloud services.
    * Configure and upgrade java_role extra services.

    This can be used in conjunction with the --tags and --lordoftheflies-tags arguments
    to upgrade specific services.
    """

    def get_parser(self, prog_name):
        parser = super(OvercloudServiceUpgrade, self).get_parser(prog_name)
        group = parser.add_argument_group("Service Upgrade")
        group.add_argument("--skip-prechecks", action='store_true',
                           help="skip the lordoftheflies-ansible prechecks command")
        return parser

    def take_action(self, parsed_args):
        self.app.LOG.debug("Upgrading overcloud services")

        # First prepare configuration.
        playbooks = _build_playbook_list("lordoftheflies-ansible", "lordoftheflies-openstack")
        self.run_java_role_playbooks(parsed_args, playbooks)

        # Run lordoftheflies-ansible prechecks before upgrade.
        if not parsed_args.skip_prechecks:
            self.run_lordoftheflies_ansible_overcloud(parsed_args, "prechecks")

        # Perform the lordoftheflies-ansible upgrade.
        self.run_lordoftheflies_ansible_overcloud(parsed_args, "upgrade")

        # Upgrade java_role extra services.
        playbooks = _build_playbook_list("overcloud-extras")
        extra_vars = {"action": "upgrade"}
        self.run_java_role_playbooks(parsed_args, playbooks,
                                     extra_vars=extra_vars)


class OvercloudServiceDestroy(KollaAnsibleMixin, JavaRoleAnsibleMixin,
                              VaultMixin, Command):
    """Destroy the overcloud services.

    Permanently destroy the overcloud containers, container images, and
    container volumes.
    """

    def get_parser(self, prog_name):
        parser = super(OvercloudServiceDestroy, self).get_parser(prog_name)
        group = parser.add_argument_group("Services")
        group.add_argument("--yes-i-really-really-mean-it",
                           action='store_true',
                           help="confirm that you understand that this will "
                                "permantently destroy all services and data.")
        return parser

    def take_action(self, parsed_args):
        if not parsed_args.yes_i_really_really_mean_it:
            self.app.LOG.error("This will permanently destroy all services "
                               "and data. Specify "
                               "--yes-i-really-really-mean-it to confirm that "
                               "you understand this.")
            sys.exit(1)

        self.app.LOG.debug("Destroying overcloud services")

        # First prepare configuration.
        playbooks = _build_playbook_list("lordoftheflies-ansible")
        self.run_java_role_playbooks(parsed_args, playbooks, tags="config")

        playbooks = _build_playbook_list("lordoftheflies-openstack")
        self.run_java_role_playbooks(parsed_args, playbooks)

        # Run lordoftheflies-ansible destroy.
        extra_args = ["--yes-i-really-really-mean-it"]
        self.run_lordoftheflies_ansible_overcloud(parsed_args, "destroy",
                                                  extra_args=extra_args)

        # Destroy java_role extra services.
        playbooks = _build_playbook_list("overcloud-extras")
        extra_vars = {"action": "destroy"}
        self.run_java_role_playbooks(parsed_args, playbooks,
                                     extra_vars=extra_vars)


class OvercloudContainerImagePull(JavaRoleAnsibleMixin, KollaAnsibleMixin,
                                  VaultMixin, Command):
    """Pull the overcloud container images from a registry."""

    def take_action(self, parsed_args):
        self.app.LOG.debug("Pulling overcloud container images")

        # First prepare configuration.
        playbooks = _build_playbook_list("lordoftheflies-ansible")
        self.run_java_role_playbooks(parsed_args, playbooks, tags="config")

        # Pull updated lordoftheflies container images.
        self.run_lordoftheflies_ansible_overcloud(parsed_args, "pull")

        # Pull container images for java_role extra services.
        playbooks = _build_playbook_list("overcloud-extras")
        extra_vars = {"action": "pull"}
        self.run_java_role_playbooks(parsed_args, playbooks,
                                     extra_vars=extra_vars)


class OvercloudContainerImageBuild(JavaRoleAnsibleMixin, VaultMixin, Command):
    """Build the overcloud container images."""

    def get_parser(self, prog_name):
        parser = super(OvercloudContainerImageBuild, self).get_parser(
            prog_name)
        group = parser.add_argument_group("Container Image Build")
        group.add_argument("--push", action="store_true",
                           help="whether to push images to a registry after "
                                "building")
        group.add_argument("regex", nargs='*',
                           help="regular expression matching names of images "
                                "to build. Builds all images if unspecified")
        return parser

    def take_action(self, parsed_args):
        self.app.LOG.debug("Building overcloud container images")
        playbooks = _build_playbook_list(
            "container-image-builders-check", "lordoftheflies-build",
            "container-image-build")
        extra_vars = {"push_images": parsed_args.push}
        if parsed_args.regex:
            regexes = "'%s'" % " ".join(parsed_args.regex)
            extra_vars["container_image_regexes"] = regexes
        else:
            extra_vars["container_image_sets"] = (
                "{{ overcloud_container_image_sets }}")
        self.run_java_role_playbooks(parsed_args, playbooks,
                                     extra_vars=extra_vars)


class OvercloudDeploymentImageBuild(JavaRoleAnsibleMixin, VaultMixin, Command):
    """Build the overcloud deployment kernel and ramdisk images."""

    def take_action(self, parsed_args):
        self.app.LOG.debug("Building overcloud deployment images")
        playbooks = _build_playbook_list("overcloud-ipa-build")
        self.run_java_role_playbooks(parsed_args, playbooks)


class OvercloudPostConfigure(JavaRoleAnsibleMixin, VaultMixin, Command):
    """Perform post-deployment configuration.

    * Register Ironic Python Agent (IPA) deployment images using Diskimage
      Builder (DIB), if building deployment images locally.
    * Register ironic inspector introspection rules with the overcloud
      inspector service.
    * Register a provisioning network with glance.
    * Configure Grafana for control plane.
    """

    def take_action(self, parsed_args):
        self.app.LOG.debug("Performing post-deployment configuration")
        playbooks = _build_playbook_list(
            "overcloud-ipa-images", "overcloud-introspection-rules",
            "overcloud-introspection-rules-dell-lldp-workaround",
            "provision-net", "overcloud-grafana-configure")
        self.run_java_role_playbooks(parsed_args, playbooks)


class NetworkConnectivityCheck(JavaRoleAnsibleMixin, VaultMixin, Command):
    """Check network connectivity between hosts in the control plane.

    Checks for access to an external IP address, an external hostname, any
    configured gateways, and between hosts on the same subnets. The MTU of
    each network is validated by sending ping packets of maximum size.
    """

    def take_action(self, parsed_args):
        self.app.LOG.debug("Performing network connectivity check")
        playbooks = _build_playbook_list("network-connectivity")
        self.run_java_role_playbooks(parsed_args, playbooks)


class BaremetalComputeInspect(JavaRoleAnsibleMixin, VaultMixin, Command):
    """Perform hardware inspection on baremetal compute nodes."""

    def take_action(self, parsed_args):
        self.app.LOG.debug("Performing hardware inspection on baremetal "
                           "compute nodes")
        playbooks = _build_playbook_list("baremetal-compute-inspect")
        self.run_java_role_playbooks(parsed_args, playbooks)


class BaremetalComputeManage(JavaRoleAnsibleMixin, VaultMixin, Command):
    """Put baremetal compute nodes into the manageable provision state."""

    def take_action(self, parsed_args):
        self.app.LOG.debug("Making baremetal compute nodes manageable")
        playbooks = _build_playbook_list("baremetal-compute-manage")
        self.run_java_role_playbooks(parsed_args, playbooks)


class BaremetalComputeProvide(JavaRoleAnsibleMixin, VaultMixin, Command):
    """Put baremetal compute nodes into the available provision state."""

    def take_action(self, parsed_args):
        self.app.LOG.debug("Making baremetal compute nodes available")
        playbooks = _build_playbook_list("baremetal-compute-provide")
        self.run_java_role_playbooks(parsed_args, playbooks)
