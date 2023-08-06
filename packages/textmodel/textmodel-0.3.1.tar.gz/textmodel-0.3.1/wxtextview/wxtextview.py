# -*- coding: latin-1 -*-


import wx
import cPickle

import layout
from textmodel import TextModel
from textmodel.texeltree import defaultstyle
from .textview import TextView
from .wxdevice import WxDevice
from .updater import Updater
from math import ceil

defaultstyle.update(dict(underline=False, facename='', weight='normal'))


# XXX should this be integrated in device?
class DCStyler:
    last_style = None
    def __init__(self, dc):
        self.dc = dc
        
    def set_style(self, style):
        if style is self.last_style:
            return
        self.last_style = style
        weight = {
            'bold' : wx.FONTWEIGHT_BOLD,
            'normal' : wx.FONTWEIGHT_NORMAL
            }[style['weight']]
        font = wx.Font(style['fontsize'], 
                       wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, 
                       weight, 
                       style['underline'], style['facename'])
        self.dc.SetFont(font)            
        try: # Phoenix
            self.dc.SetTextBackground(wx.Colour(style['bgcolor']))
            self.dc.SetTextForeground(wx.Colour(style['textcolor']))
        except TypeError: # Classic
            self.dc.SetTextBackground(wx.NamedColour(style['bgcolor']))
            self.dc.SetTextForeground(wx.NamedColour(style['textcolor']))



