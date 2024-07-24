import gi, os
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib
from gi.repository.GdkPixbuf import Pixbuf

import os, sys, html, threading

from os.path import abspath, dirname, join

from pathlib import Path
from webvtt import WebVTT
#from html2text import HTML2Text
from pysrt.srtitem import SubRipItem, SubRipTime

#WHERE_AM_I = abspath(dirname(__file__))

# by growing the recrusion limti to 1500 we will get bypassing the recurison error of reaching the 
# maximum recrusion depth while dealling the folders with big tree path.

sys.setrecursionlimit(3500)

class MyWindow(Gtk.Window):

	def __init__(self):

		Gtk.Window.__init__(self, title='VTT To SRT')

		#self.set_style()
	
		self.total_files = 0
		self.completed_files = 0
		self.failed_files = 0
		self.failed_files_path = []
		self.items = []
		self.status_bar_text = ""
		self.tree_store = Gtk.TreeStore(Pixbuf, str, bool, bool, str)		
		
		self.set_icon_from_file('./icon.ico')
		self.props.window_position = Gtk.WindowPosition.CENTER
		self.props.resizable = True
		self.connect('destroy', Gtk.main_quit)
		image = Gtk.Image.new_from_icon_name('airplane-mode-symbolic', 1)
		
		#image = Gtk.Image().new_from_stock(Gtk.STOCK_ADD, 3)
		
		self.add_button = Gtk.Button(label='Add', image=image, margin=5, halign=Gtk.Align.FILL, valign=Gtk.Align.FILL)
		self.add_button.props.always_show_image = True
		self.add_button.connect("clicked", self.on_add_button_clicked)

		self.delete_button = Gtk.Button(label="Delete", margin=5, halign=Gtk.Align.FILL, valign=Gtk.Align.FILL)
		self.delete_button.connect('clicked', self.on_delete_button_clicked)

		self.convert_button = Gtk.Button(label = "Convert", margin=5, halign=Gtk.Align.FILL, valign=Gtk.Align.FILL)
		self.convert_button.connect('clicked', self.on_convert_button_clicked)

		self.files_frame = Gtk.Frame(label = 'Files To Convert', margin=5, shadow_type=Gtk.ShadowType.ETCHED_OUT,
									valign=Gtk.Align.FILL, halign=Gtk.Align.FILL)

		scrolled_win = Gtk.ScrolledWindow.new(None, None)
		scrolled_win.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
		scrolled_win.add(self.tree_view_setup(self.tree_store))
		scrolled_win.set_size_request(450, 250)
		scrolled_win.set_vexpand(True)
		scrolled_win.set_hexpand(True)

		self.files_frame.add(scrolled_win)

		self.progressbar = Gtk.ProgressBar(margin=5)
		self.progressbar.set_text("this is progress bar")
		self.progressbar.set_show_text(True)
			
		#self.source_id = GLib.timeout_add(50, self.pulse)
				
		self.status_bar = Gtk.Statusbar()
		#self.status_bar.set_size_request(10, 10)

		self.status_bar_label = None

		self.init_status_bar()	
		
		self.init_menubar()
		
		grid = Gtk.Grid()
		
		grid.attach(self.menubar, 0, 0, 4, 1)

		grid.attach(self.files_frame, 0, 1, 4, 1)
		grid.attach(self.add_button, 0, 2, 1, 1)
		grid.attach(self.delete_button, 1, 2, 1, 1)
		grid.attach(self.convert_button, 2, 2, 1, 1)
		grid.attach(self.status_bar, 0, 3, 4, 1)
		
		self.add(grid)

	def init_menubar(self):
		# initation of the menubar items.

		self.menubar = Gtk.MenuBar.new()
		
		self.file_menu_parent = Gtk.MenuItem.new_with_label('File')
		filemenu = Gtk.Menu.new()
		self.file_menu_parent.set_submenu(filemenu)
		self.menubar.append(self.file_menu_parent)

		add = Gtk.MenuItem.new_with_label('Add')
		add.connect('activate', self.on_add_button_clicked)
		delete = Gtk.MenuItem.new_with_label('Delete')
		delete.connect('activate', self.on_delete_button_clicked)
		convert = Gtk.MenuItem.new_with_label('Convert')
		convert.connect('activate', self.on_convert_button_clicked)

		filemenu.append(add)
		filemenu.append(delete)
		filemenu.append(convert)
		#filemenu.append(file)

		help = Gtk.MenuItem.new_with_label('Help')
		helpmenu = Gtk.Menu.new()
		help.set_submenu(helpmenu)
		self.menubar.append(help)

		def about_dialog(self, widget=None):
			about = Gtk.AboutDialog()
			about.set_title('AboutDialog')
			about.set_name('Programmica')
			about.set_version('1.0')
			about.set_comments('Progreamming, system and network administration resources')
			#about.set_website("https://google.com/")
			about.set_website("https://github.com/amorvincitomnia/vtt-to-srt.py")
			about.set_website_label("google")
			about.set_authors(['ali essa', 'karim reefat'])
			logo = Gtk.IconTheme.get_default().load_icon("folder", 16, 0)
			about.set_logo(logo)

			def on_response(dialog, response):
				dialog.destroy()

			about.connect('response', on_response)
			about.run()
	
		about = Gtk.MenuItem.new_with_label('About')
		about.connect('activate', about_dialog)

		helpmenu.append(about)
	
	
	def on_convert_button_clicked(self, widget):
		# call traverse_treestore(new thread) > idle_add > timeout_add

		self.num = 0
		self.speed = 0

		self.completed_files = 0
		self.failed_files = 0
		self.update_status_bar()
	
		self.ee = threading.Event()	
		
		thread = threading.Thread(target=lambda: self.traverse_treestore(self.tree_store.get_iter_first()), daemon=True)
		thread.start()
	
		self.disable_widgets()
	
		from time import time		
		start = time()
		
		while thread.is_alive():
			self.speed += 1
			#print('speed', self.speed)
			if Gtk.events_pending():
				Gtk.main_iteration()
			if float(self.num) / self.total_files < 1:
				self.ee.wait()
				self.progressbar.set_fraction(float(self.num) / self.total_files)
				self.update_status_bar()
				self.ee.clear()
				continue
		
		end = time()				
		print('it took {end - start} seconds!')

		self.progressbar.set_fraction(0)
		self.update_status_bar()
		self.enable_widgets()

		def failed_log():
			'''
			dialog = Gtk.Dialog("Failed Files", self, 0,
				( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
					Gtk.STOCK_OK, Gtk.ResponseType.OK, 
				),
			)
            '''
			dialog = Gtk.Dialog(title="Failed Files", flags = 0)
			dialog.add_buttons( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
				Gtk.STOCK_OK, Gtk.ResponseType.OK) 
			
			dialog.set_default_size(150, 100)
			
			failed_file = ""

			for file_path in self.failed_files_path:
				failed_file += file_path + '\n'

			label = Gtk.Label(label = failed_file )
			
			box = dialog.get_content_area()
			box.add(label)
			dialog.show_all()
			response = dialog.run()

			if response == Gtk.ResponseType.OK:
				print("The OK button was clicked")
			elif response == Gtk.ResponseType.CANCEL:
				print("The Cancel Button was clicked")

			dialog.destroy()
	
		failed_log()
	
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
		# if the parent dir not exist it will create it then make the conversation from vtt to srt 
		print('f:--', file)
		if save_path:
			Path(save_path).mkdir(parents=True, exist_ok = True)
			print('stem:', Path(file).stem)
			print('save_path:', (Path(save_path) / Path(file).stem ))
			print('save_path2:', (Path(save_path) / Path(file).stem ).with_suffix('.srt'))

			new_item = (Path(save_path) / Path(file) ).with_suffix('.srt')
			print('nn:**', new_item)
		else:
			new_item = Path(file).with_suffix('.srt')
			print('n:--', new_item)

		try:
			with new_item.open(mode='w', encoding='utf-8') as srt:
				index = 0
				for caption in WebVTT().read(file):
					index += 1
					start = SubRipTime(0, 0, caption.start_in_seconds)
					end = SubRipTime(0, 0, caption.end_in_seconds)
					srt.write(SubRipItem(index, start, end, html.unescape(caption.text)).__str__()+"\n")
		except:
			print('--------')
			new_item.unlink()
			raise
	
	'''
	def traverse_treestore(self, treeiter ):
		# use the while loop instead of recursive function to loop through the tree store and convert 
		# all it's files from vtt to srt files.

		convert_value = False
		while treeiter is not None:
			if not self.tree_store.iter_has_child(treeiter):
				print(self.tree_store[treeiter][1], "--file")				
				file = self.tree_store[treeiter][1]
				save_path = self.tree_store[treeiter][4]
				if self.tree_store[treeiter][2]:
					try:
						self.convert_vtt2srt(file, save_path)
						self.tree_store[treeiter][2] = False
						self.completed_files += 1	
					except:
						self.tree_store[treeiter][2] = True
						convert_value = True
						self.failed_files += 1
				self.num += 1
				self.ee.set()
			else:
				print(self.tree_store[treeiter][1], "--folder")
				self.tree_store[treeiter][2] = False
				treeiter = self.tree_store.iter_children(treeiter)
				continue
				
			parent = self.tree_store.iter_parent(treeiter)	
			treeiter = self.tree_store.iter_next(treeiter)

			while treeiter is None :#or parent == self.tree_store.get_iter_first():
				print('-- back 1', self.tree_store[parent][1])
				if convert_value:
					self.tree_store[parent][2] = True
					print('****************')
					convert_value = False
				treeiter = self.tree_store.iter_next(parent)
				parent = self.tree_store.iter_parent(parent)
				
				if treeiter or not parent:
					#print('* -- break 1')
					break
	'''			
		
	def on_selection_changed(self, selection):
		# remove the childrens rows selection if we select it's parent 
		rows = selection.get_selected_rows()
		if rows:
			for row in rows[1]:
				iter = self.tree_store[row].iter
				if self.tree_store.iter_has_child(iter):
					iter_child = self.tree_store.iter_children(iter)
					self.loop_over_child_iter(iter_child, 
						lambda iter, value=None : self.selection.unselect_iter(iter))

	def enable_widgets(self):
		# enable the disabled widgets 

		self.file_menu_parent.set_sensitive(True)
		self.add_button.set_sensitive(True)
		self.convert_button.set_sensitive(True)
		self.delete_button.set_sensitive(True)
		#self.tree.set_sentitive(True)
		#self.files_frame.set_sentitive(True)

	def disable_widgets(self):
		# disable some widgets unitl other operations end.

		self.file_menu_parent.set_sensitive(False)
		self.add_button.set_sensitive(False)
		self.convert_button.set_sensitive(False)
		self.delete_button.set_sensitive(False)
		#self.tree.set_sentitive(False)
		#self.files_frame.set_sentitive(False)

	def remove_childs(self, iter, value=None):
		# remove value from self.items 
		if not self.tree_store.iter_has_child(iter): 
			self.items.remove(str(Path(self.tree_store[iter][1])))

	def on_delete_button_clicked(self, widget):
		# remove file or folder from the tree.
		selection = self.tree.get_selection()
		rows = selection.get_selected_rows()
		if rows:
			removed_iter_list = []
			for row in rows[1]:
				removed_iter_list.append(self.tree_store[row].iter)

			for iter in removed_iter_list:
				parent = self.tree_store.iter_parent(iter)
				# item = str(Path(self.tree_store[iter][4]) / Path(self.tree_store[iter][1]))
				item = str(Path(self.tree_store[iter][1]))

				if not self.tree_store.iter_has_child(iter):
					self.items.remove(item)
				else:
					iter_child = self.tree_store.iter_children(iter)
					self.loop_over_child_iter(iter_child, self.remove_childs)
				
				self.tree_store.remove(iter)			
			
				# this part will remove parent directory if it's empty
				while parent:
					if not self.tree_store.iter_has_child(parent):
						up_parent = self.tree_store.iter_parent(parent)
						self.tree_store.remove(parent)
					else:
						break
					parent = up_parent
		else:
			print('None')
		
		self.total_files = len(self.items)
		self.completed_files = 0
		self.failed_files = 0	
		self.update_status_bar()
		self.progressbar.set_fraction(0)
	
	def on_add_button_clicked(self, widget):
		# the call back of the add button clicked signal to add vtt files to the treeview 
		
		dialog = Gtk.FileChooserDialog(title="Please choose a folder", parent=self,
					action=Gtk.FileChooserAction.OPEN, use_header_bar=True)

		dialog.set_select_multiple(True)
		dialog.set_modal(True)
		dialog.set_transient_for(self)
		dialog.set_destroy_with_parent(True)
		
		dialog.set_current_folder('/home')
		dialog.set_filename('None')		

		filter_vtt = Gtk.FileFilter()
		filter_vtt.set_name("Vtt Files")
		filter_vtt.add_pattern("*.vtt")
		dialog.add_filter(filter_vtt)
		
		filter_any = Gtk.FileFilter()
		filter_any.set_name("Any Files")
		filter_any.add_pattern("*")
		dialog.add_filter(filter_any)
		
		self.select_button = Gtk.Button(label='Select')
		self.select_button.show()
		dialog.add_action_widget(self.select_button, 1)

		loop_through_check_button = Gtk.CheckButton(label='Loop Through')
		loop_through_check_button.show()
	
		header_bar = dialog.get_header_bar()
		header_bar.pack_end(loop_through_check_button)
	
		response_id = dialog.run()
		
		self.e = threading.Event()

		def add():
			for path in dialog.get_filenames():	
				if Path(path).is_dir() and loop_through_check_button.get_active() :
					self.add_dir(path, recursive=True)
				elif Path(path).is_dir():
					self.add_dir(path)	
				elif Path(path).is_file() and Path(path).suffix == '.vtt':
					if str(Path(path)) not in self.items:
						self.items.append(str(Path(path)))
						self.tree_store.append(None, (None, str(Path(path)), True, False, str(Path(path).parent), ))
						self.total_files += 1
						#self.update_status_bar()

		thread = threading.Thread(target=add, daemon=True)

		if response_id == 1:
			thread.start()
			self.disable_widgets()

		if response_id == 1 or response_id == -4:
			dialog.destroy()

			#	pulse the progressbar while there is adding files operation not finshed and update 
			#   the status bar data .
			speed = 0
			#print('cccccc')
		
			while thread.is_alive():
				self.e.wait()
				speed += 1
				if Gtk.events_pending():
					Gtk.main_iteration()
				self.progressbar.pulse()
				self.update_status_bar()
				#print('sssss' , speed)
				self.e.clear()
				continue
			#print('0000000')
			self.update_status_bar()		
			self.progressbar.set_fraction(0)
			self.enable_widgets()


	def add_dir(self, dir_name, parent_iter=None, recursive=False):
		# the function used to add items to the treeStore model
		print(len(dir_name), dir_name)	
		itemIcon = Gtk.IconTheme.get_default().load_icon("folder", 16, 0)
		child_iter = self.tree_store.append(parent_iter, ( 
			itemIcon, str(Path(dir_name)), True, False, str(Path(dir_name).parent), ))
		for entry in Path(dir_name).iterdir():
			if entry.is_file() and entry.suffix == '.vtt' and str(entry) not in self.items:
				self.items.append(str(entry))
				self.tree_store.append(child_iter, (None, str(entry), True, False, str(entry.parent), ))
				self.total_files += 1
				#print(self.total_files)
				self.e.set()
			elif entry.is_dir() and recursive:
				self.add_dir(str(entry), child_iter, recursive=True)
		if not self.tree_store.iter_has_child(child_iter) :
			self.tree_store.remove(child_iter)
		#print('22222')
		self.e.set()

	def loop_over_child_iter(self, treeiter, callback, value=None):
		# this function take treeiter and it iterate over all it's childrens.

		while treeiter is not None:
			callback(treeiter, value)
			if self.tree_store.iter_has_child(treeiter):
				childiter = self.tree_store.iter_children(treeiter)
				self.loop_over_child_iter(childiter, callback, value)
			treeiter = self.tree_store.iter_next(treeiter)
	
	
	def tree_view_setup(self, tree_model):
		# the function to add columns to the tree view 

		renderer_img = Gtk.CellRendererPixbuf()
		renderer_text = Gtk.CellRendererText()		

		#renderer_text.set_property('background', 'red')
	
		column_item = Gtk.TreeViewColumn("File")
		column_item.pack_start(renderer_img, False)		
		column_item.add_attribute(renderer_img, "pixbuf", 0)
		column_item.pack_start(renderer_text, False)

		# this will remove the file full path and keep it's name only for files not folders
		column_item.set_cell_data_func(renderer_text, lambda column, cell, model, iter, data: 
			cell.set_property('text', Path(self.tree_store[iter][1]).name ) )

		column_item.add_attribute(renderer_text, "text", 1)
		column_item.props.resizable = True
		
		renderer_convert = Gtk.CellRendererToggle()	

		#renderer_convert.set_property('inconsistent' , False)

		renderer_convert.connect('toggled', self.on_cell_toggled)

		column_convert = Gtk.TreeViewColumn("Convert", renderer_convert, active=2, inconsistent=3)
		column_convert.props.resizable = True

		renderer_save_dir = Gtk.CellRendererText()
		
		column_save = Gtk.TreeViewColumn("Save Dir", renderer_save_dir, text=4)
		column_save.props.resizable = True

		self.tree = Gtk.TreeView(model = tree_model, margin=10) 
		self.tree.props.activate_on_single_click = False

		self.selection = self.tree.get_selection()
		self.selection.set_mode(Gtk.SelectionMode.MULTIPLE)
		self.selection.connect('changed', self.on_selection_changed)

		self.tree.connect("row-activated", self.on_row_activated)
		self.tree.props.activate_on_single_click = False
		self.tree.append_column(column_item)
		self.tree.append_column(column_convert)
		self.tree.append_column(column_save)
		
		return self.tree

	def on_cell_toggled(self, widget, path):
		# the convert cell toggled callback function.
		
		treeiter = self.tree_store[path].iter
		
		# disable inconsistent property of the toggle cell renderer.	
		self.tree_store[treeiter][3] = False
		
		convert_value = self.tree_store[treeiter][2] = not self.tree_store[treeiter][2]

		if self.tree_store.iter_has_child(treeiter):		
			# take treeiter and reverse the the value of the convert cell of it.

			treeiter = self.tree_store.iter_children(treeiter)
			self.loop_over_child_iter(treeiter, 
				lambda treeiter, value=None: self.tree_store.set(treeiter, [2, 3], [convert_value, False]) )


	def on_row_activated(self, widget, path, column):
		# on double click the row change it's parent path.
		
		treeiter = self.tree_store[path].iter
		current_folder = self.tree_store[treeiter][4]
	
		dialog = Gtk.FileChooserDialog(title='Choose Save Directory', parent=self,
					action=Gtk.FileChooserAction.SELECT_FOLDER)
		dialog.set_modal(True)
		dialog.set_transient_for(self)
		dialog.set_destroy_with_parent(True)
		dialog.set_current_folder(current_folder)

		self.select_dir_button = Gtk.Button(label='Select')
		self.select_dir_button.show()
		dialog.add_action_widget(self.select_dir_button, 1)

		dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
		response_id = dialog.run()

		if response_id == 1:
			new_dir = self.tree_store[treeiter][4] = str(Path(dialog.get_filename()))
		
			if self.tree_store.iter_has_child(treeiter):		
				children_treeiter = self.tree_store.iter_children(treeiter)
				new = self.tree_store.append(None, [self.tree_store[treeiter][0], 
						self.tree_store[treeiter][1], self.tree_store[treeiter][2],self.tree_store[treeiter][3], 
						self.tree_store[treeiter][4]
						])
				self.tree_store_append_children(treeiter, new)
				self.loop_over_child_iter(new, self.change_childrens_save_dir, value=[current_folder, new_dir])
			else:
				self.tree_store.append(None, [ self.tree_store[treeiter][0], self.tree_store[treeiter][1],
												self.tree_store[treeiter][2], self.tree_store[treeiter][3], self.tree_store[treeiter][4] ])	
		
			parent = self.tree_store.iter_parent(treeiter)		

			self.tree_store.remove(treeiter)

			# this part will remove parent directory if it's empty
			while parent:
				if not self.tree_store.iter_has_child(parent):
					up_parent = self.tree_store.iter_parent(parent)
					self.tree_store.remove(parent)
				else:
					break
				parent = up_parent
						
		if response_id == 1 or response_id == -4 or response_id == -6:
			dialog.destroy()	
	
	def tree_store_append_children(self, treeiter, new):
		child = self.tree_store.iter_children(treeiter)
		while child is not None:
			parent = self.tree_store.append(new, [ self.tree_store[child][0], self.tree_store[child][1],
						self.tree_store[child][2], self.tree_store[child][3] , self.tree_store[child][4] ])
			if self.tree_store.iter_has_child(child):
				self.tree_store_append_children(child, parent)
			#self.tree_store.remove(child)
			child = self.tree_store.iter_next(child)
			
			
	def change_childrens_save_dir(self, treeiter, values):
		# take treeiter and change it's save path according to it's parent save path.
		
		#parent_name = os.path.basename(os.path.normpath(self.tree_store[parent_iter][1]))
		old_parent_dir = self.tree_store[treeiter][4]
		
		self.tree_store[treeiter][4] = self.tree_store[treeiter][4].replace(values[0], values[1])
		if self.tree_store[treeiter][4] == old_parent_dir:
			print(old_parent_dir, 'yes')
			

	def init_status_bar(self):
		# initate status bar with label and progress bar.
	
		frame = self.status_bar.get_children()[0]
		box = frame.get_children()[0]
		self.status_bar_label = box.get_children()[0]
		self.status_bar_label.show()
		 
		self.progressbar.show()
		box.pack_start(self.progressbar, True, True, 0)
		box.reorder_child(self.progressbar, 0)
	
		sep = Gtk.Separator
		sep = Gtk.Separator.new(Gtk.Orientation.VERTICAL)
		box.pack_start(sep, False, False, 0)
		box.reorder_child(sep, 1)

		result = '''<span color='blue'>''' + \
					"Total: " + "<span color='red'>" + str(self.total_files) + "</span>" + " - " + \
					"Completed: " + "<span color='red'>" + str(self.completed_files) + "</span>" + \
					" - " + "Failed: " + "<span color='red'>" + str(self.failed_files) + "</span>" + \
					'''</span>'''

		self.status_bar_label.set_markup(result)

	
	def update_status_bar(self):
		# update status bar data.

		result = '''<span color='blue'>''' + \
					"Total: " + "<span color='red'>" + str(self.total_files) + "</span>" + " - " + \
					"Completed: " + "<span color='red'>" + str(self.completed_files) + "</span>" + \
					" - " + "Failed: " + "<span color='red'>" + str(self.failed_files) + "</span>" + \
					'''</span>'''

		self.status_bar_label.set_markup(result)
	
	
	def set_style(self):
	
		provider = Gtk.CssProvider()

		provider.load_from_path(join("./share/themes/OS-X-Yosemite-2.0/gtk-3.20/gtk.css"))

		screen = Gdk.Display.get_default_screen(Gdk.Display.get_default())

		#GTK_STYLE_PROVIDER_PRIORITY_APPLICATION = 600

		Gtk.StyleContext.add_provider_for_screen(screen, provider,
			600) #GTK_STYLE_PROVIDER_PRIORITY_APPLICATION

	def set_themes(self):
		# set the the program themes from one of the themes in the directory ./share/themes/

		settings = Gtk.Settings.get_default()
		settings.set_property("gtk-theme-name", "Haiku")
		settings.set_property("gtk-application-prefer-dark-theme", True)

	def command_line_arguments(self, args):
		# handling files and directory if passed from the command linse insted of the gui.
		# adding -r before directory path will walk all directory after -r recursively .
		# adding -r after directory path will make only this directoy recusively .

		for arg in args:
			try:
				if Path(arg).is_dir():
					for entry in Path(arg).rglob('*.vtt'):
						try:
							self.convert_vtt2srt(entry)
						except BaseException as error:
							sys.stderr.write('Skipping: {} : {}\n'.format(entry, error))
				else:
					self.convert_vtt2srt(arg)
			except BaseException as error:
				sys.stderr.write('Skipping: {} : {}\n'.format(arg, error))
		

win = MyWindow()

if __name__ == '__main__':
	if len(sys.argv) == 1:
		win.show_all()
		Gtk.main()
	else:
		win.command_line_arguments(sys.argv[1:])
