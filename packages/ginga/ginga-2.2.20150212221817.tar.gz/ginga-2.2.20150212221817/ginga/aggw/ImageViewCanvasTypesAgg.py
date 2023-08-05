#
# ImageViewCanvasTypesAgg.py -- drawing classes for ImageViewCanvas widget
# 
# Eric Jeschke (eric@naoj.org)
#
# Copyright (c) Eric R. Jeschke.  All rights reserved.
# This is open-source software licensed under a BSD license.
# Please see the file LICENSE.txt for details.

import math
import aggdraw as agg
from . import AggHelp
from itertools import chain

from ginga.canvas.mixins import *
from ginga import Mixins
from ginga.misc import Callback, Bunch
from ginga import colors
from ginga.util.six.moves import map, zip


class AggCanvasMixin(object):

    def setup_cr(self):
        cr = AggHelp.AggContext(self.viewer.get_surface())
        return cr

    def get_pen(self, cr):
        alpha = getattr(self, 'alpha', 1.0)
        pen = cr.get_pen(self.color, alpha=alpha)
        return pen
        
    def get_brush(self, cr):
        fill = getattr(self, 'fill', False)
        if fill:
            if hasattr(self, 'fillcolor') and self.fillcolor:
                color = self.fillcolor
            else:
                color = self.color
            alpha = getattr(self, 'alpha', 1.0)
            alpha = getattr(self, 'fillalpha', alpha)
            brush = cr.get_brush(color, alpha=alpha)
        else:
            brush = None
        return brush
        
    def draw_arrowhead(self, cr, x1, y1, x2, y2, pen):
        i1, j1, i2, j2 = self.calcVertexes(x1, y1, x2, y2)
        alpha = getattr(self, 'alpha', 1.0)
        brush = cr.get_brush(self.color, alpha=alpha)
        cr.canvas.polygon((x2, y2, i1, j1, i2, j2),
                          pen, brush)
        
    def _draw_cap(self, cr, pen, brush, cap, x, y, radius=None):
        if radius is None:
            radius = self.cap_radius
        if cap == 'ball':
            #cr.arc(x, y, radius, 0, 2*math.pi)
            cr.canvas.ellipse((x-radius, y-radius, x+radius, y+radius),
                              pen, brush)
        
    def draw_caps(self, cr, cap, points, radius=None):
        alpha = getattr(self, 'alpha', 1.0)
        pen = cr.get_pen(self.color, alpha=alpha)
        brush = cr.get_brush(self.color, alpha=alpha)

        for x, y in points:
            self._draw_cap(cr, pen, brush, cap, x, y, radius=radius)
        
    def draw_edit(self, cr):
        cpoints = self.get_cpoints(points=self.get_edit_points())
        self.draw_caps(cr, 'ball', cpoints)

    def text_extents(self, cr, text, font):
        return cr.text_extents(text, font)


class Text(TextBase, AggCanvasMixin):

    def draw(self):
        cx, cy = self.canvascoords(self.x, self.y)

        cr = self.setup_cr()
        if not self.fontsize:
            fontsize = self.scale_font()
        else:
            fontsize = self.fontsize
        alpha = getattr(self, 'alpha', 1.0)
        font = cr.get_font(self.font, fontsize, self.color,
                           alpha=alpha)
        cr.canvas.text((cx, cy), self.text, font)

        if self.editing:
            self.draw_edit(cr)
        elif self.showcap:
            self.draw_caps(cr, self.cap, ((cx, cy), ))

    def get_dimensions(self):
        cr = self.setup_cr()
        if not self.fontsize:
            fontsize = self.scale_font()
        else:
            fontsize = self.fontsize
        font = cr.get_font(self.font, fontsize, self.color)
        return self.text_extents(cr, self.text, font)


class Polygon(PolygonBase, AggCanvasMixin):

    def draw(self):
        cpoints = self.get_cpoints()
        cr = self.setup_cr()
        pen = self.get_pen(cr)
        brush = self.get_brush(cr)

        cr.canvas.polygon(list(chain.from_iterable(cpoints)), 
                          pen, brush)

        if self.editing:
            self.draw_edit(cr)
        elif self.showcap:
            self.draw_caps(cr, self.cap, cpoints)