class WXTextView(wx.ScrolledWindow, TextView):
    _scrollrate = 10, 10

    def __init__(self, parent, id=-1,  
                 pos=wx.DefaultPosition, size=wx.DefaultSize, style=0):
        wx.ScrolledWindow.__init__(self, parent, id,
                                   pos, size,
                                   style|wx.WANTS_CHARS)
        TextView.__init__(self)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda event: None)
        self.Bind(wx.EVT_CHAR, self.on_char)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_leftdown)
        self.Bind(wx.EVT_LEFT_UP, self.on_leftup)
        self.Bind(wx.EVT_LEFT_DCLICK, self.on_leftdclick)
        self.Bind(wx.EVT_MOTION, self.on_motion)
        self.Bind(wx.EVT_KILL_FOCUS, self.on_focus)
        self.Bind(wx.EVT_SET_FOCUS, self.on_focus)
        
        # key = keycode, control, alt
        self.actions = {
            (wx.WXK_ESCAPE, False, False) : 'dump_info', 
            (wx.WXK_RIGHT, True, False)  : 'move_word_end',
            (wx.WXK_RIGHT, False, False)  : 'move_right',
            (wx.WXK_LEFT, True, False)  : 'move_word_begin',
            (wx.WXK_LEFT, False, False)  : 'move_left',
            (wx.WXK_DOWN, True, False)  : 'move_paragraph_end',
            (wx.WXK_DOWN, False, False)  : 'move_down',
            (wx.WXK_UP, True, False)  : 'move_paragraph_begin',
            (wx.WXK_UP, False, False)  : 'move_up',
            (wx.WXK_HOME, False, False) : 'move_line_start',
            (wx.WXK_END, False, False) : 'move_line_end',   
            (wx.WXK_HOME, True, False) : 'move_document_start',
            (wx.WXK_END, True, False) : 'move_document_end',            
            (wx.WXK_PAGEDOWN, False, False): 'move_page_down',
            (wx.WXK_PAGEUP, False, False): 'move_page_up',
            (wx.WXK_PAGEUP, True, False) : 'move_document_start',
            (wx.WXK_PAGEDOWN, True, False) : 'move_document_end',            
            (wx.WXK_RETURN, False, False): 'insert_newline',
            (wx.WXK_BACK, False, False): 'backspace',
            (wx.WXK_DELETE, False, False): 'delete',
            (3, True, False) : 'copy',
            (22, True, False) : 'paste',
            (24, True, False) : 'cut',
            (26, True, False) : 'undo',
            (18, True, False) : 'redo',  
            (127, True, False) : 'del_word_left',   
            (1, True, False) : 'select_all',
            }
        
    def create_updater(self):
        return Updater(
            self.model, 
            device=WxDevice(), 
            maxw=self._maxw)

    def refresh(self):
        self.Refresh()

    def on_focus(self, event):
        # focus changed
        self.Refresh()

    def on_char(self, event):
        keycode = event.GetKeyCode()
        ctrl = event.ControlDown()
        shift = event.ShiftDown()
        alt = event.AltDown()        
        char = event.GetUnicodeKey()
        action = self.actions.get((keycode, ctrl, alt))
        if action is None:
            action = unichr(keycode)
        self.handle_action(action, shift)
        
    def copy(self):
        if not self.has_selection():
            return        
        s1, s2 = self.get_selected()[0] # XXX Assuming just one region
        part = self.model[s1:s2]
        text = part.get_text()
        plain = wx.TextDataObject()
        plain.SetText(text)
        pickled = wx.CustomDataObject("pytextmodel")
        pickled.SetData(cPickle.dumps(part))
        data = wx.DataObjectComposite()
        data.Add(plain)
        data.Add(pickled)
        wx.TheClipboard.Open()
        wx.TheClipboard.SetData(data)
        wx.TheClipboard.Close()

    def paste(self):
        if self.has_selection():
            for s1, s2 in self.get_selected():
                self.model.remove(s1, s2)
                self.index = s1
        if wx.TheClipboard.IsOpened():  # may crash, otherwise
            return
        pickled = wx.CustomDataObject("pytextmodel")
        plain = wx.TextDataObject()
        textmodel = None
        wx.TheClipboard.Open()
        if wx.TheClipboard.GetData(pickled):            
            textmodel = cPickle.loads(pickled.GetData())

        elif wx.TheClipboard.GetData(plain):
            textmodel = self._TextModel(plain.GetText())

        wx.TheClipboard.Close()
        if textmodel is not None:
            self.insert(self.index, textmodel)

    def cut(self):
        if self.has_selection():
            self.copy()
            for s1, s2 in self.get_selected():
                self.remove(s1, s2)
         
    def on_paint(self, event):
        self._update_scroll()
        self.keep_cursor_on_screen()

        pdc = wx.PaintDC(self)
        pdc.SetAxisOrientation(True, False)
        if self.updater.get_device().buffering:
            dc = wx.BufferedDC(pdc)
            if not dc.IsOk():
                return
        else:
            dc = pdc
        dc.SetBackgroundMode(wx.SOLID)
        dc.SetBackground(wx.WHITE_BRUSH)
        dc.Clear()
        styler = DCStyler(dc)
        
        region = self.GetUpdateRegion()
        x, y, w, h = region.Box
        dc.SetClippingRegion(x-1, y-1, w+2, h+2)

        x, y = self.CalcScrolledPosition((0,0)) 
        layout = self.layout
        layout.draw(x, y, dc, styler)
        if wx.Window.FindFocus() is self: 
            layout.draw_cursor(self.index, x, y, dc, defaultstyle)
        for j1, j2 in self.get_selected():
            layout.draw_selection(j1, j2, x, y, dc)
        styler = None
        dc = None

    def on_size(self, event):
        self.keep_cursor_on_screen()

    def on_motion(self, event):
        if not event.LeftIsDown():
            return event.Skip()
        x, y = self.CalcUnscrolledPosition(event.Position) 
        i = self.layout.get_index(x, y)
        if i is not None:
            self.set_index(i, extend=True)

    def on_leftdown(self, event):
        x, y = self.CalcUnscrolledPosition(event.Position) 
        i = self.compute_index(x, y)
        if i is not None:
            self.set_index(i, extend=event.ShiftDown())
        self.SetFocus()
        self.CaptureMouse()

    def on_leftup(self, event):
        if self.HasCapture():
            self.ReleaseMouse()

    def on_leftdclick(self, event):
        # Mark word
        x, y = self.CalcUnscrolledPosition(event.Position) 
        self.select_word(x, y)
        self.SetFocus()

    ### Scroll
    def _update_scroll(self):
        layout = self.layout
        self.SetVirtualSize((layout.width, layout.height))
        self._scrollrate = 10, 10
        self.SetScrollRate(*self._scrollrate)
        
    def adjust_viewport(self):
        # Adjust view so that the cursor is visible
        layout = self.layout
        r = layout.get_rect(self.index, 0, 0)
        fw, fh = self._scrollrate

        width, height = self.GetClientSize()
        firstcol, firstrow = self.GetViewStart() # -> Scroll in Inc-steps
        x = firstcol*fw
        y = firstrow*fh
        if r.y1 <= y: 
            # If r is below and above the viewport, we prefer to scroll up
            y = r.y1
            firstrow = int(y/fh)
        elif r.y2 > y+height:
            y = r.y2-height
            firstrow = ceil(y/float(fh))
        if r.x1 <= x:
            x = r.x1
            firstcol = int(x/fw)
        elif r.x2 > x+width:
            x = r.x2-width
            firstcol = ceil(x/float(fw))
        if (firstcol, firstrow) != self.GetViewStart():
            wx.CallAfter(self.Scroll, firstcol, firstrow)
            # doesn't work when called directly. What the heck???

    def keep_cursor_on_screen(self):
        pass # not implemented
        
        
        

