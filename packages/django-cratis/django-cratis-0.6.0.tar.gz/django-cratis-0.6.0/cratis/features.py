import sys

class FeatureDependencyFailure(Exception):
    pass


class BaseFeature(object):
    """
    Basement for all the features.
    """
    settings = None

    def set_settings(self, cls):
        """
        Initialized just before configuration process start
        """
        self.settings = cls

    def get_required(self):
        """
        Returns list of classes of features that must be loaded before this feature
        can be loaded
        """
        return ()

    def on_load(self, loaded_features):
        """
        Loads feature. Used by settings class.
        By default, checks requirements and executes configure_settings() method.

        As an argument accepts list of features loaded before current one.
        """

        for requirement in self.get_required():
            if not requirement in loaded_features:
                message = '\n Feature %s depends on %s, that is not loaded yet. Order is also important!\n' % (
                    str(type(self)),
                    str(requirement),
                )
                raise FeatureDependencyFailure(message)

        self.configure_settings()


    def on_after_load(self):
        """
        Called when setting is configured
        """
        pass


    def on_startup(self):
        """
        Last chance to do something after settings are configured, called even later than on_after_load.
        """
        pass


    def configure_settings(self):
        """
        API method.
        Meant to be overridden by subsequent Features.

        Called inside on_load callback.
        """
        pass

    def configure_urls(self, urls):
        """
        API method.
        Meant to be overridden by subsequent Features.

        Called when django imports cratis.url from cratis.urls module.

        As a parameter accepts urlpatterns variable from cratis.urls
        """

    def configure_services(self, binder):
        """
        API method.
        Meant to be overridden by subsequent Features.

        Called when services injector configuration happens

        As a parameter accepts binder instance.

        See python inject for details.
        """


class Feature(BaseFeature):
    """
    Feature add some concreate functionality to the BaseFeature class.
    """

    def append_apps(self, apps):
        """
        Use this in configure_settings, to append new INSTALLED_APPS.
        """

        if isinstance(apps, basestring):
            apps = (apps,)

        for app in apps:
            if app not in self.settings.INSTALLED_APPS:
                self.settings.INSTALLED_APPS += (app,)

    def append_middleware(self, classes):
        """
        Use this in configure_settings, to append new middleware classes.
        """

        if isinstance(classes, basestring):
            classes = (classes,)

        for classname in classes:
            if classname not in self.settings.MIDDLEWARE_CLASSES:
                self.settings.MIDDLEWARE_CLASSES += (classname,)

    def append_template_processor(self, processors):
        """
        Use this in configure_settings, to append new template processors.
        """
        if isinstance(processors, basestring):
            processors = (processors,)

        for classname in processors:
            if classname not in self.settings.TEMPLATE_CONTEXT_PROCESSORS:
                self.settings.TEMPLATE_CONTEXT_PROCESSORS += (classname,)
