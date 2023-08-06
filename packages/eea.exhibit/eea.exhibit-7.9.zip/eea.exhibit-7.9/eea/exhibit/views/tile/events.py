""" Handle events
"""
from eea.app.visualization.views.events import facet_deleted

def tile_facet_deleted(obj, evt):
    """ Cleanup removed facet from view properties
    """
    return facet_deleted(obj, evt, 'daviz.tile')
