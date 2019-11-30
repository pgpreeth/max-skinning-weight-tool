try:
    from PySide2 import QtCore, QtWidgets, QtUiTools
    from shiboken2 import wrapInstance
except:
    from PySide import QtCore, QtWidgets, QtUiTools

import maya.OpenMayaUI as omui
import pymel.core as pm


def load_ui_file(ui_file_path, parent=None):
    """
    Simple UI loader function
    """

    loader = QtUiTools.QUiLoader()
    ui_file = QtCore.QFile(ui_file_path)
    ui_file.open(QtCore.QFile.ReadOnly)
    ui = loader.load(ui_file, parent)
    ui_file.close()
    return ui


def maya_workspace_docker(qt_widget, window_title):
    """
    qt maya docker
    """

    label = getattr(qt_widget, "label", window_title)
    try:
        pm.deleteUI(window_title)
    except RuntimeError:
        pass

    workspace_control = pm.workspaceControl(
        window_title, tabToControl=["AttributeEditor", -1], label=label)
    workspace_pointer = omui.MQtUtil.findControl(workspace_control)
    wrap_widget = wrapInstance(long(workspace_pointer), QtWidgets.QWidget)
    wrap_widget.setAttribute(QtCore.Qt.WA_DeleteOnClose)
    # wrap_widget.destroyed.connect(close)
    child = qt_widget(wrap_widget)
    wrap_widget.layout().addWidget(child)
    pm.evalDeferred(
        lambda *args: pm.workspaceControl(workspace_control, edit=True, restore=True))
