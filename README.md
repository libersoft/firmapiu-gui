##Description
It provides a (I hope) easy-to-use interface, at the moment only the sign and verify action are working
It complies with Italian law on signing and verifying

Buttons:
Sign -> Sign one or more files using the smartcard
Sign folder -> Sign all documents inside a folder, doesn't recurse nor sign hidden files
Verify -> Verify one ore more files
Verify folder -> Verify all documents inside a folder, doesn't recurse nor verify  hidden files

Drag and drop area -> Sign the files dropped on or verify *one* .p7m file passed, if a folder is dropped, sign all the documents inside given folder

Log area -> Gives feedback on the action if it succeeds, if something goes wrong a dialog box is displayed


## How to build .deb package
In order to build the debian package you'll need:
* git
* debuild


`sudo apt-get install git debuild`


1. git clone https://github.com/libersoft/firmapiu-gui.git
2. cd firmapiu-packages
3. git checkout debian
4. cd debian
5. debuild -uc -us

Now you should have your .deb package located in the parent folder (..)

