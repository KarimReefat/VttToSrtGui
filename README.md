using the work of jsonzilla in https://github.com/jsonzilla/vtt_to_srt2 , https://github.com/jsonzilla/vtt_to_srt3 repository i make this gtk gui for the the the script to convert vtt into srt files.

i use gtk 2 and Gtk 3 to build this gui 

to run this gui from msys on windows use :

./gui3

for Gtk 3 and python 3

./gui2

for Gtk 2 and python 2

=======================

For Develpment for python 3: 

to setup virtual enviroment:
	python -m venv --system-site-packages ./vir3
	source ./vir3/bin/activate
	
pip install pyinstaller

to use pyinstaller use build_gui file.

if you use it in windows using gvsbuild:

you can download a zip file from the https://github.com/wingtk/gvsbuild/releases/latest and unzip it to C:\gtk.

then use the gvsbuild generated wheels in virtualenv 

pip install --force-reinstall (Resolve-Path C:\gtk\wheels\PyGObject*.whl)
pip install --force-reinstall (Resolve-Path C:\gtk\wheels\pycairo*.whl)

=======================

For development for python 2: 

to stup virtual envirotment for python 2:
	C:\Python27\Scripts\pip2 install virtualenv 
	virtualenv --system-site-packages vir2
	D:\new\Projects\subtest\Repos\VttToSrtGui\vir2\Scripts\activate

pip2 install pathlib2 PyInstaller==3.6

to use pyinstaller use build_gui2 file.

after build using pyinstaller copy "lib", "share" folders from /development_files/gtk_2_files_windows/windows to /dist/gui2 folder 
