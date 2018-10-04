
Silvius on Windows and Mac
===========================

Silvius uses the 'xdotool' utility to send keystrokes to the active
window in your X session. This tool is Linux only; while 'xdotool' is
available on Windows and OS X, the functionality is reduced compared
to 'xdotool' on Linux, and on OS X it requires XQuartz to be
running. On the other hand, each platform has native tools that
accomplish the same thing:

* On Windows, there's 'NirCmd' (http://www.nirsoft.net/utils/nircmd.html)

* On Mac, there's CLI-Click (https://www.bluem.net/en/projects/cliclick/)

A few modifications were made to Silvius (and the Automator class in
particular), because these tools have slightly different command-line
formats.

Additionally, NirCmd (Windows) uses the concept of virtual key codes
(https://docs.microsoft.com/en-us/windows/desktop/inputdev/virtual-key-codes)
which are translated into characters differently, depending on your
keyboard layout. This means that you may have to modify the virtual
key codes in NirCmdAutomator if you use a different keyboard
layout. (See the NirCmdAutomator class in automators.py)


Mac: Prepare your environment
-------------------------------

There are two prerequisites we'll need to install in order to be able
to install all necessary components:

* Homebrew (https://brew.sh)

    We'll use this package manager for mac to install a couple of
    components.

* PIP

   The package manager for python. Install it by running this command
   in the Terminal:

   ``sudo easyinstall pip``

Then, we install the components themselves:

``brew install portaudio``

``pip install pyaudio ws4py``

``brew install cliclick``


Windows: Prepare your environment
----------------------------------

On Windows, you'll need to install a few components as well:

* Python 2.7 for Windows (https://www.python.org/downloads/windows/)

* NirCmd (http://www.nirsoft.net/utils/nircmd.html)

Then, install the components:

``pip install pyaudio ws4py``


Install Silvius
================

Clone the git repository to get a local copy:

``git clone https://github.com/dwks/silvius.git``

Upon startup, Silvius will detect the OS it's running on, and select
the appropriate Automator.


Run Silvius
=============

``python stream/mic.py -s silvius-server.voxhub.io | python grammar/main.py``


