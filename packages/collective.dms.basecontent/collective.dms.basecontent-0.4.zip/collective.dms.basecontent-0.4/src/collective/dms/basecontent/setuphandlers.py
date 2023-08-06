def setup_documentviewer(portal):
    from collective.documentviewer.settings import GlobalSettings
    dv_settings = GlobalSettings(portal)
    dv_settings.auto_layout_file_types = ('pdf', 'ppt', 'word', 'rft')
    dv_settings.auto_convert = True
    dv_settings.show_sidebar = False
    dv_settings.show_search = False


def importFinalSteps(context):
    """Import all final steps.
    """
    marker = context.readDataFile('collective_dms_basecontent_marker.txt')
    if marker is None:
        return

    site = context.getSite()
    setup_documentviewer(site)
