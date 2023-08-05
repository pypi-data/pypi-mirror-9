#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- no-plot -*-
"""
Demo showing the capabilities of qtgr
"""

# standard library
import sys
setattr(sys, "QT_BACKEND_ORDER", ["PyQt4", "PySide"])
import os
import time
import logging
# third party
from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4 import uic
# local library
import gr # TESTING shell
import qtgr
from qtgr.events import GUIConnector, MouseEvent, PickEvent, LegendEvent
from gr.pygr import Plot, PlotAxes, PlotCurve, ErrorBar

__author__ = "Christian Felder <c.felder@fz-juelich.de>"
__copyright__ = """Copyright 2012-2014 Forschungszentrum Juelich GmbH

This file is part of GR, a universal framework for visualization applications.
Visit http://gr-framework.org for the latest
version.

GR was developed by the Scientific IT-Systems group at the Peter Grünberg
Institute at Forschunsgzentrum Jülich. The main development has been done
by Josef Heinen who currently maintains the software.

GR is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This framework is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with GR. If not, see <http://www.gnu.org/licenses/>.
 
"""

_log = logging.getLogger(__name__)

class MainWindow(QtGui.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                "qtgrdemo.ui"), self)

        dictPrintType = dict(gr.PRINT_TYPE)
        map(dictPrintType.pop, [gr.PRINT_JPEG, gr.PRINT_TIF])
        self._saveTypes = (";;".join(dictPrintType.values()) + ";;" +
                           ";;".join(gr.GRAPHIC_TYPE.values()))
        self._saveName = None
        self._title = unicode(self.windowTitle())
        self._startupTime = time.time()

        self._chkLogX.stateChanged.connect(self._logXClicked)
        self._chkLogY.stateChanged.connect(self._logYClicked)
        self._chkGrid.stateChanged.connect(self._gridClicked)
        self._chkErr.stateChanged.connect(self._errorsClicked)
        self._chkKeepRatio.stateChanged.connect(self._keepRatioClicked)
        self._btnReset.clicked.connect(self._resetClicked)
        self._btnPick.clicked.connect(self._pickClicked)
        self._shell.returnPressed.connect(self._shellEx)
        self._actionSave.triggered.connect(self.save)
        self._actionPrint.triggered.connect(self.printGR)
        self._gr.logXinDomain.connect(self._logXinDomain)
        self._gr.logYinDomain.connect(self._logYinDomain)
        self._gr.modePick.connect(self._pickModeChanged)

        guiConn = GUIConnector(self._gr)
        guiConn.connect(MouseEvent.MOUSE_MOVE, self.mouseMoveGr)
        guiConn.connect(PickEvent.PICK_PRESS, self.pointPickGr)
        guiConn.connect(LegendEvent.ROI_CLICKED, self.legendClick)
        guiConn.connect(LegendEvent.ROI_OVER, self.legendOver)

        x = [-3.3 + t * .1 for t in range(66)]
        y = [t ** 5 - 13 * t ** 3 + 36 * t for t in x]
        x2 = [-3.5 + i * .5 for i in range(0, 15)]
        y2 = x2

        dneg = map(lambda y: y - 0.25 * abs(y), y)
        dpos = map(lambda y: y + 0.25 * abs(y), y)
        self._errBar = ErrorBar(x, y, dneg, dpos)

        self._plot = Plot((.1, .92, .2, .88))
        self._plot.offsetXLabel = -.1

        self._curveFoo = PlotCurve(x, y, legend="foo bar")
        axes = PlotAxes(self._plot.viewport).addCurves(self._curveFoo)
        axes.setXtickCallback(self._xtickCallBack)
        self._plot.addAxes(axes, PlotAxes(self._plot.viewport,
                                          drawX=False).plot(x2, y2))

        self._plot2 = Plot((.1, .95, .15, .88))
        self._plot2.addAxes(PlotAxes(self._plot2.viewport).addCurves(
                                         PlotCurve(x2, y2, legend="second")))

        self._plot.title = "QtGR Demo"
        self._plot.subTitle = "Multiple Axes Example"
        self._plot.xlabel = "x"
        self._plot.ylabel = "f(x)"
        self._plot.setLegend(True)
        self._gr.addPlot(self._plot)

        self._plot2.title = "Second Widget"
        self._plot2.subTitle = "Linear Example (less interactive)"
        self._plot2.xlabel = "x2"
        self._plot2.ylabel = "f2(x2)"
        self._plot2.setLegend(True)
        self._plot2.setGrid(False)
        self._gr2.addPlot(self._plot2)

    def save(self):
        qpath = QtGui.QFileDialog.getSaveFileName(self, "", "", self._saveTypes,
                                                  gr.PRINT_TYPE[gr.PRINT_PDF])
        if qpath:
            path = unicode(qpath)
            (_p, suffix) = os.path.splitext(path)
            suffix = suffix.lower()
            if suffix and (suffix[1:] in gr.PRINT_TYPE.keys() or
                           suffix[1:] in gr.GRAPHIC_TYPE):
                self._gr.save(path)
                self._saveName = os.path.basename(path)
                self.setWindowTitle(self._title + " - %s"
                                    % self._saveName)
            else:
                raise Exception("Unsupported file format")

    def printGR(self):
        if self._saveName:
            title = "GR_Demo-" + self._saveName
        else:
            title = "GR_Demo-untitled"
        self._gr.printDialog(title)

    def mouseMoveGr(self, event):
        dc = event.getDC()
        ndc = event.getNDC()
        wc = event.getWC(self._plot.viewport)
        self._statusbar.showMessage("DC: (%4d, %4d)\t " % (dc.x, dc.y) +
                                    "NDC: (%3.2f, %3.2f)\t " % (ndc.x, ndc.y) +
                                    "WC: (%3.2f, %3.2f)" % (wc.x, wc.y))
        self._lblOverLegend.setText("")

    def pointPickGr(self, event):
        p = event.getWC(event.viewport)

        if p.x < 0:
            self._lblPickX.setText("%4.2f" % p.x)
        else:
            self._lblPickX.setText(" %4.2f" % p.x)

        if p.y < 0:
            self._lblPickY.setText("%4.2f" % p.y)
        else:
            self._lblPickY.setText(" %4.2f" % p.y)

    def legendClick(self, event):
        if event.getButtons() & MouseEvent.LEFT_BUTTON:
            event.curve.visible = not event.curve.visible
            self._gr.update()

    def legendOver(self, event):
        self._lblOverLegend.setText(event.curve.legend)

    def _xtickCallBack(self, x, y, svalue):
        gr.setcharup(1., 1.)
        gr.settextalign(gr.TEXT_HALIGN_LEFT, gr.TEXT_VALIGN_TOP)
        try:
            gr.text(x, y, "%s (%s)"
                    % (time.strftime("%H:%M:%S",
                                     time.localtime(self._startupTime
                                                    + float(svalue))), svalue))
        except ValueError:
            gr.text(x, y, svalue)
        gr.setcharup(0., 1.)

    def _errorsClicked(self, state):
        if self._chkErr.isChecked():
            self._curveFoo.errorBar1 = self._errBar
        else:
            self._curveFoo.errorBar1 = None
        self._gr.update()

    def _keepRatioClicked(self, state):
        self._gr.keepRatio = self._chkKeepRatio.isChecked()
        self._gr.update()

    def _gridClicked(self, state):
        self._plot.setGrid(self._chkGrid.isChecked())
        self._gr.update()

    def _logXClicked(self, state):
        self._plot.setLogX(self._chkLogX.isChecked())
        self._gr.update()

    def _logYClicked(self, state):
        self._plot.setLogY(self._chkLogY.isChecked())
        self._gr.update()

    def _resetClicked(self):
        self._plot.reset()
        self._gr.update()

    def _pickClicked(self):
        self._gr.setPickMode(True)

    def _pickModeChanged(self, bool):
        self._btnPick.setChecked(bool)

    @QtCore.pyqtSlot()
    def _shellEx(self):
        input = str(self._shell.text())
        exec input
        self._shell.clear()
        self._gr.update()

    def _logXinDomain(self, bool):
        self._chkLogX.setEnabled(bool)
        if not bool:
            self._chkLogX.setChecked(bool)

    def _logYinDomain(self, bool):
        self._chkLogY.setEnabled(bool)
        if not bool:
            self._chkLogY.setChecked(bool)

if __name__ == '__main__':
    import sys
#    logging.basicConfig(level=logging.CRITICAL)
#    for name in [__name__, qtgr.__name__, qtgr.events.__name__,
#                 qtgr.events.base.__name__,
#                 gr.pygr.base.__name__, gr.pygr.__name__]:
#        logging.getLogger(name).setLevel(logging.DEBUG)
    app = QtGui.QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