class Rectangle(RectangleBase, AggCanvasMixin):

    def draw(self):
        cpoints = list(map(lambda p: self.canvascoords(p[0], p[1]),
                           ((self.x1, self.y1), (self.x2, self.y1),
                            (self.x2, self.y2), (self.x1, self.y2))))

        cr = self.setup_cr()
        pen = self.get_pen(cr)
        brush = self.get_brush(cr)

        cr.canvas.polygon(list(chain.from_iterable(cpoints)),
                          pen, brush)

        if self.editing:
            self.draw_edit(cr)
        elif self.showcap:
            self.draw_caps(cr, self.cap, cpoints)

        if self.drawdims:
            fontsize = self.scale_font()
            alpha = getattr(self, 'alpha', 1.0)
            font = cr.get_font(self.font, fontsize, self.color,
                               alpha=alpha)

            cx1, cy1 = cpoints[0]
            cx2, cy2 = cpoints[2]
            # draw label on X dimension
            cx = cx1 + (cx2 - cx1) // 2
            cy = cy2 + -4
            text = "%d" % (self.x2 - self.x1)
            cr.canvas.text((cx, cy), text, font)

            cy = cy1 + (cy2 - cy1) // 2
            cx = cx2 + 4
            text = "%d" % (self.y2 - self.y1)
            cr.canvas.text((cx, cy), text, font)


class Square(Rectangle):
    pass


class Circle(CircleBase, AggCanvasMixin):
    def draw(self):
        cx1, cy1, cradius = self.calc_radius(self.x, self.y, self.radius)

        cr = self.setup_cr()
        pen = self.get_pen(cr)
        brush = self.get_brush(cr)

        cr.canvas.ellipse((cx1-cradius, cy1-cradius, cx1+cradius, cy1+cradius),
                          pen, brush)

        if self.editing:
            self.draw_edit(cr)
        elif self.showcap:
            self.draw_caps(cr, self.cap, ((cx1, cy1), ))


class Ellipse(EllipseBase, AggCanvasMixin):

    def draw(self):
        cp = self.get_cpoints(points=self.get_bezier_pts())
        cr = self.setup_cr()

        pen = self.get_pen(cr)
        brush = self.get_brush(cr)

        # draw 4 bezier curves to make the ellipse
        # TODO: currently there is a bug in aggdraw paths
        path = agg.Path()
        path.moveto(cp[0][0], cp[0][1])
        path.curveto(cp[1][0], cp[1][1], cp[2][0], cp[2][1], cp[3][0], cp[3][1])
        path.curveto(cp[4][0], cp[4][1], cp[5][0], cp[5][1], cp[6][0], cp[6][1])
        path.curveto(cp[7][0], cp[7][1], cp[8][0], cp[8][1], cp[9][0], cp[9][1])
        path.curveto(cp[10][0], cp[10][1], cp[11][0], cp[11][1], cp[12][0], cp[12][1])
        cr.canvas.path(path.coords(), path, pen, brush)

        if self.editing:
            self.draw_edit(cr)
        elif self.showcap:
            cpoints = self.get_cpoints()
            self.draw_caps(cr, self.cap, cpoints)
        

class Box(BoxBase, AggCanvasMixin):

    def draw(self):
        cpoints = self.get_cpoints()
        cr = self.setup_cr()
        pen = self.get_pen(cr)
        brush = self.get_brush(cr)

        cr.canvas.polygon(list(chain.from_iterable(cpoints)), 
                          pen, brush)

        if self.editing:
            self.draw_edit(cr)
        elif self.showcap:
            self.draw_caps(cr, self.cap, cpoints)


