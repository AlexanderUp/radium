### Radium test task

## Description

Test task from Radium company.

Application is able to:

- Download asyncroniously with 3 concurrent tasks HEAD of repo located at https://gitea.radium.group/radium/project-configuration to temporary directory.

- Calculate sha256 hash of downloaded files.

- Pass wemake-python-styleguide linter with nitpick configuration from https://gitea.radium.group/radium/project-configuration.


## How to run application

- Clone repo

```git clone https://github.com/AlexanderUp/radium.git```

- Install dependencies

```poetry install``

- Switch to poetry shell to run script inside virtual environment

```poetry shell```

- Change directory to 'script'

```cd script```

- Run script

```python3 main.py```