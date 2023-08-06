from OFS import metaconfigure
from Products.PloneTestCase.layer import PloneSite
from Testing import ZopeTestCase as ztc
from Zope2.App import zcml


class TestLayer(PloneSite):
    """ layer for integration tests """

    @classmethod
    def setUp(cls):
        metaconfigure.debug_mode = True
        import collective.editskinswitcher
        zcml.load_config('configure.zcml',
                         collective.editskinswitcher)
        zcml.load_config('testing-skins.zcml',
                         collective.editskinswitcher)
        metaconfigure.debug_mode = False
        ztc.installPackage('collective.editskinswitcher')

    @classmethod
    def tearDown(cls):
        pass


class PreviewTestLayer(PloneSite):
    """ layer for preview tests """

    @classmethod
    def setUp(cls):
        metaconfigure.debug_mode = True
        import collective.editskinswitcher
        zcml.load_config('configure.zcml',
                         collective.editskinswitcher)
        zcml.load_config('testing.zcml',
                         collective.editskinswitcher)
        zcml.load_config('testing-skins.zcml',
                         collective.editskinswitcher)
        metaconfigure.debug_mode = False
        ztc.installPackage('collective.editskinswitcher')

    @classmethod
    def tearDown(cls):
        pass
