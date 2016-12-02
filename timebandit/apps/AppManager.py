"""
executable functions for installed Apps
"""

def shell(flags):
    try:
        from timebandit import Application
        shell_app = Application
    except ImportError:
        print "this is getting weird"
    #while True:

