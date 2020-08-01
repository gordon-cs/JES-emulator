#!/usr/bin/env python3

"""
pictureTool.py - script program to implement the "explore" functionality
                 in JES for the JES4py package

Written: 2020-07-24 Gahngnin Kim <gahngnin.kim@gordon.edu>

The "explore()" function in JES will open a new window and display the image
imported from the given file path. The window provides an interactive picture
tool for the user. It allows users to zoom in and out of the image and pick
a pixel to examine its RGB values with the color preview. When a pixel is
selected from the image, a crosshair will appear in that selected position.
Unlike, "show()" function, it cannot be repainted with "repaint()" method.

The JES4py's implementation of "explore()" function provides a nearly identical
experience with an improvement compared to JES's. Display and image size
detection code is added to ensure that the window size doesn't go beyond the
display resolution even if the image is larger. The image panel will set
scrollbars when a high-resolution image is imported will set the scrollbar to
fit the image in the window. The program can also work standalone.

The crosshair feature is currently disabled due to incomplete implementation.
To continue the implementation, check the "s20-crosshair-scrolledpanel" branch.

This program was first developed during the Gordon College Computer Science
Summer 2020 Practicum as a part of the JES4py project, under the guidance of
Dr. Jonathan Senning.

Summer 2020 JES4py Team: Dr. Jonathan Senning
                         Nick Noormand
                         Gahngnin Kim

"""

import os
import sys
import wx
import wx.lib.scrolledpanel
# import wx.lib.inspection

class Cursor:
    width = 7
    height = 7
    centerX = 3
    centerY = 3
    prevX = 0
    prevY = 0

    def __init__(self, width=7, height=7):
        self.width = width
        self.height = height
        self.centerX = int((self.width - 1)/2)
        self.centerY = int((self.height - 1)/2)

        dc = wx.MemoryDC()

        # Draw the mask
        self.cursorMask = wx.Bitmap(self.width, self.height, depth=1)
        dc.SelectObject(self.cursorMask)
        dc.SetPen(wx.Pen(wx.Colour(255, 255, 255), width=3))
        dc.DrawLine(0, self.centerY, self.width-1, self.centerY)
        dc.DrawLine(self.centerX, 0, self.centerX, self.height-1)

        # Draw the cursor
        self.cursorBitmap = wx.Bitmap(self.width, self.height)
        dc.SelectObject(self.cursorBitmap)
        dc.SetPen(wx.Pen(wx.Colour(255, 255, 0)))
        dc.DrawLine(0, self.centerY, self.width-1, self.centerY)
        dc.DrawLine(self.centerX, 0, self.centerX, self.height-1)
        self.cursorBitmap.SetMask(wx.Mask(self.cursorMask))

        # done with dc
        del dc

    def getCursorBitmap(self):
        return self.cursorBitmap

    def getCursorWidth(self):
        return self.width

    def getCursorHeight(self):
        return self.height
    
    def getCursorSize(self):
        return (self.width, self.height)

    def setWindow(self, x0, y0, x1, y1):
        self.x0, self.y0 = x0, y0
        self.x1, self.y1 = x1, y1

    def draw(self, x, y):
        x0 = max(0, self.x0 + self.centerX - x)
        y0 = max(0, self.y0 + self.centerY - y)
        #WORKING HERE
        x1 = min(self.width - 1, self.width - 1 + x - (self.x1 - self.centerX))

