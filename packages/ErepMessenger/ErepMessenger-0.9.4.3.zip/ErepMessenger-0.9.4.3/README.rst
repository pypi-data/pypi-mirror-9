Erepublik Messenger
===================

This application makes it possible to send mass in game messages for the online game Erepublik.

Installation
------------

Windows installer is now available! It has everything you need to get going including python!

Windows installer here: http://ereptools.tk/uploads/ErepMessenger_install.exe

First you should have Python 2.7 installed. You can get it `here`_

.. _here: https://www.python.org/download/releases/2.7.8/

Just download the installer for your operating system.

If you are on Mac OS X you will need to install `Tcl/Tk`_ also. Just download and install the recommended `Tcl/Tk`_ for your operating system.

.. _Tcl/Tk: http://www.python.org/download/mac/tcltk/

After Python(and Tcl/Tk on Mac OS X) is installed:

1. Download the latest ``ErepMessenger-x.x.tar.gz`` file
2. Extract all the files to anywhere you want with a file archive utility 

   * `7-Zip`_ (Windows)
   * `UnArchiver`_ (Mac)
   * `PeaZip`_ (Windows/Linux)

.. _7-Zip: http://www.7-zip.org/
.. _UnArchiver: http://unarchiver.c3.cx/unarchiver
.. _PeaZip: http://peazip.sourceforge.net/

3. Open up a command prompt/terminal (Windows: Included is a file called ``install.bat`` you can skip steps 3 - 5 by double clicking this file)

   * Windows: type in ``Command Prompt`` in the search box in the start menu then double click ``Command Prompt`` or ``Start->All Programs->Accessories->Command Prompt``

   * Mac OS X: open Finder then go to ``Applications->Utilities`` and find the Terminal application

   * Linux: press CTRL-ALT-T

4. Change directory to the folder you extracted (this folder will contain a file named ``setup.py``)

   * cd ``"the path to the folder"``

   * example: ``cd C:/erepmessenger-0.9``

5. Run the ``setup.py`` script from the command prompt/terminal

   * Windows: ``setup.py install`` if this does not work try ``python setup.py install``

   * Mac OS X and Linux: ``python setup.py install``

6. Now run the program!

   * Windows: Just double click ``messenger.pyw`` in the ``erepmessenger`` folder

   * Mac OS X and Linux: Open up the terminal to the path of ``messenger.pyw`` and enter ``python messenger.pyw``

Using the Messenger
-------------------

When you start up Erepublik Messenger you will see a simple GUI.
There is a menubar at the top with the options to "Start" and "Exit" and below that that you will see seperate text boxes for ID lists, your message subject, your message body, and there is a "Send" button.

To begin using the program press "File->Start".
You will be prompted for your Erepublik login information.

Once you are logged into Erepublik you can now fill out the Messenger form.
You may fill out the ID list with either line seperated or comma seperated lists.
Then enter your subject and message.
Keep in mind the message body is limited to 2000 characters!
An error will appear if you try to send a message longer than 2000 characters.

Also if you do not want to fill in your login information each time you use the app you can edit the file ``config.cfg`` with a text editor.
Don't use anything like Word.
Just use a basic text editor like notepad(Windows), gedit(Linux), or textedit(Mac OS X)..

Pro Tip
-------------
Put [name] in the message body and the messenger will automatically replace it with the citizens name.

Windows Users
-------------

You may create a shortcut to ``messenger.pyw`` for easy access to the program.

Included is a ``messenger.ico`` file to set as the shortcut's icon. To do this just right click the shortcut and select ``properties`` there you will see an option to change the icon.

Also if you need to be able to pin the short cut to the taskbar you will have to go to the shortcuts properties and edit the ``target`` of the shortcut to something like this::

    C:/python27/pythonw.exe C:/.../erepmessenger/messenger.pyw

You are just putting the path to ``pythonw.exe`` in front of the path to ``messenger.pyw`` separated by a single space.

 
Linux Users
-----------

To create a Launcher shortcut::

    [Desktop Entry]
    Name=Erepublik Messenger
    Comment=Run Erepublik Messenger
    Exec=python /home/YOUR/PATH/TO/messenger.pyw
    Icon=/home/YOUR/PATH/TO/messenger.gif
    Path=/home/YOUR/PATH/TO/
    Terminal=false
    Type=Application
    Categories=Utility;Application;
    
Paste that into a text editor and fill in your specific path to the files. Save as something like messenger.desktop. Make sure to make messenger.pyw and your messenger.desktop files executable.

Now you can drag the desktop file you just made to the launcher bar and are able to launch the messenger with one click!

Mac OS X Users
--------------

If any of these instructions are not correct please let me know how to fix it!

I have not done any testing on Mac OS X I obtained all this information from Google searches.
