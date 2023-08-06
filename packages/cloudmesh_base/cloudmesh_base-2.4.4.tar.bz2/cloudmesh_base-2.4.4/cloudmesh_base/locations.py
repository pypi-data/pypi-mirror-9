from cloudmesh_base.util import path_expand


__config_dir_prefix__ = "~/.cloudmesh"

__config_dir__ = path_expand(__config_dir_prefix__)


def config_file(filename):
    """
    The location of the config file: ~/.cloudmesh/filename. ~ will be expanded
    :param filename: the filename
    """
    return __config_dir__ + filename


def config_file_raw(filename):
    """
    The location of the config file: ~/.cloudmesh/filename. ~ will NOT be expanded
    :param filename: the filename
    """
    return __config_dir_prefix__ + filename


def config_file_prefix():
    """
    The prefix of the configuration file location
    """
    return __config_dir_prefix__

