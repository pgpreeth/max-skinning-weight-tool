# Copyright 2019 by Preeth PG, Technical Animator
# All rights reserved.
# This tool is released under the "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

import os
import sys
import logging
import json

import pymel.core as pm

from core import ui_function, utilities
import config

reload(ui_function)
reload(utilities)
reload(config)

# Qt modules
try:
    from PySide2 import QtCore, QtGui
    from PySide2.QtWidgets import QWidget, QMessageBox, QVBoxLayout, QListWidgetItem, QFileDialog
except:
    from PySide import QtCore, QtGui
    from PySide.QtGui import QWidget, QMessageBox, QVBoxLayout, QListWidgetItem, QFileDialog


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
        self.tool_ui.skin_transfer_but.clicked.connect(self.skin_transfer_func)
        self.tool_ui.prune_but.clicked.connect(self.prune_weights)

        self.tool_ui.set_weight_but.clicked.connect(self.set_weight)
        self.tool_ui.add_weight_but.clicked.connect(self.add_weight)
        self.tool_ui.remove_weight_but.clicked.connect(self.subtract_weight)

        self.tool_ui.set_scale_weight_but.clicked.connect(
            self.set_scale_weight)
        self.tool_ui.scale_up_weight_but.clicked.connect(self.scale_up_weight)
        self.tool_ui.scale_down_weight_but.clicked.connect(
            self.scale_down_weight)

        self.tool_ui.preset_0_but.clicked.connect(
            lambda: self.apply_weight(0.0))
        self.tool_ui.preset_0_1_but.clicked.connect(
            lambda: self.apply_weight(0.1))
        self.tool_ui.preset_0_25_but.clicked.connect(
            lambda: self.apply_weight(0.25))
        self.tool_ui.preset_0_5_but.clicked.connect(
            lambda: self.apply_weight(0.5))
        self.tool_ui.preset_0_75_but.clicked.connect(
            lambda: self.apply_weight(0.75))
        self.tool_ui.preset_0_9_but.clicked.connect(
            lambda: self.apply_weight(0.9))
        self.tool_ui.preset_1_0_but.clicked.connect(
            lambda: self.apply_weight(1.0))

        self.tool_ui.vertex_joints_list_widget.itemSelectionChanged.connect(
            self.vertex_joint_list_selection_changed)
        self.tool_ui.skin_joints_list_widget.itemSelectionChanged.connect(
            self.skin_joint_list_selection_changed)

        self.tool_ui.action_save_weight.triggered.connect(self.save_weight)
        self.tool_ui.action_load_weight.triggered.connect(self.load_weight)
        self.tool_ui.action_check_weight.triggered.connect(self.check_weight)

        self.tool_ui.action_help.triggered.connect(self.help)
        self.tool_ui.action_about.triggered.connect(self.about)

        self.update_joint_list_influence()
        self.activate_selection_callback()

    @staticmethod
    def selection_mode(mode):
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
        callback_no = pm.scriptJob(parent='weight_tool_object', e=[
            'SelectionChanged', self.update_joint_list_influence], protected=True)

    def vertex_joint_list_selection_changed(self):
        """
        update the main joint list widget when the joint list item is changed
        """

        selected_joints = self.tool_ui.vertex_joints_list_widget.selectedItems()
        if selected_joints:
            items_in_list = self.tool_ui.skin_joints_list_widget.findItems(
                selected_joints[0].text(), QtCore.Qt.MatchExactly)
            self.tool_ui.skin_joints_list_widget.setCurrentItem(
                items_in_list[0])

    def skin_joint_list_selection_changed(self):
        """
        update the main joint list widget when the joint list item is changed
        """

        selected_joints = self.tool_ui.skin_joints_list_widget.selectedItems()
        if selected_joints:
            items_in_list = self.tool_ui.vertex_joints_list_widget.findItems(
                selected_joints[0].text(), QtCore.Qt.MatchExactly)
            if len(items_in_list):
                self.tool_ui.vertex_joints_list_widget.setCurrentItem(
                    items_in_list[0])

    def update_joint_list_influence(self, selected_joint=None):
        """
        updates the joint list widget with joints info on the selected skin cluster
        """

        selected_object = pm.ls(sl=True, fl=True)
        if selected_object:
            mesh_object = pm.ls(selected_object[0], o=True)
            skin_cluster = utilities.find_skin_cluster(mesh_object[0])
            if skin_cluster is not None:
                self.tool_ui.centralwidget.setEnabled(True)

                joints = utilities.get_all_joints_in_skin(skin_cluster)
                self.tool_ui.skin_joints_list_widget.clear()
                for joint in joints:
                    item = QListWidgetItem(str(joint))
                    self.tool_ui.skin_joints_list_widget.addItem(item)

            if utilities.is_valid_selection():
                for i in selected_object:
                    joint_list = list()
                    weight_list = list()
                    try:
                        weight_list = utilities.get_weights_inf_from_vertices(
                            skin_cluster=skin_cluster, vertices=i)
                        joint_list = utilities.get_joints_inf_from_vertices(
                            skin_cluster=skin_cluster, vertices=i)

                    except:
                        pass

                    self.tool_ui.vertex_joints_list_widget.clear()
                    self.tool_ui.weight_info_list_widget.clear()

                    for joint in joint_list:
                        item = QListWidgetItem(str(joint))
                        self.tool_ui.vertex_joints_list_widget.addItem(item)
                    for weight in weight_list:
                        item = QListWidgetItem(str(round(weight, 3)))
                        self.tool_ui.weight_info_list_widget.addItem(item)
                if selected_joint is not None:
                    items_in_list = self.tool_ui.vertex_joints_list_widget.findItems(
                        selected_joint, QtCore.Qt.MatchExactly)
                    self.tool_ui.vertex_joints_list_widget.setCurrentItem(
                        items_in_list[0])
        else:
            self.tool_ui.centralwidget.setEnabled(False)
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
            if skin_cluster and utilities.is_valid_selection():
                mesh_object = pm.ls(selected_object[0], o=True)
                selected_item = self.tool_ui.skin_joints_list_widget.selectedItems()
                if len(selected_item):
                    selected_joint = selected_item[0].text()
                    for i in selected_object:
                        weight_list = utilities.set_weight(
                            skin_cluster=skin_cluster, vertices=i, joint=selected_joint, value=value)
                        self.update_joint_list_influence(selected_joint)

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
                weight_list = utilities.get_weights_inf_from_vertices(
                    skin_cluster=skin_cluster, vertices=i)
                joint_list = utilities.get_joints_inf_from_vertices(
                    skin_cluster=skin_cluster, vertices=i)
                selected_joint_index = self.tool_ui.skin_joints_list_widget.selectedItems()
                if len(selected_joint_index):
                    selected_joint = selected_joint_index[0].text()

                    for i, joint in enumerate(joint_list):
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
            weight = ((existing_weight * 5) / 100) + get_weight_value
            self.apply_weight(weight)

    def scale_down_weight(self):
        """
        Scale down weight based on the value inside the spinBox
        """

        existing_weight = self.get_weight_to_change()
        if existing_weight is not None:
            get_weight_value = self.tool_ui.scale_weight_val_spin_box.value()
            weight = existing_weight - ((existing_weight * 5) / 100)
            self.apply_weight(weight)

    def copy_vertex_skin_weight(self):
        """
        Copy vertex skin weight to the buffer
        """

        if utilities.is_selection_valid_skin_and_vertices():
            pm.mel.eval('artAttrSkinWeightCopy;')

    def paste_vertex_skin_weight(self):
        """
        Paste vertex skin weight to the buffer
        """
        if utilities.is_selection_valid_skin_and_vertices():
            pm.mel.eval('artAttrSkinWeightPaste;')
            self.update_joint_list_influence()

    def weight_hammer(self):
        """
        Weight hammer the selected vertices
        """
        if utilities.is_selection_valid_skin_and_vertices():
            pm.mel.eval('weightHammerVerts;')
            self.update_joint_list_influence()

    @staticmethod
    def skin_transfer_func():
        """
        Transfer skin-cluster from source to destination.
        """
        transfer_success = utilities.skin_transfer()
        if transfer_success:
            logging.info('Skin Transferred')
        else:
            logging.warning(
                'Please select the valid skin Source and then the target to transfer the skin')

    def prune_weights(self):
        """
        prune the weights by assigned value on the selected mesh
        """

        get_prune_value = self.tool_ui.prune_val_spin_box.value()
        selected_object = pm.ls(sl=True, fl=True)
        if selected_object:
            mesh_object = pm.ls(selected_object[0], o=True)
            skin_cluster = utilities.find_skin_cluster(mesh_object[0])
            pm.skinPercent(
                skin_cluster, mesh_object[0], pruneWeights=get_prune_value)
            self.update_joint_list_influence()

    def save_weight(self):
        """
        Function to save the skin weight of the selected mesh
        """

        directory_path = self.get_directory()
        if directory_path is None:
            return

        selected_objects = pm.ls(sl=True)
        for i in selected_objects:
            vertex = dict()

            skin_cluster = utilities.find_skin_cluster(i)
            if skin_cluster is not None:
                pm.select(i)
                no_of_vertices = pm.polyEvaluate(v=True)
                shape_node = i.getShape()
                g_main_progress_bar = pm.mel.eval('$tmp = $gMainProgressBar');
                pm.progressBar(g_main_progress_bar,
                               edit=True,
                               beginProgress=True,
                               isInterruptable=True,
                               status='"Getting skin info ...',
                               maxValue=no_of_vertices)
                for vertex_no in range(0, no_of_vertices):
                    vertex_skin_info = dict()
                    if pm.progressBar(g_main_progress_bar, query=True, isCancelled=True):
                        break
                    vertices_selection = '{}.vtx[{}]'.format(shape_node, str(vertex_no))
                    joint_list = list()
                    weight_list = list()
                    weight_list = utilities.get_weights_inf_from_vertices(skin_cluster=skin_cluster,
                                                                          vertices=vertices_selection)
                    joint_list = utilities.get_joints_inf_from_vertices(skin_cluster=skin_cluster,
                                                                        vertices=vertices_selection)
                    vertex_skin_info['joint_list'] = joint_list
                    vertex_skin_info['weight_list'] = weight_list
                    vertex[vertices_selection] = vertex_skin_info
                    pm.progressBar(g_main_progress_bar, edit=True, step=1)

                pm.progressBar(g_main_progress_bar, edit=True, endProgress=True)
            path = '{}/{}.skindata'.format(directory_path, i.name())
            with open(path, mode='w') as f:
                f.write(json.dumps(vertex, indent=4, separators=(',', ': ')))
                logging.info('{} skin saved'.format(i.name()))

    def load_weight(self):
        """
        Function to load the skin weight on the selected mesh
        the function looks for a file in the selected directoy of the same name as mesh and loads the skin
        """

        directory_path = self.get_directory()
        if directory_path is None:
            return

        selected_objects = pm.ls(sl=True)
        for i in selected_objects:
            skin_cluster = utilities.find_skin_cluster(i)
            if skin_cluster is not None:

                path = '{}/{}.skindata'.format(directory_path, i.name())
                if not os.path.isfile(path):
                    logging.warning('Skin data file doesnot exist of the name {}.skindata'.format(i.name()))
                    return

                with open(path) as fileJson:
                    try:
                        loaded_dict_from_file = json.load(fileJson)
                    except:
                        logging.warning('Corrupt skin data. {}'.format(path))
                        return
                g_main_progress_bar = pm.mel.eval('$tmp = $gMainProgressBar');
                pm.progressBar(g_main_progress_bar,
                               edit=True,
                               beginProgress=True,
                               isInterruptable=True,
                               status='"loading skin info ...',
                               maxValue=len(loaded_dict_from_file))
                for vertex, skin_info in loaded_dict_from_file.iteritems():
                    for counter, joint in enumerate(skin_info['joint_list']):
                        try:
                            utilities.set_weight(skin_cluster=skin_cluster, vertices=vertex, joint=joint,
                                                 value=skin_info['weight_list'][counter])
                            pm.progressBar(g_main_progress_bar, edit=True, step=1)
                        except:
                            logging.warning('Skin data not matching the selected mesh. {}'.format(i.name()))
                            return
                pm.progressBar(g_main_progress_bar, edit=True, endProgress=True)

                logging.info('{} skin data loaded on {} sucessfully'.format(path, i.name()))

    def get_directory(self):
        """
        Opens a file dialog to choose a directory
        """

        directory_path = str(
            QFileDialog.getExistingDirectory(self, "Select Directory", options=QFileDialog.ShowDirsOnly, dir='c:/'))
        if directory_path is not "":
            return directory_path
        return None

    @staticmethod
    def check_weight():
        """
        Function to check joint weight on vertex
        """

        logging.warning('This feature is not available currently')

    @staticmethod
    def help():
        """
        Function to load the help link
        """

        web_path = 'start {}'.format(config.HELP_PATH)
        os.system(web_path)

    def about(self):
        """
        Function 
        """

        about_box = QMessageBox()
        about_text = "Skinning weight Tool like Max Weight tool"
        about_text = "{} \nVersion : {}".format(about_text, config.VERSION)
        about_box.about(self, 'Max Skinning Weight Tool', about_text)
        about_box.setWindowIcon(QtGui.QIcon(config.ICON_PATH + '/icon.png'))


def show():
    """
    Loads the QWidget Weight Tool to the Maya environment
    """

    window_title = '{} - {}'.format(config.TOOL_NAME, config.VERSION)
    ui_function.maya_workspace_docker(MaxSkinningWeightTool, window_title)
