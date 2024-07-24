import pygtk

pygtk.require('2.0')

import gtk, pango, gobject

gobject.threads_init()
#gtk.threads_init()

#gtk.gdk.threads_init()

#from gtk import gdk
from gtk.gdk import Pixbuf

print gtk.pygtk_version 
print gtk.gtk_version

#gtk.rc_parse('./share/themes/OS-X-Yosemite-2.0/gtk-2.0/gtkrc')
#gtk.rc_parse('./share/themes/gtk-wimp-0.7.0-bin/Theme/gtk-2.0/gtkrc')
#gtk.rc_parse('./share/themes/Windows-10-3.1/gtk-2.0/gtkrc')
#gtk.rc_parse('./gtk-wimp-0.7.0-bin/Theme/gtk-2.0/gtkrc')
#gtk.rc_parse('./share/themes/Arc-Darkest/gtk-2.0/gtkrc')
#gtk.rc_parse('./share/themes/Adwaita-dark/gtk-2.0/gtkrc')
#gtk.rc_parse('./share/themes/Redmond/gtk-2.0/gtkrc')

import os, sys, sysconfig , threading, glob


from vtt_to_srt_2_update import * 

from pathlib2 import Path

sys.getfilesystemencoding = lambda: "utf-8"

from os.path import abspath, dirname, join

#from scandir import scandir

#WHERE_AM_I = abspath(dirname(__file__))

sys.setrecursionlimit(3500)

