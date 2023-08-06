""" Defines a VerticalNotebook class for displaying a series of pages
    organized vertically, as opposed to horizontally like a standard notebook.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from pyface.qt import QtCore, QtGui

from pyface.widget import Widget
from pyface.tasks.dock_pane import DockPane

from traits.api \
    import HasTraits, HasPrivateTraits, Instance, List, Str, Bool, Property, \
           Event, Any, on_trait_change, cached_property

from traitsui.api import UI

from traitsui.editor \
    import Editor

class VNotebookTraitsPage ( HasPrivateTraits ):
    """ 
    A class representing a vertical page within a notebook.
    
    This looks, unsurprisingly, very much like a TraitsDockPane
    """

    #-- Public Traits ----------------------------------------------------------

    # The name of the page (displayed on its 'tab') [Set by client]:
    name = Str

    # The Traits UI associated with this page [Set by client]:
    ui = Instance(UI)

    # Optional client data associated with the page [Set/Get by client]:
    data = Any

    # The HasTraits object whose traits we're viewing
    model = Instance(HasTraits)

    # The name of the object trait that signals a page name change [Set by
    # client]:
    trait_name = Str

    # The parent window for the client page [Get by client]:
    parent = Property

    #-- Traits for use by the Notebook/Sizer -----------------------------------

    # The current open status of the notebook page:
    is_open = Bool( False )

    # The minimum size for the page:
    min_size = Property

    # The open size property for the page:
    open_size = Property

    # The closed size property for the page:
    closed_size = Property

    #-- Private Traits ---------------------------------------------------------

    # The notebook this page is associated with:
    notebook = Instance( 'VerticalNotebook' )

    # The control representing the closed page:
    # closed_control = Instance(QtGui.QPushButton)

    # The control representing the open page:
    # open_page = Property( depends_on = 'open_theme' )

    #-- Public Methods ---------------------------------------------------------

    def close ( self ):
        """ Closes the notebook page.
        """

        if self.ui is not None:
            self.ui.dispose()
            self.ui = None
        
        '''
        if self.closed_page is not None:
            self.closed_page.control.Destroy()
            self.open_page.control.Destroy()
            self.control = None
        '''

    '''
    def set_size ( self, x, y, dx, dy ):
        """ Sets the size of the current active page.
        """
        if self.is_open:
            self.open_page.control.SetDimensions( x, y, dx, dy )
        else:
            self.closed_page.control.SetDimensions( x, y, dx, dy )
    '''
            
    def register_name_listener ( self, object, trait_name ):
        """ Registers a listener on the specified object trait for a page name
            change.
        """
        # Save the information, so we can unregister it later:
        self.object, self.trait_name = object, trait_name

        # Register the listener:
        object.on_trait_change( self._name_updated, trait_name )

        # Make sure the name gets initialized:
        self._name_updated()

    #-- Property Implementations -----------------------------------------------

    def _get_min_size ( self ):
        """ Returns the minimum size for the page.
        """
        dxo, dyo = self.open_page.best_size
        dxc, dyc = self.closed_page.best_size
        if self.is_open:
            return wx.Size( max( dxo, dxc ), dyo )

        return wx.Size( max( dxo, dxc ), dyc )

    def _get_open_size ( self ):
        """ Returns the open size for the page.
        """
        return self.open_page.best_size

    def _get_closed_size ( self ):
        """ Returns the closed size for the page.
        """
        return self.closed_page.best_size

    @cached_property
    def _get_closed_page ( self ):
        """ Returns the 'closed' form of the notebook page.
        """
        return QtGui.QPushButton(self.notebook.widget.control)

    @cached_property
    def _get_open_page ( self ):
        """ Returns the 'open' form of the notebook page.
        """
        self.ui = self.edit_traits(kind='subpanel', parent=self.notebook.widget.control)
        return self.ui.control
        result = ImagePanel( theme             = self.open_theme,
                             text              = self.name,
                             controller        = self,
                             default_alignment = 'center',
                             state             = 'open' )
        result.create_control( self.notebook.widget.control )

        return result

    def _get_parent ( self ):
        """ Returns the parent window for the client's window.
        """
        return self.open_page.control

    #-- Trait Event Handlers ---------------------------------------------------

    def _ui_changed ( self, ui ):
        """ Handles the ui trait being changed.
        """
        if ui is not None:
            self.control = ui.control

    def _control_changed ( self, control ):
        """ Handles the control for the page being changed.
        """
        if control is not None:
            self.open_page.control.GetSizer().Add( control, 1, wx.EXPAND )
            self._is_open_changed( self.is_open )

    def _is_open_changed ( self, is_open ):
        """ Handles the 'is_open' state of the page being changed.
        """
        self.closed_page.control.Show( not is_open )
        self.open_page.control.Show( is_open )

        if is_open:
            self.closed_page.control.SetSize( wx.Size( 0, 0 ) )
        else:
            self.open_page.control.SetSize( wx.Size( 0, 0 ) )

    def _name_changed ( self, name ):
        """ Handles the name trait being changed.
        """
        self.closed_page.text = self.open_page.text = name

    def _name_updated ( self ):
        """ Handles a signal that the associated object's page name has changed.
        """
        nb           = self.notebook
        handler_name = None

        method = None
        editor = nb.editor
        if editor is not None:
            method = getattr( editor.ui.handler,
                 '%s_%s_page_name' % ( editor.object_name, editor.name ), None )
        if method is not None:
            handler_name = method( editor.ui.info, self.object )

        if handler_name is not None:
            self.name = handler_name
        else:
            self.name = getattr( self.object, self.trait_name ) or '???'

    #-- ThemedControl Mouse Event Handlers -------------------------------------

    def open_left_down ( self, x, y, event ):
        """ Handles the user clicking on an open notebook page to close it.
        """
        if not self.notebook.double_click:
            self.notebook.close( self )

    def open_left_dclick ( self, x, y, event ):
        """ Handles the user double clicking on an open notebook page to close
            it.
        """
        if self.notebook.double_click:
            self.notebook.close( self )

    def closed_left_down ( self, x, y, event ):
        """ Handles the user clicking on a closed notebook page to open it.
        """
        if not self.notebook.double_click:
            self.notebook.open( self )

    def closed_left_dclick ( self, x, y, event ):
        """ Handles the user double clicking on a closed notebook page to open
            it.
        """
        if self.notebook.double_click:
            self.notebook.open( self )

#-------------------------------------------------------------------------------
#  'ThemedVerticalNotebook' class:
#-------------------------------------------------------------------------------

class VerticalNotebook(DockPane):
    """ Defines a VerticalNotebook class for displaying a series of pages
        organized vertically, as opposed to horizontally like a standard
        notebook.
        
        we'll make this a tasks DockPane instead of the usual widget.
    """

    #-- Public Traits ----------------------------------------------------------

    # Allow multiple open pages at once?
    multiple_open = Bool( False )

    # Should the notebook be scrollable?
    scrollable = Bool( False )

    # Use double clicks (True) or single clicks (False) to open/close pages:
    # double_click = Bool( False )

    # The pages contained in the notebook:
    pages = List( VNotebookPage )

    # The traits UI editor this notebook is associated with (if any):
    editor = Instance( Editor )

    #-- Private Traits ---------------------------------------------------------

    # The Qt control used to represent the notebook:
    widget = Instance(Widget)

    ###########################################################################
    # 'ITaskPane' interface.
    ###########################################################################

    def destroy(self):
        """ Destroy the toolkit-specific control that represents the pane.
        """
        # TODO - iterate through self.pages and destroy the notebook pages

        # Destroy the dock control.
        super(DockPane, self).destroy()

    ###########################################################################
    # 'IDockPane' interface.
    ###########################################################################

    def create_contents(self, parent):
        """ Create and return the toolkit-specific contents of the dock pane.
        """
        
        # TODO - init here (any required?)

        return self.widget.control

    # VerticalNotebook interface

    def create_page ( self ):
        """ Creates a new **VNotebookPage** object representing a notebook page and
            returns it as the result.
        """
        return VNotebookPage(notebook = self)
    
    def open ( self, page ):
        """ Handles opening a specified **VNotebookPage** notebook page.
        """
        if (page is not None) and (not page.is_open):
            if not self.multiple_open:
                for a_page in self.pages:
                    a_page.is_open = False

            page.is_open = True

            self._refresh()

    def close ( self, page ):
        """ Handles closing a specified **VNotebookPage** notebook page.
        """
        if (page is not None) and page.is_open:
            page.is_open = False
            self._refresh()

    #-- Trait Event Handlers ---------------------------------------------------

    def _pages_changed ( self, old, new ):
        """ Handles the notebook's pages being changed.
        """
        for page in old:
            page.close()

        self._refresh()

    def _pages_items_changed ( self, event ):
        """ Handles some of the notebook's pages being changed.
        """
        for page in event.removed:
            page.close()

        self._refresh()

    def _multiple_open_changed ( self, multiple_open ):
        """ Handles the 'multiple_open' flag being changed.
        """
        if not multiple_open:
            first = True
            for page in self.pages:
                if first and page.is_open:
                    first = False
                else:
                    page.is_open = False

        self._refresh()

    #-- wx.Python Event Handlers -----------------------------------------------
    '''
    def _erase_background ( self, event ):
        """ Do not erase the background here (do it in the 'on_paint' handler).
        """
        pass

    def _paint ( self, event ):
        """ Paint the background using the associated ImageSlice object.
        """
        paint_parent( wx.PaintDC( self.control ), self.control )
    '''

    #-- Private Methods --------------------------------------------------------

    def _refresh ( self ):
        """ Refresh the layout and contents of the notebook.
        """
        control = self.widget.control
        if control is not None:
            # Set the virtual size of the canvas (so scroll bars work right):
            sizer = control.GetSizer()
            if control.GetSize()[0] == 0:
                control.SetSize( sizer.CalcInit() )
            control.SetVirtualSize( sizer.CalcMin() )
            control.Layout()
            control.Refresh()

'''
#-------------------------------------------------------------------------------
#  'ThemedVerticalNotebookSizer' class:
#-------------------------------------------------------------------------------

class ThemedVerticalNotebookSizer ( wx.PySizer ):
    """ Defines a sizer that correctly sizes a themed vertical notebook's
        children to implement the vertical notebook UI model.
    """

    def __init__ ( self, notebook ):
        """ Initializes the object.
        """
        super( ThemedVerticalNotebookSizer, self ).__init__()

        # Save the notebook reference:
        self._notebook = notebook

    def CalcMin ( self ):
        """ Calculates the minimum size of the control by aggregating the
            sizes of the open and closed pages.
        """
        tdx, tdy = 0, 0
        for page in self._notebook.pages:
            dx, dy = page.min_size
            tdx    = max( tdx, dx )
            tdy   += dy

        return wx.Size( tdx, tdy )

    def CalcInit ( self ):
        """ Calculates a reasonable initial size of the control by aggregating
            the sizes of the open and closed pages.
        """
        tdx, tdy = 0, 0
        open_dy  = closed_dy = 0
        for page in self._notebook.pages:
            dxo, dyo = page.open_size
            dxc, dyc = page.closed_size
            tdx      = max( tdx, dxo, dxc )
            if dyo > open_dy:
                tdy += (dyo - open_dy + closed_dy)
                open_dy, closed_dy = dyo, dyc
            else:
                tdy += dyc

        return wx.Size( tdx, min( tdy, screen_dy / 2 ) )

    def RecalcSizes ( self ):
        """ Layout the contents of the sizer based on the sizer's current size
            and position.
        """
        x, y     = self.GetPositionTuple()
        tdx, tdy = self.GetSizeTuple()
        cdy      = ody = 0
        for page in self._notebook.pages:
            dx, dy = page.min_size
            if page.is_open:
                ody += dy
            else:
                cdy += dy

        ady = max( 0, tdy - cdy )

        for page in self._notebook.pages:
            dx, dy = page.min_size
            if page.is_open:
                ndy  = (ady * dy) / ody
                ady -= ndy
                ody -= dy
                dy   = ndy
            page.set_size( x, y, tdx, dy )
            y += dy
'''