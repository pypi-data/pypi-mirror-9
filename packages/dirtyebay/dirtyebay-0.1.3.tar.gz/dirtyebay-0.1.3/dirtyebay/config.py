import os
from ConfigParser import SafeConfigParser


CONFIG_PATH = os.environ.get('DIRTYEBAY_CONFIG_PATH',
                             os.path.abspath('ebay.conf'))
SANDBOX_CONFIG_PATH = os.environ.get('DIRTYEBAY_SANDBOX_CONFIG_PATH',
                                     os.path.abspath('ebay.sandbox.conf'))

production_config = SafeConfigParser()
production_config.read(CONFIG_PATH)

sandbox_config = SafeConfigParser()
sandbox_config.read(SANDBOX_CONFIG_PATH)
