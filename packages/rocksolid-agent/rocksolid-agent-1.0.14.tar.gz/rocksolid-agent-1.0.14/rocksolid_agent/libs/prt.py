class PRT:
    def __init__(self, catalog, definitions):
        from base import bcolors

        # Use catalog and definitions
        self.catalog     = catalog
        self.definitions = definitions
        self.bcolors     = bcolors

    def scan (self, fb):
        import subprocess
        from base import module_exists

        fb.add(1, 'Probing ports')
        #ports = os.popen('/bin/netstat -ntulp | grep :::').read()
        #ports = ports.split()

        if module_exists('subprocess'):
            out, err = subprocess.Popen(['/bin/netstat','-ntlp'], stdout=subprocess.PIPE).communicate()
            lines = out.splitlines()

            i = 0
            while i < len(lines):
                try:
                    ports = lines[i].split()
                    fb.add(1, 'Found open port ' + ports[3] + ' (' + ports[0] + ' ' + ports[5] + ' ' + ports[6] + ')')
                except Exception, e:
                    pass
                i += 1
        results = []

        return results