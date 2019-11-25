import pymel.core as pm
import config
import sys
import logging

from core import ui_function, utilities
reload(ui_function)
reload(utilities)

reload(config)


# Qt modules
try:
    from PySide2 import QtCore, QtGui
    from PySide2.QtWidgets import QWidget, QMenu, QAction, \
        QFileDialog, QInputDialog, QMessageBox, QVBoxLayout, QApplication, QListWidgetItem
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
        self.tool_ui = ui_function.load_ui_file(config.UI_FILE, parent)
        layout.addWidget(self.tool_ui)
        self.setLayout(layout)
        self.setObjectName('weight_tool_object')
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        self.setWindowTitle('%s - %s' % (config.TOOL_NAME, config.VERSION))
        self.setWindowIcon(QtGui.QIcon(config.ICON_PATH + '/weight_tool.png'))

        self.tool_ui.grow_but.clicked.connect(lambda: self.selection_mode(1))
        self.tool_ui.shrink_but.clicked.connect(lambda: self.selection_mode(2))
        self.tool_ui.loop_but.clicked.connect(lambda: self.selection_mode(3))
        self.tool_ui.ring_but.clicked.connect(lambda: self.selection_mode(4))
        self.tool_ui.copy_but.clicked.connect(self.copy_vertex_skin_weight)
        self.tool_ui.paste_but.clicked.connect(self.paste_vertex_skin_weight)
        self.tool_ui.weight_hammer_but.clicked.connect(self.weight_hammer)

        self.tool_ui.set_weight_but.clicked.connect(self.set_weight)
        self.tool_ui.add_weight_but.clicked.connect(self.add_weight)
        self.tool_ui.remove_weight_but.clicked.connect(self.subtract_weight)

        self.tool_ui.set_scale_weight_but.clicked.connect(self.set_scale_weight)
        self.tool_ui.scale_up_weight_but.clicked.connect(self.scale_up_weight)
        self.tool_ui.scale_down_weight_but.clicked.connect(self.scale_down_weight)

        self.tool_ui.preset_0_but.clicked.connect(lambda: self.apply_weight(0.0))
        self.tool_ui.preset_0_1_but.clicked.connect(lambda: self.apply_weight(0.1))
        self.tool_ui.preset_0_25_but.clicked.connect(lambda: self.apply_weight(0.25))
        self.tool_ui.preset_0_5_but.clicked.connect(lambda: self.apply_weight(0.5))
        self.tool_ui.preset_0_75_but.clicked.connect(lambda: self.apply_weight(0.75))
        self.tool_ui.preset_0_9_but.clicked.connect(lambda: self.apply_weight(0.9))
        self.tool_ui.preset_1_0_but.clicked.connect(lambda: self.apply_weight(1.0))

        self.tool_ui.vertex_joints_list_widget.itemSelectionChanged.connect(self.vertex_joint_list_selection_changed)
        self.tool_ui.skin_joints_list_widget.itemSelectionChanged.connect(self.skin_joint_list_selection_changed)

        self.update_joint_list_influence()
        self.activate_selection_callback()

    def selection_mode(self, mode):
        """
        Function for vertex selection mode buttons
        """

        if mode == 1:
            pm.mel.eval('PolySelectTraverse 1')
        elif mode == 2:
            pm.mel.eval('PolySelectTraverse 2')
        elif mode == 3:
            pm.polySelectSp(loop=True)
        elif mode == 4:
            pm.polySelectSp(ring=True)

    def activate_selection_callback(self):
        """
        Activate script job for selection change tool update
        """

        callback_no = int()
        if callback_no:
            pm.scriptJob(kill=callback_no)
        callback_no = pm.scriptJob(parent='weight_tool_object', e=['SelectionChanged', self.update_joint_list_influence], protected=True)

    def vertex_joint_list_selection_changed(self):
        """
        update the main joint list widget when the joint list item is changed
        """

        selected_joints = self.tool_ui.vertex_joints_list_widget.selectedItems()
        if selected_joints:
            items_in_list = self.tool_ui.skin_joints_list_widget.findItems(selected_joints[0].text(), QtCore.Qt.MatchExactly)
            self.tool_ui.skin_joints_list_widget.setCurrentItem(items_in_list[0])


    def skin_joint_list_selection_changed(self):
        """
        update the main joint list widget when the joint list item is changed
        """

        selected_joints = self.tool_ui.skin_joints_list_widget.selectedItems()
        if selected_joints:
            items_in_list = self.tool_ui.vertex_joints_list_widget.findItems(selected_joints[0].text(), QtCore.Qt.MatchExactly)
            if len(items_in_list):
                self.tool_ui.vertex_joints_list_widget.setCurrentItem(items_in_list[0])


    def update_joint_list_influence(self):
        """
        updates the joint list widget with joints info on the selected skin cluster
        """

        selected_object = pm.ls(sl=True, fl=True)
        if selected_object:
            mesh_object = pm.ls(selected_object[0], o=True)
            skin_cluster = utilities.find_skin_cluster(mesh_object[0])
            if skin_cluster is not None:
                joints = utilities.get_all_joints_in_skin(skin_cluster)
                self.tool_ui.skin_joints_list_widget.clear()
                for joint in joints:
                    item = QListWidgetItem(str(joint))
                    self.tool_ui.skin_joints_list_widget.addItem(item)

            if utilities.is_valid_selection():
                mesh_object = pm.ls(selected_object[0], o=True)
                skin_cluster = utilities.find_skin_cluster(mesh_object[0])
                for i in selected_object:
                    weight_list = utilities.get_weights_inf_from_vertices(skin_cluster=skin_cluster, vertices=i)
                    joint_list = utilities.get_joints_inf_from_vertices(skin_cluster=skin_cluster, vertices=i)
                    self.tool_ui.vertex_joints_list_widget.clear()
                    self.tool_ui.weight_info_list_widget.clear()

                    for joint in joint_list:
                        item = QListWidgetItem(str(joint))
                        self.tool_ui.vertex_joints_list_widget.addItem(item)
                        self.tool_ui.vertex_joints_list_widget.setCurrentItem(item)
                    for weight in weight_list:
                        item = QListWidgetItem(str(round(weight, 3)))
                        self.tool_ui.weight_info_list_widget.addItem(item)
        else:
            self.tool_ui.weight_info_list_widget.clear()
            self.tool_ui.vertex_joints_list_widget.clear()
            self.tool_ui.skin_joints_list_widget.clear()

    def apply_weight(self, value):
        """
        Apply weight value to the vertices
        """

        selected_object = pm.ls(sl=True, fl=True)
        if selected_object:
            mesh_object = pm.ls(selected_object[0], o=True)
            skin_cluster = utilities.find_skin_cluster(mesh_object[0])
            if utilities.is_valid_selection():
                mesh_object = pm.ls(selected_object[0], o=True)
                for i in selected_object:
                    selected_joint = self.tool_ui.skin_joints_list_widget.selectedItems()[0].text()
                    weight_list = utilities.set_weight(skin_cluster=skin_cluster, vertices=i, joint=selected_joint, value=value)
                    self.update_joint_list_influence()
                    print ('Preeth')

        else:
            logging.info('Weight not set') 

    def set_weight(self):
        """
        Function for setting weight from the set value inside the spinBox widget
        """

        get_weight_value = self.tool_ui.add_rem_weight_val_spin_box.value()
        self.apply_weight(get_weight_value)

    def set_scale_weight(self):
        """
        Function for scaling weight from the set value inside the spinBox widget
        """

        get_weight_value = self.tool_ui.scale_weight_val_spin_box.value()
        self.apply_weight(get_weight_value)

    def get_weight_to_change(self):
        """
        get weight from the joint list for the selected vertices for adding and scaling. etc
        """

        selected_object = pm.ls(sl=True, fl=True)
        if selected_object:
            mesh_object = pm.ls(selected_object[0], o=True)
            skin_cluster = utilities.find_skin_cluster(mesh_object[0])

            for i in selected_object:
                weight_list = utilities.get_weights_inf_from_vertices(skin_cluster=skin_cluster, vertices=i)
                joint_list = utilities.get_joints_inf_from_vertices(skin_cluster=skin_cluster, vertices=i)
                selected_joint = self.tool_ui.skin_joints_list_widget.selectedItems()[0].text()

                for i,joint in enumerate(joint_list):
                    if joint == selected_joint:
                        get_weight = weight_list[i]
                        return get_weight
        return None

    def add_weight(self):
        """
        Increment weight based on the value inside the spinBox
        """

        existing_weight = self.get_weight_to_change()
        if existing_weight is not None:
            get_weight_value = self.tool_ui.add_rem_weight_val_spin_box.value()
            weight = existing_weight + get_weight_value
            self.apply_weight(weight)

    def subtract_weight(self):
        """
        decrement weight based on the value inside the spinBox
        """

        existing_weight = self.get_weight_to_change()
        if existing_weight is not None:
            get_weight_value = self.tool_ui.add_rem_weight_val_spin_box.value()
            weight = existing_weight - get_weight_value
            self.apply_weight(weight)

    def scale_up_weight(self):
        """
        Scale up weight based on the value inside the spinBox
        """

        existing_weight = self.get_weight_to_change()
        if existing_weight is not None:
            get_weight_value = self.tool_ui.scale_weight_val_spin_box.value()
            weight = ((existing_weight * 5)/100) + get_weight_value
            self.apply_weight(weight)

    def scale_down_weight(self):
        """
        Scale down weight based on the value inside the spinBox
        """

        existing_weight = self.get_weight_to_change()
        if existing_weight is not None:
            get_weight_value = self.tool_ui.scale_weight_val_spin_box.value()
            weight = existing_weight - ((existing_weight * 5)/100)
            self.apply_weight(weight)

    def copy_vertex_skin_weight(self):
        """
        Copy vertex skin weight to the buffer
        """
        pm.mel.eval('artAttrSkinWeightCopy;')


    def paste_vertex_skin_weight(self):
        """
        Paste vertex skin weight to the buffer
        """

        pm.mel.eval('artAttrSkinWeightPaste;')
        self.update_joint_list_influence()


    def weight_hammer(self):
        """
        Weight hammer the selected vertices
        """

        pm.mel.eval('weightHammerVerts;')
        self.update_joint_list_influence()

def show():
    """
    Loads the QWidget Weight Tool to the Maya environment
    """

    window_title = '{} - {}'.format(config.TOOL_NAME, config.VERSION)
    ui_function.maya_workspace_docker(MaxSkinningWeightTool, window_title)
