# Python imports

import extend_me


class Plugin(object):
    """ Base class for all plugins, extensible by name

        (uses metaclass extend_me.ExtensibleByHashType)

        :param erp_proxy: instance of ERP_Proxy to bind plugins to
        :type erp_proxy: openerp_proxy.core.ERP_Proxy instance

        Example of simple plugin::

            from openerp_proxy.plugin import Plugin

            class AttandanceUtils(Plugin):

                # This is required to register Your plugin
                # *name* - is for db.plugins.<name>
                class Meta:
                    name = "attendance"

                def get_sign_state(self):
                    # Note: folowing code works on version 6 of Openerp/Odoo
                    emp_obj = self.proxy['hr.employee']
                    emp_id = emp_obj.search([('user_id', '=', self.proxy.uid)])
                    emp = emp_obj.read(emp_id, ['state'])
                    return emp[0]['state']

        This plugin will automaticaly register itself in system, when module which contains it will be imported.
    """
    __metaclass__ = extend_me.ExtensibleByHashType._('Plugin', hashattr='name')

    def __init__(self, erp_proxy):
        self._erp_proxy = erp_proxy

    @property
    def proxy(self):
        """ Related ERP_Proxy instance
        """
        return self._erp_proxy

    def __repr__(self):
        try:
            name = self.Meta.name
        except AttributeError:
            name = None

        if name is not None:
            return 'openerp_proxy.plugin.Plugin:%s' % name
        return super(Plugin, self).__repr__()


class TestPlugin(Plugin):
    """ Jusn an example plugin to test if plugin logic works
    """

    class Meta:
        name = 'Test'

    def test(self):
        print self.proxy.get_url()


class PluginManager(object):
    """ Class that holds information about all plugins

        :param erp_proxy: instance of ERP_Proxy to bind plugins to
        :type erp_proxy: openerp_proxy.core.ERP_Proxy instance

        Plugiins will be accessible via index or attribute syntax::

            plugins = PluginManager(proxy)
            plugins.Test   # acceps plugin 'Test' as attribute
            plugins['Test']  # access plugin 'Test' via indexing
    """
    def __init__(self, erp_proxy):
        """
        """
        self.__erp_proxy = erp_proxy
        self.__plugins = {}

    def __getitem__(self, name):
        plugin = self.__plugins.get(name, False)
        if plugin is False:
            try:
                pluginCls = type(Plugin).get_class(name)
            except ValueError as e:
                raise KeyError(e.message)

            plugin = pluginCls(self.__erp_proxy)
            self.__plugins[name] = plugin
        return plugin

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __dir__(self):
        res = dir(super(PluginManager, self))
        res.extend(self.registered_plugins)
        return res

    @property
    def registered_plugins(self):
        """ List of names of registered plugins
        """
        return type(Plugin).get_registered_names()

    def refresh(self):
        """ Clean-up plugin cache
            This will force to reinitialize each plugin when asked
        """
        self.__plugins = {}
        return self