class MyWindow(gtk.Window):

	def __init__(self):

		gtk.Window.__init__(self,) 
		
		#self.set_icon_from_file('./icon.ico')

		#self.set_style()
	
		self.total_files = 0
		self.completed_files = 0
		self.failed_files = 0
		self.failed_files_path = []
		self.items = []
		self.status_bar_text = ""
		self.tree_store = gtk.TreeStore(Pixbuf, str, bool, bool, str)

		self.props.window_position = gtk.WIN_POS_CENTER
		self.props.title = 'VTT To SRT'
		#self.props.icon = gtk.gdk.pixbuf_new_from_file('./icon.ico')
		self.props.resizable = True
		self.connect('destroy', gtk.main_quit)
		
	
		#settings = gtk.settings_get_default()
		#settings.props.gtk_button_images =  True

		self.add_button = gtk.Button(label='Add', stock=gtk.STOCK_ADD)
		self.add_button.set_image_position(gtk.POS_LEFT)
		#image = gtk.Image()
		#pix = gtk.gdk.pixbuf_new_from_file('./icon2.ico')
		#image.set_from_pixbuf(pix)
		#image.set_from_file('./icon2.ico')
		#image.show()
		#self.add_button.set_image(image)

		self.add_button.connect("clicked", self.on_add_button_clicked)

		self.delete_button = gtk.Button(label="Delete" ) #, stock=gtk.STOCK_REMOVE)
		self.delete_button.connect('clicked', self.on_delete_button_clicked)

		self.convert_button = gtk.Button(label = "Convert", stock=gtk.STOCK_CONVERT)
		self.convert_button.connect('clicked', self.on_convert_button_clicked)

		self.test_button_1 = gtk.Button(label = 'Test 1')
		self.test_button_1.connect('clicked', self.enable_widgets)

		self.test_button_2 = gtk.Button(label = 'Test 2')
		self.test_button_2.connect('clicked', self.disable_widgets)

		self.files_frame = gtk.Frame(label = 'Files To Convert')
		
		scrolled_win = gtk.ScrolledWindow(None, None)
		#scrolled_win.set_policy(gtk.PolicyType.AUTOMATIC, gtk.PolicyType.AUTOMATIC)
		scrolled_win.add(self.tree_view_setup(self.tree_store))
		scrolled_win.set_size_request(450, 250)
		#scrolled_win.set_vexpand(True)
		#scrolled_win.set_hexpand(True)

		self.files_frame.add(scrolled_win)

		self.progressbar = gtk.ProgressBar()
		self.progressbar.set_text("progress bar")
		self.progressbar.set_show_text(True)
		self.progressbar.show()
		
		self.status_bar = gtk.Statusbar()
	
		self.init_status_bar()	
		self.init_menubar()

		grid = gtk.VBox()

		grid.pack_start(self.menubar, False, False)

		grid.pack_start(self.files_frame)

		self.spin = gtk.Spinner()
		self.spin.show()

		box = gtk.HBox(spacing=5, homogeneous=True)
		box.props.border_width = 5
		box.pack_start(self.add_button, False)
		box.pack_start(self.delete_button, False)
		box.pack_start(self.convert_button, False)
		box.pack_start(self.spin, False)
		box.pack_start(self.test_button_1, False)
		box.pack_start(self.test_button_2, False)
		grid.pack_start(box, False, False)
		grid.pack_start(self.status_bar, False, False)
		
		self.add(grid)

		self.pause_event = threading.Event()

	def init_menubar(self):

		self.menubar = gtk.MenuBar()
		
		self.file_menu_parent = gtk.MenuItem(label='File')
		filemenu = gtk.Menu()
		self.file_menu_parent.set_submenu(filemenu)
		self.menubar.append(self.file_menu_parent)

		add = gtk.MenuItem(label='Add')
		add.connect('activate', self.on_add_button_clicked)
		delete = gtk.MenuItem(label='Delete')
		delete.connect('activate', self.on_delete_button_clicked)
		convert = gtk.MenuItem(label='Convert')
		convert.connect('activate', self.on_convert_button_clicked)
		
		filemenu.append(add)
		filemenu.append(delete)
		filemenu.append(convert)

		help = gtk.MenuItem(label='Help')
		helpmenu = gtk.Menu()

		def about_dialog(widget=None):
			about = gtk.AboutDialog()
			about.set_title('AboutDialog')
			about.set_name('Vtt To Srt')
			#about.set_version('0.1')
			about.props.version = '0.2'
			about.set_comments('Small Programm to convert Vtt Files to Srt files.')
			about.set_website('https://google.com')
			about.set_authors(['karim reefat', 'hessuan mohammed'])
			logo = gtk.icon_theme_get_default().load_icon('folder', 16, 0)
			about.set_logo(logo)

			about.set_position(gtk.WIN_POS_CENTER_ALWAYS)
			#about.set_modal(True)
			#about.set_transient_for(self)

			about.connect('response', lambda dialog, response: dialog.destroy())
			about.run()
 
		about = gtk.MenuItem('About')
		about.connect('activate', about_dialog)
		helpmenu.append(about)
		help.set_submenu(helpmenu)
		
		self.menubar.append(help)

	def on_convert_button_clicked(self, widget):
		#self.traverse_treestore(self.tree_store.get_iter_first())
		
		self.num = 0
		self.speed = 0

		self.completed_files = 0
		self.failed_files = 0
		self.update_status_bar()

		self.ee = threading.Event()

		thread = threading.Thread(target=lambda: self.traverse_treestore(self.tree_store.get_iter_first()))

		thread.start()

		#self.disable_widgets()

		from time import time 
		start = time()

		def update():
			if float(self.num) / self.total_files < 1:
				self.ee.wait()
				self.progressbar.set_fraction(float(self.num) / self.total_files)
				#self.progressbar.pulse()
				self.update_status_bar()
				self.ee.clear()
				if thread.is_alive():
					return True
				else:
					return False
		
		gobject.idle_add(update)

		self.progressbar.set_fraction(0)
		self.update_status_bar()


	def traverse_treestore(self, treeiter):
		
		parent = self.tree_store.iter_parent(treeiter)
		
		while treeiter is not None:				
			
			if self.tree_store.iter_has_child(treeiter):

				self.tree_store[treeiter][2] = False
				print('d: - ', self.tree_store[treeiter][1])

				childiter = self.tree_store.iter_children(treeiter)
				self.traverse_treestore(childiter)
			else:
				#print('f: -- ', self.tree_store[treeiter][1])
				file = self.tree_store[treeiter][1]
				save_path = self.tree_store[treeiter][4]
				if self.tree_store[treeiter][2]:
					print(1)
					try:
						self.convert_vtt2srt(file, save_path)
						self.tree_store[treeiter][2] = False
						self.completed_files += 1	
					except:
						self.failed_files += 1
						self.failed_files_path.append(file)
						self.tree_store[treeiter][3] = True
						self.tree_store[parent][3] = True
				self.num += 1
				self.ee.set()
			#print('e: ---', self.tree_store[treeiter][1])
			treeiter = self.tree_store.iter_next(treeiter)
			

	def convert_vtt2srt(self, file, save_path=None):
	
		vtt_to_srt(file)	

	def enable_widgets(self, widget):
		# enable the disable widgets

		print 'enabled: ===', widget

		self.file_menu_parent.set_sensitive(True)
		self.add_button.set_sensitive(True)
		self.convert_button.set_sensitive(True)
		self.delete_button.set_sensitive(True)
		#self.tree.set_sentitive(True)
		#self.files_frame.set_sentitive(True)

	def disable_widgets(self):
		# disable some widgets until other operations end.

		#print 'disabled: ==' , widget
	
		self.file_menu_parent.set_sensitive(False)
		self.add_button.set_sensitive(False)
		self.convert_button.set_sensitive(False)
		self.delete_button.set_sensitive(False)
		#self.tree.set_sentitive(False)
		#self.files_frame.set_sentitive(False)
		
	def loop_over_child_iter(self, treeiter, callback, value=None):
		# This function take treeiter and iterate over all it's childrens and excute the call back on every treeiter child.

		while treeiter is not None:
			callback(treeiter, value)
			if self.tree_store.iter_has_child(treeiter):
				childiter = self.tree_store.iter_children(treeiter)
				self.loop_over_child_iter(childiter, callback, value)
			treeiter = self.tree_store.iter_next(treeiter)

	def remove_childs(self, iter, value=None):
		# remove value from self.items
			if not self.tree_store.iter_has_child(iter):
				self.items.remove(self.tree_store[iter][1])

	def on_delete_button_clicked(self, widget):
		# remove files or folders from the tree.
	
		selection = self.tree.get_selection()
		rows = selection.get_selected_rows()

		if rows:
			removed_iter_list = []
			for row in rows[1]:
				removed_iter_list.append(self.tree_store[row].iter)

			for iter in removed_iter_list:
				parent = self.tree_store.iter_parent(iter)
				item = self.tree_store[iter][1]

				if not self.tree_store.iter_has_child(iter):
					self.items.remove(item)
				else:
					iter_child = self.tree_store.iter_children(iter)
					self.loop_over_child_iter(iter_child, self.remove_childs)
				
				self.tree_store.remove(iter)
				
			# This part will remove parent directory if it's empty
			while parent:
				if not self.tree_store.iter_has_child(parent):
					up_parent = self.tree_store.iter_parent(parent)
					self.tree_store.remove(parent)
				else:
					break
				parent = up_parent
		else:
			print 'None'

		self.total_files = len(self.items)
		self.completed_files = 0
		self.failed_files = 0
		self.update_status_bar()
		self.progressbar.set_fraction(0)

	def init_status_bar(self):
        # initate status bar with label and progress bar.

		frame = self.status_bar.get_children()[0]
		box = frame.get_children()[0]

		self.status_bar_label = box.get_children()[0]
		self.status_bar_label.props.ellipsize = pango.ELLIPSIZE_NONE
		self.status_bar_label.set_justify(gtk.JUSTIFY_RIGHT)
		self.status_bar_label.set_selectable(True)
		self.status_bar_label.show()

		result = '''<span color='blue'>''' + \
					"Total: " + "<span color='red'>" + str(self.total_files) + "</span>" + " - " + \
                    "Completed: " + "<span color='red'>" + str(self.completed_files) + "</span>" + \
                    " - " + "Failed: " + "<span color='red'>" + str(self.failed_files) + "</span>" + \
                    '''</span>'''

		self.status_bar_label.set_markup(result)

		box.pack_start(self.progressbar, True, True, 0)
		self.progressbar.show()
		box.reorder_child(self.progressbar, 0)
		
		sep = gtk.VSeparator()
		sep.show()
		box.pack_start(sep, False, False, 20)
		box.reorder_child(sep, 1)
		
		print box.query_child_packing(self.status_bar_label)		
		box.set_child_packing(self.status_bar_label, False, False, 0, gtk.PACK_END)
		print box.query_child_packing(self.status_bar_label)		

		#self.status_bar.set_size_request(10, 10)
		#self.status_bar.pack_start(control_grid, True, True, 0)

	def update_status_bar(self):
		
		result = '''<span color='blue'>''' + \
					"Total: " + "<span color='red'>" + str(self.total_files) + "</span>" + " - " + \
					"Completed: " + "<span color='red'>" + str(self.completed_files) + "</span>" + \
					" - " + "Failed: " + "<span color='red'>" + str(self.failed_files) + "</span>" + \
				'''</span>'''
		self.status_bar_label.set_markup(result)

	def on_add_button_clicked(self, widget):	
		
		self.dialog = gtk.FileChooserDialog("Open..", self, gtk.FILE_CHOOSER_ACTION_OPEN ,
												(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
												gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		
		self.dialog.props.select_multiple = True
		self.dialog.set_current_folder('./')
		self.dialog.set_modal(True)
		self.dialog.set_transient_for(self)
		self.dialog.set_destroy_with_parent(True)
		#dialog.set_select_multiple(True)
		self.dialog.props.select_multiple = True
		
		filter = gtk.FileFilter()
		filter.set_name("All files")
		filter.add_pattern("*")
		self.dialog.add_filter(filter)

		self.select_button = gtk.Button(label='Select')
		self.select_button.show()
		self.dialog.add_action_widget(self.select_button, 1)

		loop_through_check_button = gtk.CheckButton(label='Loop Through')
		loop_through_check_button.show()

		action_area = self.dialog.get_action_area()
		action_area.pack_end(loop_through_check_button)

		response_id = self.dialog.run()
		
		print 'rrr', response_id
		 
		print "Add: --"
		
		#gtk.gdk.threads_enter()

		self.e = threading.Event()

		filenames = self.dialog.get_filenames()

		def add():
			for path in filenames:
				path = u"\\\\?\\" + path
				if os.path.isdir(path) and loop_through_check_button.get_active():
					self.add_dir(path, recursive= True)
				elif os.path.isdir(path):
					self.add_dir(path)
				elif os.path.isfile(path) and os.path.splitext(path)[1] == '.vtt' and \
					path not in self.items:
						self.items.append(path)
						#self.tree_store.append(None, (None, path, True, os.path.dirname(path), ))
						self.tree_store.append(None, (None, str(Path(path)), True, False, str(Path(path).parent), ))
						self.total_files += 1
	
		thread = threading.Thread(target=add)

		if response_id == 1:
			#gtk.gdk.threads_enter()
			self.add_button.set_label("Pause")
			thread.start()
		
		if response_id == 1 or response_id == -6:
			self.dialog.destroy()

		self.progressbar.set_fraction(0.1)
		self.a = 1

		def update():
			print 'a: ', self.a
			self.a += 1
			self.progressbar.pulse()
			self.update_status_bar()
			#self.e.wait()
			if thread.is_alive():
				#self.e.clear()
				return True
			else:
				#gtk.gdk.threads_leave()
				self.add_button.set_label("Add")
				print 'items count= :', len(self.items)	
				#self.e.clear()	
				return False
	
		gobject.idle_add(update)

		self.progressbar.set_fraction(0.01)
		#gtk.gdk.threads_leave()
		self.update_status_bar()
	
	def add_dir(self, dir_name, parent_iter=None, recursive=False):
		# the function used to add items to the treeStore model
		
		itemIcon = gtk.icon_theme_get_default().load_icon("folder", 16, 0)
		child_iter = self.tree_store.append(parent_iter, ( 
			itemIcon, str(Path(dir_name)), True, False, os.path.dirname(dir_name), ))

		if sysconfig.get_platform() == "mingw":
			sep = '\\'
		else:
			sep = os.sep		

		for entry in os.listdir(dir_name):
			#full_path = os.path.join(dir_name, entry)
			full_path = dir_name + sep + entry

			print 'f**' , len(full_path)
			#print full_path
			#print len(full_path)

			if os.path.isfile(full_path) and os.path.splitext(full_path)[1] == '.vtt' and \
					full_path not in self.items:
				self.items.append(full_path)
				self.tree_store.append(child_iter, (None, full_path, True, False, os.path.dirname(full_path), ))
				#self.tree_store.append(child_iter, (None, str(entry), True, False, str(entry.parent), ))
				self.total_files += 1
				#self.e.set()
			elif os.path.isdir(full_path) and recursive:
				#print full_path
				self.add_dir(full_path, child_iter, recursive=True)
		if not self.tree_store.iter_has_child(child_iter):
			self.tree_store.remove(child_iter)		

		#self.e.set()

		'''
		for entry in Path(dir_name).iterdir():
			if entry.is_file() and entry.suffix == '.vtt' and str(entry) not in self.items:
				self.items.append(str(entry))
				print entry
				self.tree_store.append(child_iter, (None, str(entry), True, str(entry.parent),))
				self.total_files += 1
				#self.e.set()
			elif entry.is_dir() and recursive:
				self.add_dir(str(entry), child_iter, recursive=True)
		if not self.tree_store.iter_has_child(child_iter):
				self.tree_store.remove(child_iter)
		'''

		'''
		dir_name =  dir_name + '*'
		print glob.glob(dir_name)		
		for entry in glob.glob(dir_name):
			#file_path = os.path.join(dir_name, entry)
			#file_path = dir_name + entry
				
			print entry
		'''

	def tree_view_setup(self, tree_model):
		# the function to add columns to the tree view 

		renderer_img = gtk.CellRendererPixbuf()
		renderer_text = gtk.CellRendererText()

		column_item = gtk.TreeViewColumn("File")
		column_item.pack_start(renderer_img, False)		
		column_item.add_attribute(renderer_img, "pixbuf", 0)
		column_item.pack_start(renderer_text, False)

		column_item.set_cell_data_func(renderer_text, lambda column, cell, model, iter, data=None:
			cell.set_property('text', Path(self.tree_store[iter][1]).name ) ) 

		column_item.add_attribute(renderer_text, "text", 1)
		column_item.props.resizable = True

		renderer_convert = gtk.CellRendererToggle()
		renderer_convert.connect('toggled', self.on_cell_toggled)

		column_convert = gtk.TreeViewColumn("Convert", renderer_convert, active=2)
		column_convert.props.resizable = True
	
		renderer_save_dir = gtk.CellRendererText()
		#renderer_save_dir.set_property("editable", True)
		#renderer_save_dir.connect("editing-started", self.on_save_dir_edit_started)
		
		column_save = gtk.TreeViewColumn("Save Dir", renderer_save_dir, text=3)
		column_save.props.resizable = True
		column_save.set_cell_data_func(renderer_save_dir, lambda column, cell, model, iter, data=None:
			cell.set_property('text', self.tree_store[iter][4].lstrip( "\\\\?\\" ) ) )

		self.tree = gtk.TreeView(model = tree_model) 
		#self.tree.props.activate_on_single_click = False
		self.selection = self.tree.get_selection()
		self.selection.set_mode(gtk.SELECTION_MULTIPLE)

		self.tree.connect("row-activated", self.on_row_activated)

		self.tree.append_column(column_item)
		self.tree.append_column(column_convert)
		self.tree.append_column(column_save)
		
		return self.tree

	def on_cell_toggled(self, widget, path):
		self.tree_store[path][2] = not self.tree_store[path][2]


	def on_save_dir_edit_started(self, renderer, cell, path):
		print(renderer)
		print(path)
		print(cell)

		treeiter = self.tree_store.get_iter(path)
		current_folder = self.tree_store.get_value(treeiter, 3)
		
		print(current_folder, self.tree_store.iter_has_child(treeiter))
		
		dialog = gtk.FileChooserDialog(title='Choose Save Directory', parent=self,
					action=gtk.FileChooserAction.SELECT_FOLDER)
		dialog.set_modal(True)
		dialog.set_transient_for(self)
		dialog.set_destroy_with_parent(True)
		dialog.set_current_folder(current_folder)

		self.select_dir_button = gtk.Button(label='Select')
		self.select_dir_button.show()
		dialog.add_action_widget(self.select_dir_button, 1)

		dialog.add_buttons(gtk.STOCK_CANCEL, gtk.ResponseType.CANCEL)
		
		dialog.connect('response', self.on_save_dir_dialog_response, treeiter, renderer, path, cell)
		dialog.run()


	def on_save_dir_dialog_response(self, dialog, response_id, treeiter, renderer, path, cell):
		# the function return from the calling the change dir files dialog.
		if response_id == 1:
			print(dialog.get_filename())
			self.tree_store[treeiter][3] = dialog.get_filename()
			
			# this part of code will add key press event to the tree view after change the save dir
			# in order to update the cell renderer text value directly after changing this value without
			# the need to press escape or click other palce on the tree view.
			
			event = Gdk.Event.new(Gdk.EventType.KEY_PRESS)
			#event.key.send_event = False
			#event.key.time = 0
			event.keyval = Gdk.KEY_Escape
			event.window = self.tree.get_window()
			event.put()
				
	
		if response_id == 1 or response_id == -4 or response_id == -6:
			dialog.destroy()


	def on_row_activated(self, widget, path, column):
		
		print(widget, path, column)
		print(self.tree_store[path][2])

		
	def set_style(self):
	
		provider = gtk.CssProvider()

		provider.load_from_path(join("./share/themes/Haiku/gtk-3.0/gtk.css"))

		screen = Gdk.Display.get_default_screen(Gdk.Display.get_default())

		#GTK_STYLE_PROVIDER_PRIORITY_APPLICATION = 600

		gtk.StyleContext.add_provider_for_screen(screen, provider,
			600) #GTK_STYLE_PROVIDER_PRIORITY_APPLICATION

"""
settings = gtk.Settings.get_default()
settings.set_property("gtk-theme-name", "Haiku")
settings.set_property("gtk-application-prefer-dark-theme", True)
"""

win = MyWindow()
#win.properties.title='VTT To SRT'

gtk.rc_reset_styles(gtk.settings_get_for_screen(win.get_screen()))

win.show_all()


#gtk.gdk.threads_enter()

gtk.main()

#gtk.gdk.threads_leave()
