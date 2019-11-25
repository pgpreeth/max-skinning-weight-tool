import pymel.core as pm
from collections import namedtuple


def find_skin_cluster(mesh):
    """
    find the skincluster of a given mesh
    """

    skin_cluster = pm.mel.eval('findRelatedSkinCluster ' + mesh)
    if skin_cluster:
        return skin_cluster
    return None

def get_all_joints_in_skin(skin_cluster):
    """
    return all joints inside a skincluster
    """

    joints = pm.skinCluster(skin_cluster, query=True, inf=True)
    if len(joints):
        return joints
    return None

def set_weight(skin_cluster, vertices, joint, value):
    """
    set the weight of the vertices by assigned value
    """

    pm.skinPercent(skin_cluster, vertices, transformValue=[(joint, value)])


def get_weights_inf_from_vertices(skin_cluster=None, joint=None, vertices=None):
    """
    gets the weight of the vertices and also based of assigned/specified joint
    return value list
    """

    if joint is None:
        weight = pm.skinPercent(skin_cluster, vertices,ignoreBelow=0.0001, query=True, value=True)
    else:
        weight = [pm.skinPercent(
            skin_cluster, vertices, transform=joint, ignoreBelow=0.0001, query=True, value=True)]

    return weight

def get_joints_inf_from_vertices(skin_cluster=None, vertices=None):
    """
    get joint list from a given vertices
    """

    joints = pm.skinPercent(skin_cluster, vertices, ignoreBelow=0.0001, query=True, transform=None)
    if len(joints):
        return joints
    return None


def get_selected_components():
    """
    get selection type
    """

    selection_type = namedtuple('selectiontype', 'faces verts edges')
    pm.selectPref(trackSelectionOrder=True)
    sel = pm.ls(sl=True, type='float3')
    faces = pm.polyListComponentConversion(sel, ff=True, tf=True)
    verts = pm.polyListComponentConversion(sel, fv=True, tv=True)
    edges = pm.polyListComponentConversion(sel, fe=True, te=True)
    return selection_type(faces, verts, edges)


def is_valid_selection():
    """
    Check if the selection of the component is valid. (ie) vertices
    """

    get_selected_component = get_selected_components()
    if len(get_selected_component[1]):
        return True
    return False
