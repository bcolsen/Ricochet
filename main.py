import wx
import model

class View(wx.Panel):
    def __init__(self, parent, game):
        wx.Panel.__init__(self, parent, style=wx.WANTS_CHARS)
        self.game = game
        self.color = None
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
    def on_size(self, event):
        event.Skip()
        self.Refresh()
    def on_key_down(self, event):
        code = event.GetKeyCode()
        if code == wx.WXK_ESCAPE:
            self.game = model.Game()
            self.Refresh()
        elif code >= 32 and code < 128:
            value = chr(code)
            if value in model.COLORS:
                self.color = value
        elif self.color:
            lookup = {
                wx.WXK_UP: model.NORTH,
                wx.WXK_RIGHT: model.EAST,
                wx.WXK_DOWN: model.SOUTH,
                wx.WXK_LEFT: model.WEST,
            }
            if code in lookup:
                color = self.color
                direction = lookup[code]
                try:
                    self.game.do_move(color, direction)
                except Exception:
                    pass
                self.Refresh()
    def on_paint(self, event):
        brushes = {
            model.RED: wx.Brush(wx.Colour(255, 0, 0)),
            model.GREEN: wx.Brush(wx.Colour(0, 255, 0)),
            model.BLUE: wx.Brush(wx.Colour(0, 0, 255)),
            model.YELLOW: wx.Brush(wx.Colour(255, 255, 0)),
        }
        dc = wx.AutoBufferedPaintDC(self)
        dc.SetBackground(wx.LIGHT_GREY_BRUSH)
        dc.Clear()
        w, h = self.GetClientSize()
        p = 40
        size = min((w - p) / 16, (h - p) / 16)
        wall = size / 10
        ox = (w - size * 16) / 2
        oy = (h - size * 16) / 2
        dc.SetDeviceOrigin(ox, oy)
        dc.SetClippingRegion(0, 0, size * 16 + 1, size * 16 + 1)
        dc.SetBrush(wx.WHITE_BRUSH)
        dc.DrawRectangle(0, 0, size * 16 + 1, size * 16 + 1)
        for j in range(16):
            for i in range(16):
                x = i * size
                y = j * size
                index = model.idx(i, j)
                cell  = self.game.grid[index]
                robot = self.game.get_robot(index)
                # border
                dc.SetPen(wx.BLACK_PEN)
                dc.SetBrush(wx.TRANSPARENT_BRUSH)
                dc.DrawRectangle(x, y, size + 1, size + 1)
                # token
                if self.game.token in cell:
                    dc.SetBrush(brushes[self.game.token[0]])
                    dc.DrawRectangle(x, y, size + 1, size + 1)
                # robot
                if robot:
                    dc.SetBrush(brushes[robot])
                    dc.DrawCircle(x + size / 2, y + size / 2, size / 3)
                # walls
                dc.SetBrush(wx.BLACK_BRUSH)
                if model.NORTH in cell:
                    dc.DrawRectangle(x, y, size + 1, wall)
                    dc.DrawCircle(x, y, wall - 1)
                    dc.DrawCircle(x + size, y, wall - 1)
                if model.EAST in cell:
                    dc.DrawRectangle(x + size + 1, y, -wall, size + 1)
                    dc.DrawCircle(x + size, y, wall - 1)
                    dc.DrawCircle(x + size, y + size, wall - 1)
                if model.SOUTH in cell:
                    dc.DrawRectangle(x, y + size + 1, size + 1, -wall)
                    dc.DrawCircle(x, y + size, wall - 1)
                    dc.DrawCircle(x + size, y + size, wall - 1)
                if model.WEST in cell:
                    dc.DrawCircle(x, y, wall - 1)
                    dc.DrawCircle(x, y + size, wall - 1)
                    dc.DrawRectangle(x, y, wall, size + 1)
        dc.DrawText(str(self.game.moves), wall + 1, wall + 1)

class Frame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, 'Ricochet Robots!')
        self.view = View(self, model.Game())
        self.view.SetSize((800, 800))
        self.Fit()

def main():
    app = wx.PySimpleApp()
    frame = Frame()
    frame.Center()
    frame.Show()
    app.MainLoop()

if __name__ == '__main__':
    main()