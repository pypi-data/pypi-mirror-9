import os

# Owners to use in testing...
VALID_OWNERS = ('Data Center',)

# Database stuff
DATABASE_ENGINE = 'sqlite3'

# The prefix is... ME! (Abs path to the current file)
PREFIX = os.path.dirname(os.path.abspath(__file__))

# .tacacsrc Stuff
DEFAULT_REALM = 'aol'
TACACSRC_KEYFILE = os.getenv('TACACSRC_KEYFILE', os.path.join(PREFIX, 'tackf'))
TACACSRC = os.getenv('TACACSRC', os.path.join(PREFIX, 'tacacsrc'))
RIGHT_TACACSRC = os.getenv('TACACSRC', os.path.join(PREFIX, 'right_tacacsrc'))
MEDIUMPW_TACACSRC = os.getenv('TACACSRC', os.path.join(PREFIX, 'mediumpw_tacacsrc'))
LONGPW_TACACSRC = os.getenv('TACACSRC', os.path.join(PREFIX, 'longpw_tacacsrc'))
BROKENPW_TACACSRC = os.getenv('TACACSRC', os.path.join(PREFIX, 'brokenpw_tacacsrc'))
EMPTYPW_TACACSRC = os.getenv('TACACSRC', os.path.join(PREFIX, 'emptypw_tacacsrc'))


# Configs
NETDEVICES_SOURCE = os.environ.get('NETDEVICES_SOURCE',
                                   os.path.join(PREFIX, 'netdevices.xml'))
AUTOACL_FILE = os.environ.get('AUTOACL_FILE',
                              os.path.join(PREFIX, 'autoacl.py'))
BOUNCE_FILE = os.environ.get('BOUNCE_FILE', os.path.join(PREFIX, 'bounce.py'))
