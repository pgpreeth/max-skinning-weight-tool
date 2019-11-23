import pymel.core as pm
import config
import sys
import core.utilities as utilities
reload(utilities)

reload(config)


# Qt modules
try:
    from PySide2 import QtCore, QtGui
    from PySide2.QtWidgets import QWidget, QMenu, QAction, \
        QFileDialog, QInputDialog, QMessageBox, QVBoxLayout, QApplication
except:
    from PySide import QtCore, QtGui
    from PySide.QtGui import QWidget, QMenu, QAction, \
        QFileDialog, QInputDialog, QMessageBox, QVBoxLayout, QApplication


class MaxSkinningWeightTool(QWidget):
    """
    Max Skinning Weight Tool for Maya
    """

    def __init__(self, parent=None):

        super(MaxSkinningWeightTool, self).__init__(parent=parent)
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setMargin(0)
        self.weight_tool_ui = utilities.load_ui_file(config.UI_FILE, parent)
        layout.addWidget(self.weight_tool_ui)
        self.setLayout(layout)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        self.setWindowTitle('%s - %s' % (config.TOOL_NAME, config.VERSION))
        self.setWindowIcon(QtGui.QIcon(config.ICON_PATH + '/weight_tool.png'))


def show():
    """
    Loads the QWidget Weight Tool to the Maya environment
    """

    window_title = '%s - %s' % (config.TOOL_NAME, config.VERSION)
    utilities.maya_workspace_docker(MaxSkinningWeightTool, window_title)
