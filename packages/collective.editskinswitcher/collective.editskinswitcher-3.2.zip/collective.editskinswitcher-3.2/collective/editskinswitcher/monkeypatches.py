### Cleanest way to add the drop down to the property sheet ... until
### plone property sheets do zope vocab lookups!
from AccessControl.class_init import InitializeClass
from Products.CMFPlone.PropertiesTool import SimpleItemWithProperties
from collective.editskinswitcher.config import SWITCH_SKIN_OPTIONS


def editSwitchList(self):
    """ Options for switch_skin_action property """
    return SWITCH_SKIN_OPTIONS

setattr(SimpleItemWithProperties, 'editSwitchList', editSwitchList)
InitializeClass(SimpleItemWithProperties)
