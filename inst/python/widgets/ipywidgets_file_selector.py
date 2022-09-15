from ipywidgets import DOMWidget
from traitlets import Unicode, List, Dict, observe
import os

class IPFileSelector(DOMWidget):
    _view_module = Unicode('nbextensions/ipywidgets_file_selector/ipywidgets_file_selector', sync=True)
    _view_name = Unicode('IPFileSelector', sync=True)
    home_path = Unicode().tag(sync=True)
    current_path = Unicode().tag(sync=True)
    subdirs = List().tag(sync=True)
    subfiles = List().tag(sync=True)
    selected = Dict().tag(sync=True)

    def __init__(self, *args, **kwargs):
        super(IPFileSelector, self).__init__(*args, **kwargs)
        self.selected = kwargs.get('selected', dict())
        self.home_path = kwargs.get('home', os.getcwd())
        self.on_msg(self._handleMsg)

    def __del__(self):
        self.close()

    def _handleMsg(self, widget, content, buffers=None):
        if (content['type'] == 'init'):
            self._current_path_changed(None)
        if (content['type'] == 'select'):
            self.selected = content['selected']

    @observe('current_path')
    def _current_path_changed(self, change):
        if change is not None:
            self.current_path = change['new']
        subdirs_temp = [ ]
        subfiles_temp = [ ]
        if (os.path.isdir(self.current_path)):
            for f in os.listdir(self.current_path):
                ff = self.current_path + "/" + f
                if os.path.isdir(ff):
                    subdirs_temp.append(ff)
                else:
                    subfiles_temp.append(ff)
        self.subdirs = subdirs_temp
        self.subfiles = subfiles_temp
        #msg = dict()
        #msg["type"] = "dir_update"
        #self.send(msg)

    @observe('selected')
    def _selected_changed(self, change):
        self.selected = change['new']
        pass

    @observe('subfile')
    def _subfiles_changed(self, change):
        self.subfiles = change['new']

    @observe('subdirs')
    def _subdirs_changed(self, change):
        self.subdirs = change['new']
