# Ansible Role: Java

## Status

[![Build Status](https://travis-ci.org/lordoftheflies/java_role.svg?branch=master)](https://travis-ci.org/lordoftheflies/java_role)

Installs Java for RedHat/CentOS and Debian/Ubuntu linux servers.

## Setup test environment

```shell script
virtualenv --python=/usr/bin/python3.7 .env
source .env/bin/activate
pip install molecule molecule[lint] molecule[docker] docker docker-compose tox pytest
```

## Requirements

None.

## Role Variables

Available variables are listed below, along with default values:

    # The defaults provided by this role are specific to each distribution.
    java_packages:
      - java-1.8.0-openjdk

Set the version/development kit of Java to install, along with any other necessary Java packages. Some other options include are included in the distribution-specific files in this role's 'defaults' folder.

    java_home: ""

If set, the role will set the global environment variable `JAVA_HOME` to this value.

## Dependencies

None.

## Example Playbook (using default package)

    - hosts: servers
      roles:
        - role: lordoftheflies.role_java
          become: yes

## Example Playbook (install OpenJDK 8)

For RHEL / CentOS:

    - hosts: server
      roles:
        - role: lordoftheflies.role_java
          when: "ansible_os_family == 'RedHat'"
          java_packages:
            - java-1.8.0-openjdk

For Ubuntu < 16.04:

    - hosts: server
      tasks:
        - name: installing repo for Java 8 in Ubuntu
  	      apt_repository: repo='ppa:openjdk-r/ppa'
    
    - hosts: server
      roles:
        - role: lordoftheflies.role_java
          when: "ansible_os_family == 'Debian'"
          java_packages:
            - openjdk-8-jdk
            
## Authors

* [lordoftheflies](https://cherubits.hu/lordoftheflies) [:email:](mailto:laszlo.hegedus@cherubits.hu)
* [geerlingguy](https://www.jeffgeerling.com/) [:email:](jeff@jeffgeerling.com)

###> Setup for development

```shell script
pre-commit install
```

It is highly recommend you enable setting for storing the venvs within your projects.

```shell script
poetry config settings.virtualenvs.in-project true
```

Install project dependencies.
```shell script
poetry install
```

### Running the package locally

Activate the virtual environment.

```shell script
source .venv/bin/activate
```

Run the package as a module.

```shell script
python -m gitcommit
```

### Deploy

Deployment is handled automatically by Travis CI. It has been linked to the repository and is automatically watching for pushes to master. It will build and test every commit to master. It will also build every tagged commit as if it was a branch, and since its a tagged commit, will attempt to publish it to PyPI.

Don't forget to increment version number set in pyproject.toml. This can be done with poetry.

```shell script
poetry version [patch|minor|major]
```

Tag the commit (by default applies to HEAD commit - make sure you are on the latest develop commit).

```shell script
git tag v#.#.#
```

When pushing commits to remote, you must explicitly push tags too.

```shell script
git push origin --tags
```