testtext = u"""Ein m�nnlicher Briefmark erlebte
Was Sch�nes, bevor er klebte.
Er war von einer Prinzessin beleckt.
Da war die Liebe in ihm geweckt.
Er wollte sie wiederk�ssen,
Da hat er verreisen m�ssen.
So liebte er sie vergebens.
Das ist die Tragik des Lebens.

(Joachim Ringelnatz)"""

def init_testing(redirect=True):
    app = wx.App(redirect=redirect)
    model = TextModel(testtext)
    model.set_properties(15, 24, fontsize=14)
    model.set_properties(249, 269, fontsize=14)

    frame = wx.Frame(None)
    win = wx.Panel(frame, -1)
    view = WXTextView(win, -1, style=wx.SUNKEN_BORDER)
    view.model = model
    box = wx.BoxSizer(wx.VERTICAL)
    box.Add(view, 1, wx.ALL|wx.GROW, 1)
    win.SetSizer(box)
    win.SetAutoLayout(True)

    frame.Show()    
    return locals()


    
def test_02():
    ns = init_testing(redirect=False)
    view = ns['view']
    view.cursor = 5
    view.selection = 3, 6    
    return ns


def test_03():
    ns = init_testing(redirect=False)
    model = ns['model']
    view = ns['view']
    model.set_properties(10, 20, fontsize=15)

    n = len(model)
    text = '\n12345\n'
    model.insert_text(5, text)
    model.remove(5, 5+len(text))
    assert len(model) == n
    assert len(view.layout) == n+1
    return locals()


def test_04():
    "insert/remove"
    ns = init_testing()
    model = ns['model']
    view = ns['view']
    text = model.get_text()
    n = len(model)
    for i in range(len(text)):
        model.insert_text(i, 'X')
        assert len(model) == n+1
        model.remove(i, i+1)
        assert len(model) == n

def test_05():
    "remove"
    ns = init_testing(redirect=False)
    model = ns['model']
    view = ns['view']
    text = model.get_text()
    n = len(model)
    for i in range(len(text)-1):
        old = model.remove(i, i+1)
        assert len(model) == n-1
        model.insert(i, old)
        assert len(model) == n

def test_09():
    "linebreak"
    ns = init_testing(redirect=False)
    model = ns['model']
    view = ns['view']
    text = model.get_text()
    view.set_maxw(100)
    return ns

def test_10():
    ns = init_testing(redirect=False)
    model = ns['model']
    view = ns['view']
    model.remove(0, len(model))
    model.insert(0, TextModel("123\n"))

    updater = view.updater
    updater.set_maxw(100)
    layout = view.layout
    assert layout.get_info(4, 0, 0)
    x, y =  layout.get_info(3, 0, 0)[-2:]
    u, v = layout.get_info(4, 0, 0)[-2:]
    # Cursorposition 4 must be at the begining of next line
    assert u<x # 3 must be left of 4
    assert v>y # and 4 must be below 3


