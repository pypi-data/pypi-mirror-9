class PAC:
    def __init__(self, catalog, definitions):
        from base import bcolors

        # Use catalog and definitions
        self.catalog     = catalog
        self.definitions = definitions
        self.bcolors     = bcolors

    def scan (self, fb):
        import subprocess

        fb.add(1, 'Scanning packages')

        #out, err = subprocess.Popen(['/bin/rpm','-qa'], stdout=subprocess.PIPE).communicate()
        #packages = out.splitlines()

        cmd = subprocess.Popen(["/bin/rpm", "-qa"], stdout=subprocess.PIPE)
        packagesraw, _ = cmd.communicate()
        packagesraw = packagesraw.rstrip()
        packages = packagesraw.split("\n")

        return packages