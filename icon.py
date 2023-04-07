from PySide2.QtGui import QIcon, QPixmap
from PySide2.QtWidgets import QStyle


def get_app_icon():
    app_icon = QIcon()
    for size in [16, 32, 64, 128, 256]:
        app_icon.addPixmap(QPixmap(":/icons/app/icon-ate-%s.png" % str(size)))
    return app_icon


def get_icon(name: str):
    _icon = QIcon()
    _icon.addPixmap(QPixmap(":/icons/fatcow/16x16/%s.png" % name))
    _icon.addPixmap(QPixmap(":/icons/fatcow/32x32/%s.png" % name))
    return _icon  # built at runtime

def setupActionsIcons(mw: 'MainWindow'):  # just adds icons to actions
    mw.actionNew.setIcon(get_icon("new"))
    mw.actionOpen.setIcon(get_icon("open"))
    mw.actionExample_Recent.setIcon(get_icon("document_recent"))
    mw.actionSave.setIcon(get_icon("save"))
    mw.actionSave_As.setIcon(get_icon("file_save_as"))
    mw.actionChange_Font.setIcon(get_icon("characters"))
    mw.menuChange_Language.setIcon(get_icon("change_language"))
    mw.actionEnglish.setIcon(get_icon("flag_usa"))
    mw.actionAbout.setIcon(get_icon("info"))
    mw.actionAbout_Qt.setIcon(mw.style().standardIcon(QStyle.SP_TitleBarMenuButton))
    mw.actionContribute.setIcon(get_icon("wishlist_add"))
    mw.actionView_GitHub_page.setIcon(get_icon("gh"))
    mw.actionExit.setIcon(get_icon("exit"))
    mw.actionExport.setIcon(get_icon("generic_export"))

