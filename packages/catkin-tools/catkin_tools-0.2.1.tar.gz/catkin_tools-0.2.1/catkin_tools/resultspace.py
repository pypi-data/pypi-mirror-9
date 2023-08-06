
import os
import re

from .runner import run_command
from .common import string_type


def get_resultspace_environment(result_space_path, quiet=False):
    """Get the environemt variables which result from sourcing another catkin
    workspace's setup files as the string output of `cmake -E environment`.
    This command is used to be as portable as possible.

    :param result_space_path: path to a Catkin result-space whose environment should be loaded, ``str``
    :type result_space_path: str
    :param quiet: don't throw exceptions, ``bool``
    :type quiet: bool

    :returns: a dictionary of environment variables and their values
    """
    # Check to make sure result_space_path is a valid directory
    if not os.path.isdir(result_space_path):
        if quiet:
            return dict()
        raise IOError(
            "Cannot load environment from resultspace \"%s\" because it does not "
            "exist." % result_space_path
        )

    # Check to make sure result_space_path contains a `.catkin` file
    # TODO: `.catkin` should be defined somewhere as an atom in catkin_pkg
    if not os.path.exists(os.path.join(result_space_path, '.catkin')):
        if quiet:
            return dict()
        raise IOError(
            "Cannot load environment from resultspace \"%s\" because it does not "
            "appear to be a catkin-generated resultspace (missing .catkin marker "
            "file)." % result_space_path
        )

    # Determine the shell to use to source the setup file
    shell_path = os.environ['SHELL']
    (_, shell_name) = os.path.split(shell_path)

    # Use fallback shell if using a non-standard shell
    if shell_name not in ['bash', 'zsh']:
        shell_name = 'bash'

    # Check to make sure result_space_path contains the appropriate setup file
    setup_file_path = os.path.join(result_space_path, 'env.sh')
    if not os.path.exists(setup_file_path):
        if quiet:
            return dict()
        raise IOError(
            "Cannot load environment from resultspace \"%s\" because the "
            "required setup file \"%s\" does not exist." % (result_space_path, setup_file_path)
        )

    # Construct a command list which sources the setup file and prints the env to stdout
    norc_flags = {'bash': '--norc', 'zsh': '-f'}
    subcommand = '%s cmake -E environment | sort' % (setup_file_path)

    command = [
        shell_path,
        norc_flags[shell_name],
        '-c', subcommand]

    # Run the command to source the other environment and output all environment variables
    blacklisted_keys = ('_', 'PWD')
    env_regex = re.compile('(.+?)=(.*)$', re.M)
    env_dict = {}

    for line in run_command(command, cwd=os.getcwd()):
        if isinstance(line, string_type):
            matches = env_regex.findall(line)
            for (key, value) in matches:
                value = value.rstrip()
                if key not in blacklisted_keys and key not in env_dict:
                    env_dict[key] = value

    return env_dict


def load_resultspace_environment(result_space_path):
    """Load the environemt variables which result from sourcing another
    workspace path into this process's environment.

    :param result_space_path: path to a Catkin result-space whose environment should be loaded, ``str``
    :type result_space_path: str
    """
    env_dict = get_resultspace_environment(result_space_path)
    os.environ.update(env_dict)
