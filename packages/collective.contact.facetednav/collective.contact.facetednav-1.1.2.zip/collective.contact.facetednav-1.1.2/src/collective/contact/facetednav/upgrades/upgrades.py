from ecreall.helpers.upgrade.interfaces import IUpgradeTool


def v2(context):
    tool = IUpgradeTool(context)
    tool.runProfile('collective.contact.facetednav.upgrades:v2')

def v3(context):
    tool = IUpgradeTool(context)
    tool.runImportStep('collective.contact.facetednav', 'actions')
    tool.runImportStep('collective.contact.facetednav', 'jsregistry')

def v4(context):
    tool = IUpgradeTool(context)
    tool.refreshResources()