class MainWindow(wx.Frame):

    MinWindowWidth = 350
    MinWindowHeight = 0
    ColorPanelHeight = 70
    PaintChipSize = 24
    zoomLevels = [25, 50, 75, 100, 150, 200, 500]
    zoomLevel = float(zoomLevels[3]) / 100.0
    cursorBitmap = None
    crosshair = None
    x = 0
    y = 0

    def __init__(self, filename, parent, title):
        # Load image and get image size
        self.image = wx.Image(filename, wx.BITMAP_TYPE_ANY)
        self.bmp = wx.Bitmap(self.image)

        super(MainWindow, self).__init__(parent=parent, title=title, style=wx.DEFAULT_FRAME_STYLE)

        #self.crosshair = Cursor(7, 7)
        self.InitUI()
        self.Center()
        self.clipOnBoundary()
        # wx.lib.inspection.InspectionTool().Show() # Inspection tool for debugging

    def InitUI(self):
        wScr, hScr = wx.DisplaySize()
        wView, hView = int(wScr * 0.95), int(hScr * 0.85)
        w, h = self.image.GetSize()

        # Debugging purpose (for the crosshair function)
        self.points = []
        self.savedBmpPos = None
        self.savedBmp = None

        # w = min(max(self.MinWindowWidth, w), wView)
        # h = min(max(self.MinWindowHeight, h + self.ColorPanelHeight), hView)
        w = min(max(self.MinWindowWidth, w), wView)
        h = min(max(self.MinWindowHeight, h + self.ColorPanelHeight), hView)

        # setup the zoom menu
        self.setupZoomMenu()

        # create main sizer
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)

        # setup the color information panel
        self.setupColorInfoDisplay()
        self.mainSizer.Add(self.colorInfoPanel, 0, wx.EXPAND|wx.ALL, 0)

        # set up the image display panel
        self.setupImageDisplay()
        self.mainSizer.Add(self.imagePanel, 0, wx.EXPAND|wx.ALL, 0)

        self.SetSizer(self.mainSizer)
        # self.SetSize((w, h))
        self.Fit()
        self.imagePanel.SetupScrolling(scrollToTop=True)

        # w, h = self.image.GetSize()
        # h = h + self.ColorPanelHeight
        self.SetSize((w, h))
        self.SetClientSize((w,h))

    def setupZoomMenu(self):
        # Set up zoom menu
        zoomMenu = wx.Menu()
        for z in self.zoomLevels:
            item = "{}%".format(z)
            helpString = "Zoom by {}%".format(z)
            zoomID = zoomMenu.Append(wx.ID_ANY, item, helpString)
            self.Bind(wx.EVT_MENU, self.onZoom, zoomID)

        # menuZoom25 = zoomMenu.Append(wx.ID_ANY, "25%","Zoom by 25%")
        # menuZoom50 = zoomMenu.Append(wx.ID_ANY, "50%","Zoom by 50%")
        # menuZoom75 = zoomMenu.Append(wx.ID_ANY, "75%","Zoom by 75%")
        # menuZoom100 = zoomMenu.Append(wx.ID_ANY, "100%","Zoom by 100%")
        # menuZoom150 = zoomMenu.Append(wx.ID_ANY, "150%","Zoom by 150%")
        # menuZoom200 = zoomMenu.Append(wx.ID_ANY, "200%","Zoom by 200%")
        # menuZoom500 = zoomMenu.Append(wx.ID_ANY, "500%","Zoom by 500%")

        # # Set menu events
        # self.Bind(wx.EVT_MENU, self.onZoom, menuZoom25)
        # self.Bind(wx.EVT_MENU, self.onZoom, menuZoom50)
        # self.Bind(wx.EVT_MENU, self.onZoom, menuZoom75)
        # self.Bind(wx.EVT_MENU, self.onZoom, menuZoom100)
        # self.Bind(wx.EVT_MENU, self.onZoom, menuZoom150)
        # self.Bind(wx.EVT_MENU, self.onZoom, menuZoom200)
        # self.Bind(wx.EVT_MENU, self.onZoom, menuZoom500)
        
        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(zoomMenu, "&Zoom") # Adds the "zoomMenu" to the MenuBar
        self.SetMenuBar(menuBar) # Adds the MenuBar to the Frame content.

    def setupColorInfoDisplay(self):
        self.colorInfoPanel = wx.Panel(parent=self, size=(-1, self.ColorPanelHeight))

        # Create main sizer for this color info panel
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        # ---- First row ----

        # Create sizer to hold components
        sizer1 = wx.BoxSizer(wx.HORIZONTAL)

        # X and Y labels
        lblX = wx.StaticText(self.colorInfoPanel, 0, style=wx.ALIGN_CENTER)
        lblY = wx.StaticText(self.colorInfoPanel, 0, style=wx.ALIGN_CENTER)
        lblX.SetLabel("X: ")
        lblY.SetLabel("Y: ")
    
        # Navigation buttons (Enable after getting the colorpicker/eyedropper functional)
        # Icons made by Freepik from www.flaticon.com; Modified by Gahngnin Kim
        img_R = os.path.join(sys.path[0], 'images', 'Right.png')
        img_L = os.path.join(sys.path[0], 'images', 'Left.png')
        bmp_R = wx.Bitmap(img_R, wx.BITMAP_TYPE_ANY)
        bmp_L = wx.Bitmap(img_L, wx.BITMAP_TYPE_ANY)
        bmp_size = (bmp_L.GetWidth()+5,bmp_L.GetHeight()+5)
        buttonX_L = wx.BitmapButton(self.colorInfoPanel, wx.ID_ANY, bitmap=bmp_L, size=bmp_size)
        buttonX_L.myname = "XL"
        buttonX_R = wx.BitmapButton(self.colorInfoPanel, wx.ID_ANY, bitmap=bmp_R, size=bmp_size)
        buttonX_R.myname = "XR"
        buttonY_L = wx.BitmapButton(self.colorInfoPanel, wx.ID_ANY, bitmap=bmp_L, size=bmp_size)
        buttonY_L.myname = "YL"
        buttonY_R = wx.BitmapButton(self.colorInfoPanel, wx.ID_ANY, bitmap=bmp_R, size=bmp_size)
        buttonY_R.myname = "YR"
        buttonX_L.Bind(wx.EVT_BUTTON, self.ImageCtrl_OnNavBtn)
        buttonX_R.Bind(wx.EVT_BUTTON, self.ImageCtrl_OnNavBtn)
        buttonY_L.Bind(wx.EVT_BUTTON, self.ImageCtrl_OnNavBtn)
        buttonY_R.Bind(wx.EVT_BUTTON, self.ImageCtrl_OnNavBtn)

        # Textboxes to display X and Y coordinates on click
        self.pixelTxtX = wx.TextCtrl(self.colorInfoPanel, wx.ALIGN_CENTER, \
            style=wx.TE_PROCESS_ENTER, size=(50, -1))
        self.pixelTxtY = wx.TextCtrl(self.colorInfoPanel, wx.ALIGN_CENTER, \
            style=wx.TE_PROCESS_ENTER, size=(50, -1))
        self.pixelTxtX.Bind(wx.EVT_TEXT_ENTER, self.ImageCtrl_OnEnter)
        self.pixelTxtY.Bind(wx.EVT_TEXT_ENTER, self.ImageCtrl_OnEnter)

        # Add first row components to sizer
        # X coordinate display
        sizer1.Add(lblX, 0, flag=wx.CENTER, border=0)
        sizer1.Add(buttonX_L, 0, border=0)
        sizer1.Add(self.pixelTxtX, 0, flag=wx.CENTER, border=5) # Text Control Box
        sizer1.Add(buttonX_R, 0, border=0)

        # Horizonal spacer
        sizer1.Add((5, -1))

        # Y coordinate display
        sizer1.Add(lblY, 0, flag=wx.CENTER, border=0)
        sizer1.Add(buttonY_L, 0, border=0)
        sizer1.Add(self.pixelTxtY, 0, flag=wx.CENTER, border=5) # Text Control Box
        sizer1.Add(buttonY_R, 0, border=0)
        
        # Add first row sizer to the main sizer
        mainSizer.Add(sizer1, 0, flag=wx.LEFT|wx.RIGHT|
                    wx.TOP|wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, border=1)

        # Vertical spacer
        mainSizer.Add((-1, 5))

        # ---- Second row ----

        # Create sizer to hold components
        sizer2 = wx.BoxSizer(wx.HORIZONTAL)

        # Static text displays RGB values of the given coordinates
        # Initialized with dummie values
        self.rgbValue = wx.StaticText(self.colorInfoPanel, label=u'')#, style=wx.ALIGN_CENTER)
        font = self.rgbValue.GetFont()
        font.PointSize += 2
        self.rgbValue.Font = font

        # initialize an empty bitmap
        bmp = wx.Bitmap(self.PaintChipSize, self.PaintChipSize)
        self.colorPreview = wx.StaticBitmap(parent=self.colorInfoPanel, bitmap=bmp)

        # Add items to the second sizer (sizer2)
        sizer2.Add(self.rgbValue, 0, flag=wx.ALIGN_CENTER, border=5)

        # Horizontal spacer
        sizer2.Add((10, -1), 0)

        # Small image that shows the color at the selected pixel
        sizer2.Add(self.colorPreview, 0, flag=wx.ALIGN_CENTER, border=5) 

        # Add sizer2 to the main sizer
        mainSizer.Add(sizer2, 0, flag=wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, border=1)

        # Vertical spacer
        mainSizer.Add((-1, 5))

        self.colorInfoPanel.SetSizer(mainSizer)
        #mainSizer.Fit(panel)
        #panel.Layout()
        #self.Show()

    def setupImageDisplay(self):
        """Set up image display panel
        """
        # Get image size and make scrolled panel large enough to hold image
        # even with maximum zoom
        w, h = self.image.GetSize()
        maxZoomLevel = int(int(self.zoomLevels[-1]) / 100)
        maxSize = (maxZoomLevel * w, maxZoomLevel * h)
    
        # Create a scrolled panel to hold the image
        self.imagePanel = wx.lib.scrolledpanel.ScrolledPanel(parent=self, size=maxSize, style=wx.NO_BORDER)

        # Store the image and setup even handlers for mouse clicks and motion
        self.imageCtrl = wx.StaticBitmap(parent=self.imagePanel, bitmap=self.bmp)
        if wx.Platform == "__WXMSW__" or wx.Platform == "__WXGTK__":
            self.imageCtrl.Bind(wx.EVT_LEFT_DOWN, self.ImageCtrl_OnMouseClick)
            self.imageCtrl.Bind(wx.EVT_MOTION, self.ImageCtrl_OnMouseClick)
            #self.imageCtrl.Bind(wx.EVT_LEFT_UP, self.OnPaint)
        elif wx.Platform == "__WXMAC__":
            self.imagePanel.Bind(wx.EVT_LEFT_DOWN, self.ImageCtrl_OnMouseClick)
            self.imagePanel.Bind(wx.EVT_MOTION, self.ImageCtrl_OnMouseClick) 
            #self.imagePanel.Bind(wx.EVT_LEFT_UP, self.OnPaint)
        #panel.SetFocus()
        #panel.Bind(wx.EVT_LEFT_DOWN, self.onFocus)

        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(self.imageCtrl, 0, wx.ALIGN_LEFT|wx.ALIGN_TOP|wx.ALL, 0)
        self.imagePanel.SetSizer(mainSizer)
        self.mainSizer.Fit(self.imagePanel)
        self.imagePanel.SetupScrolling(scrollToTop=True)
        #return panel

    def clipOnBoundary(self):
        """Clips x and y to be valid pixel coordinates

        Ensures that the current values of x and y are valid pixel
        coordinates for the image

        Modifies
        --------
        self.x, self.y : int
            the pixel coordinates
        self.pixelTxtX, self.pixelTxtY : wx.TextCtrl
            the textboxes displaying the pixel coordinates
        """
        width, height = self.image.GetSize()
        if self.x < 0:
            self.x = 0
        elif self.x >= width:
            self.x = width - 1
        if self.y < 0:
            self.y = 0
        elif self.y >= height:
            self.y = height - 1
        self.pixelTxtX.SetValue(str(self.x))
        self.pixelTxtY.SetValue(str(self.y))
        self.updateColorInfo()

    def updateColorInfo(self):
        """Updates the color patch in the color information display

        The color patch is a small square image with a black outline and
        interior color matching that corresponding to the most-recently
        selected pixel in the image.
        """
        r = self.image.GetRed(self.x, self.y)
        g = self.image.GetGreen(self.x, self.y)
        b = self.image.GetBlue(self.x, self.y)
        self.rgbValue.SetLabel(label=u'R: {} G: {} B: {}  Color at location:'.format(r, g, b))

        # Sets the color of the square image on mouse click
        bmp = wx.Bitmap(self.PaintChipSize, self.PaintChipSize)
        dc = wx.MemoryDC()
        dc.SelectObject(bmp)
        pen = wx.Pen(wx.Colour(0,0,0)) # black for outline
        dc.SetPen(pen)
        brush = wx.Brush(wx.Colour(r,g,b)) # current image pixel color
        dc.SetBrush(brush)
        dc.DrawRectangle(0, 0, self.PaintChipSize, self.PaintChipSize)
        del dc
        self.colorPreview.SetBitmap(bmp) # Replace the bitmap with the new one
        self.colorInfoPanel.Layout()

    def updateView(self):
        """Scale image according to the zoom factor and (re)display it
        """
        width, height = self.image.GetSize()
        w = int(width * self.zoomLevel)
        h = int(height * self.zoomLevel)
        image = self.image.Scale(w, h)
        self.bmp = wx.Bitmap(image, wx.BITMAP_TYPE_ANY)
        self.imageCtrl.SetBitmap(self.bmp)

        # Redraw crosshair cursor (if any)
        if self.savedBmp is not None:
            self.savedBmp = None
            self.computeCursorPosition()

        #self.drawBitmap()

    # def makeCursor(self):
    #     """Create the bitmap (w/mask) for the crosshair cursor
    #     """
    #     dc = wx.MemoryDC()

    #     # Draw the mask
    #     self.cursorMask = wx.Bitmap(7, 7, depth=1)
    #     dc.SelectObject(self.cursorMask, )
    #     dc.SetPen(wx.Pen(wx.Colour(255, 255, 255), width=3))
    #     dc.DrawLine(0, 3, 6, 3)
    #     dc.DrawLine(3, 0, 3, 6)

    #     # Draw the cursor
    #     self.cursorBitmap = wx.Bitmap(7, 7)
    #     dc.SelectObject(self.cursorBitmap)
    #     dc.SetPen(wx.Pen(wx.Colour(255, 255, 0)))
    #     dc.DrawLine(0, 3, 6, 3)
    #     dc.DrawLine(3, 0, 3, 6)
    #     self.cursorBitmap.SetMask(wx.Mask(self.cursorMask))

    #     # done with dc
    #     del dc

    def computeCursorPosition(self):
        # Get cursor coordinates
        dc = wx.ClientDC(self.imageCtrl)
        self.imagePanel.DoPrepareDC(dc)
        sx, sy = dc.GetDeviceOrigin()
        sx = int(sx / self.zoomLevel)
        sy = int(sy / self.zoomLevel)
        #origin = dc.GetDeviceOrigin()
        #sx, sy = self.imagePanel.CalcUnscrolledPosition(origin)
        #sx, sy = self.imagePanel.CalcScrolledPosition(origin)
        x = int(self.x * self.zoomLevel) + sx
        y = int(self.y * self.zoomLevel) + sy
        self.cursorPos = x, y
        self.cursorPos2 = x - sx, y - sy
        del dc
        print(f"({self.x},{self.y}); ({x},{y}); ({sx},{sy})")

    def undrawCursor(self):
        """Restore bitmap (if any) saved previous cursor event
        """
        if self.savedBmp is not None:
            dc = wx.ClientDC(self.imageCtrl)
            dc.DrawBitmap(self.savedBmp, self.savedBmpPos, False)
            del dc
            
    def drawCursor(self):
        # cw, ch = self.cursorBitmap.GetSize()
        # bx0 = x - int((cursorSize[0]-1)/2)
        # by0 = y - int((cursorSize[1]-1)/2)
        # bx1 = x + int((cursorSize[0]-1)/2)
        # by1 = y + int((cursorSize[1]-1)/2)
        # if bx0 < 0:
        #     bx0 = 0
        # if by0 < 0:
        #     by0 = 0
        # if bx1 > self.

        x, y = self.cursorPos
        x2, y2 = self.cursorPos2

        dc = wx.ClientDC(self.imageCtrl)

        # Save bitmap from new cursor location
        cursorSize = self.cursorBitmap.GetSize()
        print(f"Cursor size: {cursorSize}")
        self.savedBmpPos = x-int((cursorSize[0]-1)/2), y-int((cursorSize[1]-1)/2)
        self.savedBmpPos2 = x2-int((cursorSize[0]-1)/2), y2-int((cursorSize[1]-1)/2)
        cursorRect = wx.Rect(self.savedBmpPos2, cursorSize)
        print(f"Cursor Rect: {cursorRect}")
        self.savedBmp = self.bmp.GetSubBitmap(cursorRect)

        # Draw the cursor bitmap
        dc.DrawBitmap(self.cursorBitmap, self.savedBmpPos, True)
        del dc

    def drawCrosshairs(self):
        """This feature works fine with Linux but not with Windows
        """
        # pass
        # """Draw image with crosshairs to indicate selected position
        # """
        if self.crosshair is None:
            self.crosshair = Cursor()
        self.cursorBitmap = self.crosshair.getCursorBitmap()

        # Restore bitmap (if any) saved previous cursor event
        self.undrawCursor()

        # Get cursor coordinates
        self.computeCursorPosition()

        # draw the cursor bitmap
        self.drawCursor()