class Point(PointBase, AggCanvasMixin):

    def draw(self):
        cx, cy, cradius = self.calc_radius(self.x, self.y, self.radius)
        cx1, cy1 = cx - cradius, cy - cradius
        cx2, cy2 = cx + cradius, cy + cradius

        cr = self.setup_cr()
        pen = self.get_pen(cr)
        #cr.set_line_cap(cairo.LINE_CAP_ROUND)
        if self.style == 'cross':
            cr.canvas.line((cx1, cy1, cx2, cy2), pen)
            cr.canvas.line((cx1, cy2, cx2, cy1), pen)
        else:
            cr.canvas.line((cx, cy1, cx, cy2), pen)
            cr.canvas.line((cx1, cy, cx2, cy), pen)

        if self.editing:
            self.draw_edit(cr)
        elif self.showcap:
            self.draw_caps(cr, self.cap, ((cx, cy), ))


class Line(LineBase, AggCanvasMixin):
        
    def draw(self):
        cx1, cy1 = self.canvascoords(self.x1, self.y1)
        cx2, cy2 = self.canvascoords(self.x2, self.y2)

        cr = self.setup_cr()
        pen = self.get_pen(cr)
        #cr.set_line_cap(cairo.LINE_CAP_ROUND)
        cr.canvas.line((cx1, cy1, cx2, cy2), pen)

        if self.arrow == 'end':
            self.draw_arrowhead(cr, cx1, cy1, cx2, cy2, pen)
            caps = [(cx1, cy1)]
        elif self.arrow == 'start':
            self.draw_arrowhead(cr, cx2, cy2, cx1, cy1, pen)
            caps = [(cx2, cy2)]
        elif self.arrow == 'both':
            self.draw_arrowhead(cr, cx2, cy2, cx1, cy1, pen)
            self.draw_arrowhead(cr, cx1, cy1, cx2, cy2, pen)
            caps = []
        else:
            caps = [(cx1, cy1), (cx2, cy2)]

        if self.editing:
            self.draw_edit(cr)
        elif self.showcap:
            self.draw_caps(cr, self.cap, caps)


class Path(PathBase, AggCanvasMixin):

    def draw(self):
        cpoints = list(map(lambda p: self.canvascoords(p[0], p[1]),
                           self.points))
        cr = self.setup_cr()
        pen = self.get_pen(cr)

        # TODO: see if there is a path type in aggdraw and if so, use it
        for i in range(len(cpoints) - 1):
            cx1, cy1 = cpoints[i]
            cx2, cy2 = cpoints[i+1]
            cr.canvas.line((cx1, cy1, cx2, cy2), pen)

        if self.editing:
            self.draw_edit(cr)
        elif self.showcap:
            self.draw_caps(cr, self.cap, cpoints)


class Compass(CompassBase, AggCanvasMixin):

    def draw(self):
        (cx1, cy1), (cx2, cy2), (cx3, cy3) = self.get_cpoints()
        cr = self.setup_cr()

        pen = self.get_pen(cr)
        # draw North line and arrowhead
        #cr.set_line_cap(cairo.LINE_CAP_ROUND)
        cr.canvas.line((cx1, cy1, cx2, cy2), pen)
        self.draw_arrowhead(cr, cx1, cy1, cx2, cy2, pen)

        # draw East line and arrowhead
        cr.canvas.line((cx1, cy1, cx3, cy3), pen)
        self.draw_arrowhead(cr, cx1, cy1, cx3, cy3, pen)

        # draw "N" & "E"
        if not self.fontsize:
            fontsize = self.scale_font()
        else:
            fontsize = self.fontsize
        alpha = getattr(self, 'alpha', 1.0)
        font = cr.get_font(self.font, fontsize, self.color,
                           alpha=alpha)
        cx, cy = self.get_textpos(cr, 'N', cx1, cy1, cx2, cy2, font)
        cr.canvas.text((cx, cy), 'N', font)

        cx, cy = self.get_textpos(cr, 'E', cx1, cy1, cx3, cy3, font)
        cr.canvas.text((cx, cy), 'E', font)

        if self.editing:
            self.draw_edit(cr)
        elif self.showcap:
            self.draw_caps(cr, self.cap, ((cx1, cy1), ))

    def get_textpos(self, cr, text, cx1, cy1, cx2, cy2, font):
        htwd, htht = self.text_extents(cr, text, font)

        diag_xoffset = 0
        diag_yoffset = 0
        xplumb_yoffset = 0
        yplumb_xoffset = 0

        diag_yoffset = 14
        if abs(cy1 - cy2) < 5:
            pass
        elif cy1 < cy2:
            xplumb_yoffset = -4
        else:
            xplumb_yoffset = 14
            diag_yoffset = -4
        
        if abs(cx1 - cx2) < 5:
            diag_xoffset = -(4 + htwd)
        elif (cx1 < cx2):
            diag_xoffset = -(4 + htwd)
            yplumb_xoffset = 4
        else:
            diag_xoffset = 4
            yplumb_xoffset = -(4 + 0)

        xh = min(cx1, cx2); y = cy1 + xplumb_yoffset
        xh += (max(cx1, cx2) - xh) // 2
        yh = min(cy1, cy2); x = cx2 + yplumb_xoffset
        yh += (max(cy1, cy2) - yh) // 2

        xd = xh + diag_xoffset
        yd = yh + diag_yoffset
        return (xd, yd)

        
