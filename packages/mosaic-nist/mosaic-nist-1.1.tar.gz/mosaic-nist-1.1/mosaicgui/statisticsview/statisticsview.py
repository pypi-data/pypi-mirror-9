from __future__ import with_statement

import sys
import math
import os
import csv
import sqlite3

import numpy as np
from scipy.optimize import curve_fit
from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtCore import Qt

import mosaic.sqlite3MDIO as sqlite
from mosaic.utilities.resource_path import resource_path, last_file_in_directory
import mosaicgui.sqlQueryWorker as sqlworker

css = """QLabel {
      color: black;
}"""


class StatisticsWindow(QtGui.QDialog):
	def __init__(self, parent = None):
		self.v=[]

		super(StatisticsWindow, self).__init__(parent)

		# uic.loadUi(os.path.join(os.path.dirname(os.path.abspath(__file__)),"statisticsview.ui"), self)
		uic.loadUi(resource_path("statisticsview.ui"), self)
		
		self._positionWindow()

		self.idleTimer=QtCore.QTimer()
		self.idleTimer.start(3000)

		self.queryString="select AbsEventStart from metadata where ProcessingStatus='normal' order by AbsEventStart ASC"
		self.queryData=[]
		self.totalEvents=0
		self.elapsedTime=0.0

		self.qWorker=None
		self.qThread=QtCore.QThread()

		# Set QLabel properties
		self.neventsLabel.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
		self.errorrateLabel.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
		self.caprateLabel.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)

	def openDB(self, dbpath):
		"""
			Open the latest sqlite file in a directory
		"""
		self.openDBFile( last_file_in_directory(dbpath, "*sqlite") )

	def openDBFile(self, dbfile):
		"""
			Open a specific database file.
		"""
		# Create an index to speed up queries
		self._createDBIndex(dbfile)
		
		self.qWorker=sqlworker.sqlQueryWorker(dbfile)
	
		# Connect signals and slots
		self.qWorker.resultsReady2.connect(self.OnDataReady)

		self.qWorker.moveToThread(self.qThread)
	
		self.qWorker.finished.connect(self.qThread.quit)

		self.qThread.start()

		# reset elapsed time
		self.elapsedTime=0.0

		# Query the DB
		self._updatequery()

		# Idle processing
		QtCore.QObject.connect(self.idleTimer, QtCore.SIGNAL('timeout()'), self.OnAppIdle)

	def closeDB(self):
		pass

	def _positionWindow(self):
		"""
			Position settings window at the top left corner
		"""
		if sys.platform=='win32':
			self.setGeometry(1050, 30, 375, 200)
		else:
			self.setGeometry(1050, 0, 375, 200)
		# self.move( (-screen.width()/2)+200, -screen.height()/2 )

	def _createDBIndex(self, dbfile):
		db = sqlite3.connect(dbfile, detect_types=sqlite3.PARSE_DECLTYPES)
		with db:
			db.execute('CREATE INDEX IF NOT EXISTS statisticsAbsEventStartIndex ON metadata (AbsEventStart, ProcessingStatus)')
			db.execute('CREATE INDEX IF NOT EXISTS statisticsProcessingStatusIndex ON metadata (ProcessingStatus)')
		db.commit()
		db.close()

	def _updatequery(self):
		self.qThread.start()
		QtCore.QMetaObject.invokeMethod(self.qWorker, 'queryDB2', Qt.QueuedConnection, 
				QtCore.Q_ARG(str, self.queryString),
				QtCore.Q_ARG(str, "select ProcessingStatus from metadata") 
			)
		self.queryRunning=True

	def OnDataReady(self, res1, res2, errorstr):
		if not errorstr:
			try:
				self.queryData=np.hstack(res1)
				self.totalEvents=len( res2 )

				c=self._caprate()

				self.neventsLabel.setText( str(self.totalEvents) )
				self.errorrateLabel.setText( str(round(100.*(1 - len(self.queryData)/float(self.totalEvents)), 2)) + ' %' )
				self.caprateLabel.setText( str(c[0]) + " &#177; " + str(c[1]) + " s<sup>-1</sup>" )
				self.elapsedtimeLabel.setText( self._formatelapsedtime() )

				self.queryRunning=False
			except ZeroDivisionError:
				pass
			except IndexError:
				# If no data is returned do nothing and wait for the next update
				self.queryRunning=False
			except:
				raise

	def _caprate(self):
		if len(self.queryData) < 200:
			return [0,0]

		arrtimes=np.diff(self.queryData)/1000.		
		counts, bins = np.histogram(arrtimes, bins=100, density=True)
		
		try:
			popt, pcov = curve_fit(self._fitfunc, bins[:len(counts)], counts, p0=[1, np.mean(arrtimes)])
			perr=np.sqrt(np.diag(pcov))
		except:
			return [0,0]

		return self._roundcaprate([ 1/popt[1], 1/(popt[1]*math.sqrt(len(self.queryData))) ])
	
	def _roundcaprate(self, caprate):
		try:
			x,y=caprate

			sigx=int(min(0, math.log10(x)))

			if x<10:
				return [ round(x, sigx), round(y, sigx-1) ]
			else:
				return [ int(round(x, sigx)), int(round(y, sigx)) ]
		except:
			return [0,0]

	def _formatelapsedtime(self):
		oneMin=60
		oneSec=1

		etime=self.queryData[-1]/1000.
		if etime > self.elapsedTime:
			self.elapsedTime=etime

		if self.elapsedTime < oneMin:
			elaptime=str(round(self.elapsedTime, 2)) + " s"
		# elif self.elapsedTime > 60 and self.elapsedTime < 600:
		else:
			m=int(self.elapsedTime/oneMin)
			s=int(self.elapsedTime%oneMin)
			elaptime=str(m) + " min " + str(s) + " s"
		# else:
		# 	elaptime=str(round(self.elapsedTime/60., 1)) + " min"

		return elaptime
		
	def _fitfunc(self, t, a, tau):
		return a * np.exp(-t/tau)

	def OnAppIdle(self):
		if not self.queryRunning:
			self._updatequery()

if __name__ == '__main__':
	# dbfile=resource_path('eventMD-PEG29-Reference.sqlite')
	dbfile=resource_path('eventMD-tempMSA.sqlite')

	app = QtGui.QApplication(sys.argv)
	dmw = StatisticsWindow()
	dmw.openDBFile(dbfile)
	dmw.show()
	dmw.raise_()
	sys.exit(app.exec_())

