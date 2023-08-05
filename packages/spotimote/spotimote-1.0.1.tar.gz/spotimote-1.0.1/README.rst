Spotimote
------------------------------------------------------------------------------

Python Spotify remote control using the Spotimote server

This library can control the Spotimote (http://www.nodria.com/) server using Python.
It can automatically detect the running Spotimote server and can be called like this:

    python spotimote.py play_pause
    python spotimote.py next
    python spotimote.py prev
    python spotimote.py shuffle
    python spotimote.py repeat
    python spotimote.py volume_up
    python spotimote.py volume_down

Or without autodetection of the host:

    python spotimote.py --host 192.168.0.2 --port 5116 volume_down

To use it as a library:

    # Setup the spotimote library
    from spotimote import Spotimote
    spotimote = Spotimote()
    
    # Play the next song
    spotimote.next()
    
    # Or scan for spotimote servers
    print 'Hosts:', list(spotimote.detect())
    
