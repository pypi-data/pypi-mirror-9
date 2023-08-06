class MOD:
    def __init__(self, catalog, definitions):
        from base import bcolors

        # Use catalog and definitions
        self.catalog     = catalog
        self.definitions = definitions
        self.bcolors     = bcolors

    def scan ( self, fb, results):
        import os
        import re

        # Find additional modules to CMS systems
        i = 0

        fb.add(1, 'Scanning modules')

        for hit,file in results.iteritems():
            j = 0
            while j < len(self.definitions):
                # MOD: Linked to SRC name, SRC can have multiple MOD defs... therefore while loop
                if self.definitions[j]['type'] == 'MOD' and self.definitions[j]['name'] == file['name']:
                    # Determine basedir of this module definition\
                    old,new,ext = self.definitions[j]['file'].split('|')
                    basedir  = file['path'].replace(old, new)

                    # List the modules folder
                    if len(basedir) > 0 and os.path.isdir(basedir):
                        fb.add(1, 'Checking for ' + file['name'] + ' plugins in ' + basedir)
                        # Create multi-dimensional dict
                        file['modules'] = {}

                        for basename in os.listdir(basedir):
                            if os.path.isdir(os.path.join(basedir, basename)):
                                # Do the magic
                                filename = basedir + basename + '/' + basename + ext
                                if os.path.exists(filename):
                                    content = open(filename, 'rb').read(512000)  # Read maximum of 500KB into memory
                                    result = re.search(self.definitions[j]['regex'], content, flags=re.DOTALL)  # re.DOTALL = multiline search
                                    if result:
                                        # Call group only if we've got a hit to avoid crash and strip non-digits (aka: Magento notation)
                                        module_version = ".".join(re.findall(r'\d+', result.group(1)))
                                    else:
                                        module_version = "unknown"

                                file['modules'][basename]   = module_version
                                i += 1

                j += 1

        fb.add(1, 'Gevonden modules : ' + str(i))

        return results