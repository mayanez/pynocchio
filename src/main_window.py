# -*- coding:utf-8 -*-

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4 import uic

import model
import recent_files_manager
import status_bar

MainWindowForm, MainWindowBase = uic.loadUiType('../view/main_window.ui')


class MainWindow(MainWindowBase, MainWindowForm):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        self.model = model.Model(self)
        self.scroll_area_viewer.model = self.model
        self.scroll_area_viewer.label = self.label

        self.statusbar = status_bar.StatusBar(self)
        self.setStatusBar(self.statusbar)

        self.on_action_show_statusbar_triggered()
        self.on_action_show_toolbar_triggered()

        self._create_action_group_view()
        self.action_about_qt.setIcon(QtGui.QIcon(':/trolltech/qmessagebox/images/qtlogo-64.png'))

        actions = []

        for i in range(5):
            act = QtGui.QAction(self)
            act.setVisible(False)
            act.triggered.connect(self._on_action_recent_files)
            act.setObjectName(str(i))
            actions.append(act)
            self.menu_recent_files.addAction(act)

        self.recentFileManager = recent_files_manager.RecentFileManager(actions)
        self._load_settings()
        self._init_bookmark_menu()
        self._adjust_main_window()
        self._define_global_shortcuts()

    def _adjust_main_window(self):
        screen = QtGui.QDesktopWidget().screenGeometry()
        size = self.geometry()
        x_center = (screen.width() - size.width()) / 2
        y_center = (screen.height() - size.height()) / 2
        self.move(x_center, y_center)
        self.setMinimumSize(QtGui.QApplication.desktop().screenGeometry().size() * 0.8)

    def _define_global_shortcuts(self):

        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+Shift+Left"), self, self.on_action_previous_comic_triggered)
        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+Left"), self, self.on_action_first_page_triggered)
        QtGui.QShortcut(QtGui.QKeySequence("Left"), self, self.on_action_previous_page_triggered)
        QtGui.QShortcut(QtGui.QKeySequence("Right"), self, self.on_action_next_page_triggered)
        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+Right"), self, self.on_action_last_page_triggered)
        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+Shift+Right"), self, self.on_action_next_comic_triggered)

        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+R"), self, self.on_action_rotate_right_triggered)
        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+Shift+R"), self, self.on_action_rotate_left_triggered)

    def _create_action_group_view(self):
        self.actionGroupView = QtGui.QActionGroup(self)

        self.actionGroupView.addAction(self.action_original_fit)
        self.actionGroupView.addAction(self.action_vertical_adjust)
        self.actionGroupView.addAction(self.action_horizontal_adjust)
        self.actionGroupView.addAction(self.action_best_fit)

        checked_action = self.actionGroupView.checkedAction()
        self.model.adjustType = checked_action.text()

        self.action_original_fit.triggered.connect(self._on_action_group_view_adjust)
        self.action_vertical_adjust.triggered.connect(self._on_action_group_view_adjust)
        self.action_horizontal_adjust.triggered.connect(self._on_action_group_view_adjust)
        self.action_best_fit.triggered.connect(self._on_action_group_view_adjust)

    def load(self, path, initial_page=0):

        if self.model.load_comic(path, initial_page):
            self.scroll_area_viewer.label.setPixmap(self.model.get_current_page())
            self.setWindowTitle(self.model.comic.name)
            self._update_status_bar()
            self._enable_actions()
            self.recentFileManager.update_recent_file_list(path)
            self.model.current_directory = path
            self.model.verify_comics_in_path(self.action_next_comic, self.action_previous_comic)
        else:
            QtGui.QMessageBox().information(self, self.tr('Error'), self.tr("Error to load file ") + path)

        self._update_view_actions()

    @QtCore.pyqtSlot()
    def on_action_open_triggered(self):

        file_path = QtGui.QFileDialog().getOpenFileName(
            self, self.tr('Open comic file'), self.model.current_directory,
            self.tr('All supported files (*.zip *.cbz *.rar *.cbr *.tar *.cbt);; '
                    'Zip Files (*.zip *.cbz);; Rar Files (*.rar *.cbr);; '
                    'Tar Files (*.tar *.cbt);; All files (*)'))

        if file_path:
            self.load(file_path)

    # @QtCore.pyqtSlot()
    # def on_action_open_folder_triggered(self):
    #     path = QtGui.QFileDialog.getExistingDirectory(
    #         self.parent(), self.tr("Open Directory"), QtCore.QDir.currentPath(),
    #         QtGui.QFileDialog.ShowDirsOnly)
    #
    #     if not path:
    #         return
    #
    #     if self.model.load_folder(path):
    #         pix_map = self.model.get_current_page()
    #
    #         if pix_map:
    #             self.scroll_area_viewer.label.setPixmap(pix_map)
    #             self.setWindowTitle(self.model.comic.name)
    #             self._update_status_bar()
    #             self._enable_actions()
    #         else:
    #             QtGui.QMessageBox.information(self, self.tr('Error'), self.tr("Folder don't have image files!!"))
    #     else:
    #         QtGui.QMessageBox.information(self, self.tr('Error'), self.tr("Error to load folder!!") + path)

    def _on_action_recent_files(self):
        action = self.sender()
        if action:
            path = self.recentFileManager.get_action_path(action.objectName())
            self.load(path)

    @QtCore.pyqtSlot()
    def on_action_next_page_triggered(self):
        self.scroll_area_viewer.next_page()
        self._update_status_bar()
        self._update_view_actions()

    @QtCore.pyqtSlot()
    def on_action_previous_page_triggered(self):
        self.scroll_area_viewer.previous_page()
        self._update_status_bar()
        self._update_view_actions()

    @QtCore.pyqtSlot()
    def on_action_first_page_triggered(self):
        self.scroll_area_viewer.first_page()
        self._update_status_bar()
        self._update_view_actions()

    @QtCore.pyqtSlot()
    def on_action_last_page_triggered(self):
        self.scroll_area_viewer.last_page()
        self._update_status_bar()
        self._update_view_actions()

    @QtCore.pyqtSlot()
    def on_action_go_to_page_triggered(self):
        import go_to_dialog
        go_to_dlg = go_to_dialog.GoToDialog(self.model, self.scroll_area_viewer)
        go_to_dlg.show()
        go_to_dlg.exec_()
        self._update_view_actions()

    @QtCore.pyqtSlot()
    def on_action_next_comic_triggered(self):
        file_name = self.model.next_comic()
        if file_name:
            self.load(file_name)

    @QtCore.pyqtSlot()
    def on_action_previous_comic_triggered(self):
        file_name = self.model.previous_comic()
        if file_name:
            self.load(file_name)

    @QtCore.pyqtSlot()
    def on_action_rotate_left_triggered(self):
        self.scroll_area_viewer.rotate_left()

    @QtCore.pyqtSlot()
    def on_action_rotate_right_triggered(self):
        self.scroll_area_viewer.rotate_right()

    @QtCore.pyqtSlot()
    def on_action_fullscreen_triggered(self):

        if self.isFullScreen():
            self.menubar.show()
            self._update_view_actions()
            self.showMaximized()
            self.on_action_show_toolbar_triggered()
            self.on_action_show_statusbar_triggered()
            self._update_status_bar()
        else:
            self.showFullScreen()
            self.toolbar.hide()
            self.menubar.hide()
            self.statusbar.hide()

    def _on_action_group_view_adjust(self):
        action = self.sender()

        if action:
            checked_action = action
            self.model.adjustType = checked_action.objectName()
            self.scroll_area_viewer.label.setPixmap(self.model.get_current_page())
            self._update_status_bar()

    def _init_bookmark_menu(self):
        for i in range(0, self.model.NUM_BOOKMARK):
            act = QtGui.QAction(self)
            act.setVisible(False)
            act.triggered.connect(self._load_bookmark)
            self.menu_Bookmarks.addAction(act)

        self._update_bookmarks_menu(self.model.get_bookmark_list(self.model.NUM_BOOKMARK))

    def _update_bookmarks_menu(self, bookmark_list=None):
        acts = self.menu_Bookmarks.actions()

        if not bookmark_list:
            bookmark_list = self.model.get_bookmark_list(self.model.NUM_BOOKMARK)

        bookmark_list_len = len(bookmark_list)

        # Added 4 because the 3 actions in bookmark menu is add, remove and manage bookmark
        for i in range(0, bookmark_list_len):
            page = ' [%d]' % (bookmark_list[i][2])
            acts[i+4].setObjectName(bookmark_list[i][0])
            acts[i+4].setText(bookmark_list[i][0] + page)
            acts[i+4].setVisible(True)

        # make the others bookmarks items invisibles
        for i in range(bookmark_list_len, self.model.NUM_BOOKMARK):
            acts[i+4].setVisible(False)

    @QtCore.pyqtSlot()
    def on_action_add_bookmark_triggered(self):
        self._update_bookmarks_menu(self.model.add_bookmark())

    @QtCore.pyqtSlot()
    def on_action_remove_bookmark_triggered(self):
        self._update_bookmarks_menu(self.model.remove_bookmark())

    @QtCore.pyqtSlot()
    def on_action_bookmark_manager_triggered(self):
        import bookmark_manager_dialog
        bookmark_dialog = bookmark_manager_dialog.BookmarkManagerDialog(self.model, self)
        bookmark_dialog.show()
        bookmark_dialog.exec_()

        item_to_open = bookmark_dialog.item_to_open
        if item_to_open:
            self.load(item_to_open)

        self._update_bookmarks_menu(self.model.get_bookmark_list(self.model.NUM_BOOKMARK))

    def _load_bookmark(self):
        action = self.sender()
        if action:
            bk = self.model.find_bookmark(action.objectName())
            self.load(action.objectName(), bk[2] - 1)

    @QtCore.pyqtSlot()
    def on_action_show_toolbar_triggered(self):
        if self.action_show_toolbar.isChecked():
            self.toolbar.show()
        else:
            self.toolbar.hide()

    @QtCore.pyqtSlot()
    def on_action_show_statusbar_triggered(self):
        if self.action_show_statusbar.isChecked():
            self._update_status_bar()
            self.statusbar.show()
        else:
            self.statusbar.hide()

    @QtCore.pyqtSlot()
    def on_action_about_triggered(self):
        # import about_dialog
        # about_dlg = about_dialog.AboutDialog(self)
        # about_dlg.show()
        # about_dlg.exec_()

        msg = "<p align=\"left\"> The <b>Pynocchio Comic Reader</b> " \
              "is an image viewer specifically designed to handle comic books.</p>" + \
              "<p align=\"left\">It reads ZIP, RAR and tar archives, as well as plain image files." +\
              "<p align=\"left\">Pynocchio Comic Reader is licensed under the GNU General Public License." + \
              "<p align=\"left\">Copyright 2014 Michell Stuttgart Faria</p>" + \
              "<p align=\"left\">Pynocchio use http://freeiconmaker.com to build icon set. " + \
              "Icons pack by Icon Sweets 2 and Streamline icon set free pack.</p>"

        QtGui.QMessageBox().about(self, self.tr("About Pynocchio Comic Reader"), msg)

    @QtCore.pyqtSlot()
    def on_action_about_qt_triggered(self):
        QtGui.QMessageBox.aboutQt(self, self.tr(u'About Qt'))

    @QtCore.pyqtSlot()
    def on_action_exit_triggered(self):
        self._save_settings()
        self.recentFileManager.save_settings()
        super(MainWindow, self).close()

    def _update_view_actions(self):

        if not self.model.comic:
            return

        if self.model.is_last_page():
            self.action_next_page.setEnabled(False)
            self.action_last_page.setEnabled(False)
            self.action_previous_page.setEnabled(True)
            self.action_first_page.setEnabled(True)
        elif self.model.is_first_page():
            self.action_previous_page.setEnabled(False)
            self.action_first_page.setEnabled(False)
            self.action_next_page.setEnabled(True)
            self.action_last_page.setEnabled(True)
        else:
            self.action_next_page.setEnabled(True)
            self.action_last_page.setEnabled(True)
            self.action_previous_page.setEnabled(True)
            self.action_first_page.setEnabled(True)

    def _update_status_bar(self):

        if self.statusbar.isVisible() and self.model.comic:

            n_page = self.model.comic.get_current_page_number()
            pages_size = self.model.comic.get_number_of_pages()
            page_width = self.model.get_current_page().width()
            page_height = self.model.get_current_page().height()
            page_title = self.model.comic.get_current_page_title()

            self.statusbar.set_comic_page(n_page, pages_size)
            self.statusbar.set_page_resolution(page_width, page_height)
            self.statusbar.set_comic_path(page_title)

    def _enable_actions(self):

        self.action_fullscreen.setEnabled(True)
        self.action_original_fit.setEnabled(True)
        self.action_best_fit.setEnabled(True)
        self.action_horizontal_adjust.setEnabled(True)
        self.action_vertical_adjust.setEnabled(True)
        self.action_rotate_left.setEnabled(True)
        self.action_rotate_right.setEnabled(True)

        self.action_next_page.setEnabled(True)
        self.action_last_page.setEnabled(True)
        self.action_go_to_page.setEnabled(True)
        self.action_next_comic.setEnabled(True)
        self.action_previous_comic.setEnabled(True)

        self.action_add_bookmark.setEnabled(True)
        self.action_remove_bookmark.setEnabled(True)

    def _save_settings(self):
        import settings_manager
        sett = {'view': {}, 'settings': {}}

        sett['view']['view_adjust'] = self.actionGroupView.checkedAction().objectName()
        sett['settings']['show_toolbar'] = self.action_show_toolbar.isChecked()
        sett['settings']['show_statusbar'] = self.action_show_statusbar.isChecked()
        sett['settings']['directory'] = self.model.current_directory

        settings_manager.SettingsManager.save_settings(sett, 'settings.ini')

    def _load_settings(self):
        import settings_manager
        from distutils import util

        sett = settings_manager.SettingsManager.load_settings('settings.ini')

        try:
            self.action_show_toolbar.setChecked(util.strtobool(sett['settings']['show_toolbar']))
            self.action_show_statusbar.setChecked(util.strtobool(sett['settings']['show_statusbar']))

            for act in self.actionGroupView.actions():
                if act.objectName() == sett['view']['view_adjust']:
                    act.setChecked(True)
                    self.model.adjustType = act.text()

            self.model.current_directory = sett['settings']['directory']

        except KeyError, err:
            print err

        self.on_action_show_toolbar_triggered()
        self.on_action_show_statusbar_triggered()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_F:
            self.on_action_fullscreen_triggered()
        elif event.key() == QtCore.Qt.Key_Escape and self.isFullScreen():
            self.on_action_fullscreen_triggered()
        else:
            super(MainWindow, self).keyPressEvent(event)

    def mouseDoubleClickEvent(self, *args, **kwargs):
        if args[0].button() == QtCore.Qt.LeftButton:
            self.on_action_fullscreen_triggered()
        else:
            super(MainWindow, self).mousePressEvent(*args, **kwargs)