# ===========================================================================
# Event handlers
# ===========================================================================

    def onFocus(self, event):
        self.imagePanel.SetFocus()

    def onZoom(self, event):
        """Sets desired zoom level and updates image display

        (Zoom event handler)
        """
        id_selected = event.GetId() # Gets the event id of the selected menu item
        obj = event.GetEventObject() # Gets the event object
        menuItem = obj.GetLabelText(id_selected) # Gets the label text of the menu item
        self.zoomLevel = float(menuItem.replace('%','')) / 100.0
        #self.x = self.y = 0
        self.imagePanel.Scroll(self.x, self.y) # "non-scrolled" position
        self.PostSizeEvent()
        self.clipOnBoundary()
        self.updateView()

    def ImageCtrl_OnNavBtn(self, event):
        """Increment or decrement x or y pixel coordinate
        """
        selectedBtn = event.GetEventObject().myname
        if selectedBtn == "XL":
            self.x = int(self.pixelTxtX.GetValue()) - 1
        elif selectedBtn == "XR":
            self.x = int(self.pixelTxtX.GetValue()) + 1
        elif selectedBtn == "YL":
            self.y = int(self.pixelTxtY.GetValue()) - 1
        elif selectedBtn == "YR":
            self.y = int(self.pixelTxtY.GetValue()) + 1
        self.clipOnBoundary()
        self.drawCrosshairs()

    def ImageCtrl_OnEnter(self, event):
        """Adjusts x and y pixel values to match displayed values
        """
        self.x = int(self.pixelTxtX.GetValue())
        self.y = int(self.pixelTxtY.GetValue())
        self.clipOnBoundary()
        self.drawCrosshairs()

    def ImageCtrl_OnMouseClick(self, event):
        """Update x and y pixel coordinates from pointer location
        """
        if event.LeftIsDown():
            event.Skip()
            dc = wx.ClientDC(self)
            self.imagePanel.DoPrepareDC(dc)
            if wx.Platform == "__WXMSW__":
                dc_pos = event.GetPosition()
            elif wx.Platform == "__WXGTK__" or wx.Platform == "__WXMAC__":
                dc_pos = event.GetLogicalPosition(dc)
            #self.coordinates = dc_pos
            del dc
            self.x = int(dc_pos.x / self.zoomLevel)
            self.y = int(dc_pos.y / self.zoomLevel)
            #===================================
            # Debugging - trying to store the selected position
            crosshair_pos = self.x, self.y
            self.points.append(crosshair_pos)
            #===================================
            self.clipOnBoundary()
            self.drawCrosshairs()

# ===========================================================================
# Main program
# ===========================================================================

def main(argv):

    usage = "usage: {} file [title]".format(argv[0])
    # Get image file name and optional image title from command line
    if len(argv) == 2:
        filename = title = argv[1]
    elif len(argv) == 3:
        filename = argv[1]
        title = argv[2]
    else:
        print(usage)
        exit(1)

    if not os.path.isfile(filename):
        print("{} does not exist or is not a file".format(filename))
        print(usage)
        exit(1)

    app = wx.App(False)
    frame = MainWindow(filename=filename, parent=None, title=title)
    frame.Show()
    app.MainLoop()

if __name__ == '__main__':
    main(sys.argv)
