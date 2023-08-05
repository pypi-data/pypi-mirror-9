# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
# after http://docs.enthought.com/mayavi/mayavi/building_applications.html
import wx

from traits.api import HasTraits, Range, Instance, on_trait_change
from traitsui.api import View, Item, HGroup
from tvtk.pyface.scene_editor import SceneEditor
from mayavi.tools.mlab_scene_model import MlabSceneModel
from mayavi.core.ui.mayavi_scene import MayaviScene


class Visualization(HasTraits):
    scene = Instance(MlabSceneModel, ())

    def __init__(self):
        HasTraits.__init__(self)
        # self.plot = self.scene.mlab.plot3d(x, y, z, t, colormap='Spectral')

    # the layout of the dialog created
    view = View(Item('scene', editor=SceneEditor(scene_class=MayaviScene),
                     # height=250, width=300,
                     show_label=False))


class MayaviFrame(wx.Frame):
    def __init__(self, parent=None, id=wx.ID_ANY):
        wx.Frame.__init__(self, parent, id, 'Mayavi in Wx')
        self.visualization = Visualization()
        self.control = self.visualization.edit_traits(parent=self,
                                kind='subpanel').control
        self.Show()
