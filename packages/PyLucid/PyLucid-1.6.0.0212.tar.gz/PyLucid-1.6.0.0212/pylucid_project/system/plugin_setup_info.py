# coding: utf-8

"""
    Stuff needed to expand settings.INSTALLED_APPS and settings.TEMPLATE_DIRS
    
    Important: We can't use any django things here. Because this module
    would be imported in settings.py
"""


from pylucid_project.utils.python_tools import has_init_file
import os
import warnings
import sys


class Plugin(object):
    def __init__(self, pkg_path, section, pkg_dir):
        self.pkg_path = pkg_path
        self.section = section
        self.pkg_dir = pkg_dir


class PyLucidPluginSetupInfo(dict):
    """
    A instance would be made in settings.py and bind to:
    
        settings.PYLUCID_PLUGIN_SETUP_INFO
        
    This instance used in pylucid_project.system.pylucid_plugins
    """
    def __init__(self, plugin_package_list, verbose=True):
        super(PyLucidPluginSetupInfo, self).__init__()
        self.verbose = verbose

        # for expand: settings.TEMPLATE_DIRS
        self.template_dirs = []
        # for expand: settings.INSTALLED_APPS
        self.installed_plugins = []

        self.additional_settings = []

        if "PYLUCID_ADD_PLUGINS_PATH" in os.environ:
            additional_path = os.environ["PYLUCID_ADD_PLUGINS_PATH"]

            plugin_package_list = list(plugin_package_list)

            for path in additional_path.split(";"):
                if self.verbose:
                    print "Add additional plugin path: %s" % path

                base_path, pkg_dir = os.path.split(path)
                section = os.path.split(base_path)[1]

                plugin_package_list.append(
                    (base_path, section, pkg_dir)
                )

            plugin_package_list = tuple(plugin_package_list)

            if self.verbose:
                print "Use this paths: %s" % repr(plugin_package_list)


        for base_path, section, pkg_dir in plugin_package_list:
            # e.g.: (PYLUCID_BASE_PATH, "pylucid_project", "pylucid_plugins")
            self.add(base_path, section, pkg_dir)

        self.template_dirs = tuple(self.template_dirs)
        self.installed_plugins = tuple(self.installed_plugins)

#        print " *** template dirs:\n", "\n".join(self.template_dirs)
#        print " *** installed plugins:\n", "\n".join(self.installed_plugins)

    def _isdir(self, path):
        if os.path.isdir(path):
            return True
        if self.verbose:
            warnings.warn("path %r doesn't exist." % path)
        return False

    def add(self, base_path, section, pkg_dir):
        """
        Add all plugins in one filesystem path/packages.
        e.g.: (PYLUCID_BASE_PATH, "pylucid_project", "pylucid_plugins")
        """
        if not self._isdir(base_path):
            return

        pkg_path = os.path.join(base_path, pkg_dir)
        if not self._isdir(pkg_path):
            return

        if not has_init_file(pkg_path):
            if self.verbose:
                warnings.warn("plugin path %r doesn't contain a __init__.py file, skip." % pkg_path)
            return

        if pkg_path not in sys.path: # settings imported more than one time!
#            print "append to sys.path: %r" % pkg_path
            sys.path.append(pkg_path)

        for plugin_name in os.listdir(pkg_path):
            if plugin_name.startswith(".") or plugin_name.startswith("_"): # e.g. svn dir or __init__.py file
                continue

            if plugin_name in self:
                warnings.warn("Plugin %r exist more than one time." % plugin_name)
                continue

            plugin_pkg = ".".join([section, pkg_dir, plugin_name])

            if not has_init_file(os.path.join(pkg_path, plugin_name)):
                if self.verbose:
                    warnings.warn("plugin '%s' doesn't contain a __init__.py file, skip." % plugin_pkg)
                continue

            if self.verbose:
                print "add plugin %r" % plugin_pkg

            self.installed_plugins.append(plugin_pkg)

            abs_template_path = os.path.join(pkg_path, plugin_name, "templates")
            if os.path.isdir(abs_template_path):
                self.template_dirs.append(abs_template_path)

            additional_settings_path = os.path.join(pkg_path, plugin_name, "additional_settings.py")
            if os.path.isfile(additional_settings_path):
                self.additional_settings.append("%s.additional_settings" % plugin_name)

            self[plugin_name] = (pkg_path, section, pkg_dir)

    def get_additional_settings(self, locals_dict):
        for mod_name in self.additional_settings:
            obj = __import__(mod_name, globals(), locals(), ["add_settings"])
            obj.add_settings(locals_dict)
