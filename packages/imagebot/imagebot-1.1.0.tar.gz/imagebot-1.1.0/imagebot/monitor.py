#!/usr/bin/python

from gi.repository import Gtk, GObject, GLib
from gi.repository.GdkPixbuf import Pixbuf, InterpType
from gi.repository import Gdk
import sys
import os
import glob
import shutil
from time import sleep
from threading import Thread, Event

from imagebot.settings import settings
from imagebot.dbmanager import DBManager


GObject.signal_new('change_image', Gtk.Window, GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (GObject.TYPE_STRING,))

class MyWindow(Gtk.Window):

	def __init__(self, jobname, outpipe, title='imagebot'):
		Gtk.Window.__init__(self, title=title)
		Gtk.Window.set_default_size(self, 800, 600)

		self.connect("key_press_event", self.on_key_pressed)
		self.connect("change_image", self.on_change_image)
		self.image = Gtk.Image()
		
		self.db = DBManager(settings.IMAGES_DB)
		self.db.connect()
		self.rowid = 0
		self.query = "SELECT max(rowid), path FROM images WHERE job = '%s'"%jobname

		self._outpipe = outpipe
		

	def on_key_pressed(self, event, data):
		(b, k) = data.get_keyval()
		key = Gdk.keyval_name(k)

		if key == "Right":
			self.next_image()
		elif key == "Left":
			self.prev_image()
		elif key == "d" or key == "D":
			self.delete_image()


	def on_change_image(self, event, data):
		pass


	def update_image(self):
		image_path = None
		if self._outpipe.poll():
			image_path = self._outpipe.recv()
			self.set_image(image_path)
		
		sleep(0.2)
		return True

	def set_image(self, filename, event=None):
		Gtk.Window.set_title(self, filename)
		self.remove(self.image)

		pb = Pixbuf.new_from_file(filename)

		iw = Pixbuf.get_width(pb)
		ih = Pixbuf.get_height(pb)
		ar = (float)(iw) / ih
		
		(w, h) = Gtk.Window.get_size(self)
		if (iw > ih):
			nw = w
			nh = (int)(nw / ar)
		else:
			nh = h
			nw = (int)(nh * ar)

		pb2 = Pixbuf.scale_simple(pb, nw, nh, InterpType.BILINEAR)

		self.image.set_from_pixbuf(pb2)
		self.add(self.image)

		self.image.show_all()


	def next_image(self):
		if (self.currentFile < len(self.jpgList) - 1):
			self.currentFile += 1
		self.set_image(self.jpgList[self.currentFile])


	def prev_image(self):
		if (self.currentFile > 0):
			self.currentFile -= 1
		self.set_image(self.jpgList[self.currentFile])


	def delete_image(self):
		print("trashing ", self.jpgList[self.currentFile], " to ", trashPath)
		shutil.move(self.jpgList[self.currentFile], trashPath)

	
	def set_sourcePath(self, sourcePath):
		os.chdir(sourcePath)
		self.jpgList = sorted(glob.glob('*.jpg'))
		self.currentFile = 0
		self.set_image(self.jpgList[0])

	def set_trashPath(self, trashPath):
		self.trashPath = trashPath


class Monitor():
	def __init__(self, jobname, outpipe):
		self._jobname = jobname
		self._outpipe = outpipe


	def start(self):
		win = MyWindow(self._jobname, self._outpipe)
		win.connect("delete-event", Gtk.main_quit)

		win.show_all()
		GLib.idle_add(win.update_image)
		Gtk.main()
		#print 'gtk ended..'


#== main program ===============>

if __name__ == '__main__':
	argc = len(sys.argv)
	if (argc < 2):
		print("missing jobname")
		quit()

	mon = Monitor(sys.argv[1])
	mon.start()