class RightTriangle(RightTriangleBase, AggCanvasMixin):

    def draw(self):
        cpoints = list(map(lambda p: self.canvascoords(p[0], p[1]),
                           ((self.x1, self.y1), (self.x2, self.y2),
                            (self.x2, self.y1))))

        cr = self.setup_cr()
        pen = self.get_pen(cr)
        brush = self.get_brush(cr)

        cr.canvas.polygon(list(chain.from_iterable(cpoints)),
                          pen, brush)

        if self.editing:
            self.draw_edit(cr)
        elif self.showcap:
            self.draw_caps(cr, self.cap, cpoints)


class Triangle(TriangleBase, AggCanvasMixin):

    def draw(self):
        cpoints = self.get_cpoints()

        cr = self.setup_cr()
        pen = self.get_pen(cr)
        brush = self.get_brush(cr)

        cr.canvas.polygon(list(chain.from_iterable(cpoints)),
                          pen, brush)

        if self.editing:
            self.draw_edit(cr)
        elif self.showcap:
            self.draw_caps(cr, self.cap, cpoints)


class Ruler(RulerBase, AggCanvasMixin):

    def draw(self):
        cx1, cy1 = self.canvascoords(self.x1, self.y1)
        cx2, cy2 = self.canvascoords(self.x2, self.y2)

        text_x, text_y, text_h = self.get_ruler_distances()

        cr = self.setup_cr()
        pen = self.get_pen(cr)
        
        if not self.fontsize:
            fontsize = self.scale_font()
        else:
            fontsize = self.fontsize
        alpha = getattr(self, 'alpha', 1.0)
        font = cr.get_font(self.font, fontsize, self.color,
                           alpha=alpha)

        # draw the line connecting the start and end drag points
        # and add arrows on each end
        #cr.set_line_cap(cairo.LINE_CAP_ROUND)
        cr.canvas.line((cx1, cy1, cx2, cy2), pen)
        self.draw_arrowhead(cr, cx1, cy1, cx2, cy2, pen)
        self.draw_arrowhead(cr, cx2, cy2, cx1, cy1, pen)

        #cr.set_dash([ 3.0, 4.0, 6.0, 4.0], 5.0)

        # calculate offsets and positions for drawing labels
        # try not to cover anything up
        xtwd, xtht = self.text_extents(cr, text_x, font)
        ytwd, ytht = self.text_extents(cr, text_y, font)
        htwd, htht = self.text_extents(cr, text_h, font)

        diag_xoffset = 0
        diag_yoffset = 0
        xplumb_yoffset = 0
        yplumb_xoffset = 0

        diag_yoffset = 14
        if abs(cy1 - cy2) < 5:
            show_angle = 0
        elif cy1 < cy2:
            #xplumb_yoffset = -4
            xplumb_yoffset = -16
        else:
            #xplumb_yoffset = 14
            xplumb_yoffset = 4
            diag_yoffset = -4
        
        if abs(cx1 - cx2) < 5:
            diag_xoffset = -(4 + htwd)
            show_angle = 0
        elif (cx1 < cx2):
            diag_xoffset = -(4 + htwd)
            yplumb_xoffset = 4
        else:
            diag_xoffset = 4
            yplumb_xoffset = -(4 + ytwd)

        xh = min(cx1, cx2); y = cy1 + xplumb_yoffset
        xh += (max(cx1, cx2) - xh) // 2
        yh = min(cy1, cy2); x = cx2 + yplumb_xoffset
        yh += (max(cy1, cy2) - yh) // 2

        xd = xh + diag_xoffset
        yd = yh + diag_yoffset
        cr.canvas.text((xd, yd), text_h, font)

        if self.showplumb:
            if self.color2:
                pen = cr.get_pen(self.color2, linewidth=self.linewidth,
                                 alpha=alpha)
                font = cr.get_font(self.font, fontsize, self.color2,
                                   alpha=alpha)

            # draw X plumb line
            cr.canvas.line((cx1, cy1, cx2, cy1), pen)

            # draw Y plumb line
            cr.canvas.line((cx2, cy1, cx2, cy2), pen)

            # draw X plum line label
            xh -= xtwd // 2
            cr.canvas.text((xh, y), text_x, font)

            # draw Y plum line label
            cr.canvas.text((x, yh), text_y, font)

        if self.editing:
            self.draw_edit(cr)
        elif self.showcap:
            self.draw_caps(cr, self.cap, ((cx2, cy1), ))


