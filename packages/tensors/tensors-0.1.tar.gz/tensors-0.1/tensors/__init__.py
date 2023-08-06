import beswitch
import sys


if "sphinx" in sys.modules:
    beswitch.select("none")
else:
    try:
        import tt
        beswitch.select("qtt")
    except ImportError:
        beswitch.select("none")
