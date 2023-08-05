"""
Default settings for cratis project
"""
import inject
import os

from configurations import Configuration


class CratisConfig(Configuration):
    """
    Base class for Configurations that will be used with cratis.

    Class contains hooks pre_setup and post_setup that will load
    and configure Features defined in FEATURES settings variable.

    Also class defines ROOT_URLCONF settings variable, that use cratis.urls
    to load all urls collected from your Features. Usually you wouldn't change this
    when working with cratis.

    BASE_DIR just points to project directory, so you can specify paths relatively, ex:

    STATIC_ROOT = os.path.join(CratisConfig.BASE_DIR, 'some dir')

    Order of Feature load is following:

     - Call set_settings() on each Feature, providing class reference, so Feature can save it for future use.
     - Call do_load() on each Feature, passing previously loaded feature list as an argument
     - .. now django-configurations executes own internal things..
     - Django is fully configured, we run on_after_load on each Feature, so Features can do latest adjustments
     - And finally call on_startup() on each feature, features shouldn't modify anything on this step.

    """

    BASE_DIR = os.environ.get('CRATIS_APP_PATH', '.')
    ROOT_URLCONF = 'cratis.urls'

    FEATURES = ()

    @classmethod
    def pre_setup(cls):
        super(CratisConfig, cls).pre_setup()

        loaded_features = []
        for feature in cls.FEATURES:
            feature.set_settings(cls)
            feature.on_load(loaded_features)
            loaded_features.append(type(feature))


    @classmethod
    def post_setup(cls):
        super(CratisConfig, cls).post_setup()

        def configure_feature_services(binder):
            for feature in cls.FEATURES:
                feature.configure_services(binder)

        inject.configure(configure_feature_services)

        for feature in cls.FEATURES:
            feature.on_after_load()

        for feature in cls.FEATURES:
            feature.on_startup()

    @classmethod
    def override_feature(cls, feature):
        cls.FEATURES = tuple([x if not isinstance(x, type(feature)) else feature for x in cls.FEATURES])

    @classmethod
    def add_feature(cls, feature):
        cls.FEATURES += (feature,)