class Image(ImageBase, AggCanvasMixin):

    def draw(self):
        # currently, drawing of images is handled in base class
        # here we just draw the caps
        ImageBase.draw(self)
        
        cpoints = self.get_cpoints()
        cr = self.setup_cr()

        # draw border
        if self.linewidth > 0:
            pen = self.get_pen(cr)
            cr.canvas.polygon(list(chain.from_iterable(cpoints)), 
                              pen)

        if self.editing:
            self.draw_edit(cr)
        elif self.showcap:
            self.draw_caps(cr, self.cap, cpoints)


class NormImage(NormImageBase, AggCanvasMixin):

    def draw(self):
        # currently, drawing of images is handled in base class
        # here we just draw the caps
        ImageBase.draw(self)
        
        cpoints = self.get_cpoints()
        cr = self.setup_cr()

        # draw border
        if self.linewidth > 0:
            pen = self.get_pen(cr)
            cr.canvas.polygon(list(chain.from_iterable(cpoints)), 
                              pen)

        if self.editing:
            self.draw_edit(cr)
        elif self.showcap:
            self.draw_caps(cr, self.cap, cpoints)


class DrawingCanvas(DrawingMixin, CanvasMixin, CompoundMixin,
                    CanvasObjectBase, AggCanvasMixin, 
                    Mixins.UIMixin, Callback.Callbacks):
    def __init__(self):
        CanvasObjectBase.__init__(self)
        AggCanvasMixin.__init__(self)
        CompoundMixin.__init__(self)
        CanvasMixin.__init__(self)
        Callback.Callbacks.__init__(self)
        Mixins.UIMixin.__init__(self)
        DrawingMixin.__init__(self, drawCatalog)
        self.kind = 'drawingcanvas'


drawCatalog = dict(text=Text, rectangle=Rectangle, circle=Circle,
                   line=Line, point=Point, polygon=Polygon, path=Path, 
                   ellipse=Ellipse, square=Square, box=Box,
                   triangle=Triangle, righttriangle=RightTriangle,
                   ruler=Ruler, compass=Compass,
                   compoundobject=CompoundObject, canvas=Canvas,
                   drawingcanvas=DrawingCanvas,
                   image=Image, normimage=NormImage)

        
#END