def test_11():
    # Problem: Wenn man rechts neben eine Zeile klickt springt der
    # Cursor nicht an die letzte, sondern an die vorletzte Position.
    ns = init_testing(redirect=False)
    model = ns['model']
    view = ns['view']
    view.layout.dump_boxes(0, 0, 0)
    model.remove(0, len(model))
    model.insert(0, TextModel("123\n"))
    assert view.layout.get_index(100, 0) == 3

    # Problem: wenn der Text mit einem NL endet, dann funktioniert
    # get_index f�r diese letzte Zeile nicht.
    view.layout.dump_boxes(0, 0, 0)
    print view.layout.get_index(0, 1000)
    assert view.layout.get_index(0, 1000) == len(model)
            

def test_13():
    # Exception during delete 10.01.2015
    ns = init_testing(redirect=False)
    model = ns['model']
    view = ns['view']
    view.index = 271
    view.selection = (42, 42+227)
    view.cut()
    
def test_14():
    "join_undo"
    ns = init_testing(redirect=False)
    view = ns['view']
    for i, text in enumerate('abcd'):
        view.add_undo(view.insert(i, TextModel(text)))
    assert len(view._undoinfo) == 1

    view._undoinfo = [] # reset undo

    # emulate backspace
    view.add_undo(view.remove(10, 11))
    view.add_undo(view.remove(9, 10))
    assert len(view._undoinfo) == 1
    print view._undoinfo
    print repr(view._undoinfo[-1][1].get_text())

def demo_00():
    "simple demo"
    ns = test_02()
    import testing
    testing.pyshell(ns)    
    ns['app'].MainLoop()


def demo_01():
    "colorize demo"
    app = wx.App(redirect = False)
    frame = wx.Frame(None)
    win = wx.Panel(frame, -1)
    view = WXTextView(win, -1, style=wx.SUNKEN_BORDER)
    box = wx.BoxSizer(wx.VERTICAL)
    box.Add(view, 1, wx.ALL|wx.GROW, 1)
    win.SetSizer(box)
    win.SetAutoLayout(True)

    from textmodel.textmodel import pycolorize
    from textmodel import treebase
    filename = treebase.__file__.replace('pyc', 'py')
    rawtext = open(filename).read() 
    model = pycolorize(rawtext)
    #model = TextModel(rawtext.decode('latin-1'))
    view.set_model(model)
    frame.Show()
    app.MainLoop()


def demo_02():
    "empty text"
    app = wx.App(redirect = True)
    frame = wx.Frame(None)
    win = wx.Panel(frame, -1)
    view = WXTextView(win, -1, style=wx.SUNKEN_BORDER)
    box = wx.BoxSizer(wx.VERTICAL)
    box.Add(view, 1, wx.ALL|wx.GROW, 1)
    win.SetSizer(box)
    win.SetAutoLayout(True)
    model = TextModel(u'')
    view.set_model(model)
    frame.Show()
    import testing
    testing.pyshell(locals())    
    app.MainLoop()


def demo_03():
    "line break"
    ns = test_09()
    import testing
    testing.pyshell(ns)    
    ns['app'].MainLoop()

def benchmark_00():
    text = ""
    for i in range(1000):
        text += "Copy #%d \n" % i

    model = TextModel(u'Hello World!')
    model.set_properties(6, 11, fontsize=14)
    model.set_properties(0, 11, bgcolor='yellow')
    model.insert(len(model), TextModel(text))
    app = wx.App(False)

    frame = wx.Frame(None)
    view = WXTextView(frame, -1)
    view.model = model
    frame.Show()

    for i in range(100):
        model.insert_text(1000, "TEXT")

    
    
if __name__ == '__main__':
    from textmodel import alltests
    alltests.dotests()
