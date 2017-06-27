import wx
import sys
import model

class View(wx.Panel):
    def __init__(self, parent, match):
        wx.Panel.__init__(self, parent, style=wx.WANTS_CHARS)
        self.match = match
        self.game = match.game
        self.color = None
        self.path = None
        self.undo = []
        self.lines = []
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
    def solve(self):
        self.solutions = self.game.search()
        self.path = list(self.solutions[0])
        #self.path = ricochet.search(self.game, self.callback)
        #print 'solved', self.solutions
        print '\nSolutions:'
        for i, path in enumerate(self.solutions):
            print i, len(path), ', '.join(''.join(move[0:-1]) for move in path)
        #self.on_solve()
    def callback(self, depth, nodes, inner, hits):
        print 'Depth: %d, Nodes: %d (%d inner, %d hits)' % (depth, nodes, inner, hits)
    def on_solve(self):
        if not self.path:
            return
        self.do_move(*self.path.pop(0))
        self.Refresh()
        wx.CallLater(500, self.on_solve)
    def do_move(self, color, direction, index):
        start = self.game.robots[color]
        end = self.game.compute_move(color, direction)
        data = self.game.do_move(color, direction, index)
        self.undo.append(data)
        self.lines.append((color, start, end, direction))
    def undo_move(self):
        self.game.undo_move(self.undo.pop(-1))
        self.lines.pop(-1)
    def reset(self):
        for m in range(len(self.undo)):
            self.undo_move()
    def on_size(self, event):
        event.Skip()
        self.Refresh()
    def on_key_down(self, event):
        code = event.GetKeyCode()
        if code == wx.WXK_ESCAPE:
            self.GetParent().Close()
        elif code >= 32 and code < 128:
            value = chr(code)
            if value in model.COLORS:
                self.color = value
            elif value == 'S':
                self.solve()
            elif value == 'U' and self.undo:
                self.undo_move()
                self.Refresh()
            elif value == 'A':
                self.reset()
                self.Refresh()
            elif value == 'N':
                self.path = None
                self.undo = []
                self.lines = []
                self.game = self.match.next_game()
                self.Refresh()
            elif value in '1234567890':
                self.reset()
                self.path = list(self.solutions[int(value)])
                self.on_solve()
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
                #try:
                self.do_move(color, direction, 0)
                #except Exception:
                    #pass
                self.Refresh()
    def on_paint(self, event):
        colors = {
            model.RED: wx.Colour(178, 34, 34),
            model.GREEN: wx.Colour(50, 205, 50),
            model.BLUE: wx.Colour(65, 105, 225),
            model.YELLOW: wx.Colour(255, 215, 0),
        }
        if len(self.game.robots) == 5:
            colors[model.SILVER] = wx.Colour(100, 100, 100)
        dc = wx.AutoBufferedPaintDC(self)
        dc.SetBackground(wx.LIGHT_GREY_BRUSH)
        dc.Clear()
        w, h = self.GetClientSize()
        p = 40
        size = min((w - p) / 16, (h - p) / 16)
        wall = size / 8
        ox = (w - size * 16) / 2
        oy = (h - size * 16) / 2
        dc.SetDeviceOrigin(ox, oy)
        dc.SetClippingRegion(0, 0, size * 16 + 1, size * 16 + 1)
        dc.SetBrush(wx.WHITE_BRUSH)
        dc.DrawRectangle(0, 0, size * 16 + 1, size * 16 + 1)
        for color, start, end, direction in self.lines:
            dc.SetPen(wx.Pen(colors[color], 3, wx.DOT))
            x1, y1 = model.xy(start)
            x1, y1 = x1 * size + size / 2, y1 * size + size / 2
            x2, y2 = model.xy(end)
            x2, y2 = x2 * size + size / 2, y2 * size + size / 2
            if x1 > x2 and direction == 'E':
                dc.DrawLine(x1, y1, 800, y2)
                dc.DrawLine(0, y1, x2, y2)
            elif x1 < x2 and direction == 'W':
                dc.DrawLine(800, y1, x2, y2)
                dc.DrawLine(x1, y1, 0, y2)
            elif y1 > y2 and direction == 'S':
                dc.DrawLine(x1, y1, x2, 800)
                dc.DrawLine(x1, 0, x2, y2)
            elif y1 < y2 and direction == 'N':
                dc.DrawLine(x1, 800, x2, y2)
                dc.DrawLine(x1, y1, x2, 0)
            else:
                dc.DrawLine(x1, y1, x2, y2)
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
                    dc.SetBrush(wx.Brush(colors[self.game.token[0]]))
                    dc.DrawRectangle(x, y, size + 1, size + 1)
                if i in (7, 8) and j in (7, 8):
                    dc.SetBrush(wx.LIGHT_GREY_BRUSH)
                    dc.DrawRectangle(x, y, size + 1, size + 1)
                # robot
                if robot:
                    dc.SetBrush(wx.Brush(colors[robot]))
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
                # bumpers
                if model.LEFT in cell:
                    bumper_color = [c for c in colors.keys() if c in cell][0]
                    dc.SetPen(wx.Pen(colors[bumper_color], 9))
                    dc.DrawLine(x, y, x + size, y + size)
                if model.RIGHT in cell:
                    bumper_color = [c for c in colors.keys() if c in cell][0]
                    dc.SetPen(wx.Pen(colors[bumper_color], 9))
                    dc.DrawLine(x + size, y, x, y + size)
        dc.DrawText(str(self.game.moves), wall + 1, wall + 1)

class Frame(wx.Frame):
    def __init__(self, seed=None, num_robots=None, quads=None):
        wx.Frame.__init__(self, None, -1, 'Ricochet Robot!')
        print seed, num_robots
        match = model.Match(seed, quads=quads, num_robots=num_robots)
        #game = model.Game.hardest()
        self.view = View(self, match)
        self.view.SetSize((800, 800))
        self.Fit()

def main():
    app = wx.App(False)
    seed = int(sys.argv[1]) if len(sys.argv) >= 2 else None
    periodic = bool(int(sys.argv[2])) if len(sys.argv) >= 3 else False
    num_robots = int(sys.argv[3]) if len(sys.argv) >= 4 else 4
    quad_list = sys.argv[4].split(',') if len(sys.argv) == 5 else None
    print seed, num_robots, periodic, quad_list
    s_quads = model.P_QUADS if periodic else model.QUADS
    quads = [s_quads[model.COLORS.index(s[0])][int(s[1])-1] for s in quad_list] if quad_list else None
    frame = Frame(seed, num_robots, quads)
    frame.Center()
    frame.Show()
    app.MainLoop()

if __name__ == '__main__':
    main()
