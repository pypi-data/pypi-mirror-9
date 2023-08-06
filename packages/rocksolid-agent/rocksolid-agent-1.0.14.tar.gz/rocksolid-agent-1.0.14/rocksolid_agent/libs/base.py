# Base classes

class FeedBack:
    def __init__(self):
        self.logfile = open('/var/log/rocksolid-agent.log', 'w')

    def add(self, debug_level, data):
        from time import gmtime, strftime
        if debug_level > 0:
            output = strftime("%Y-%m-%d %H:%M:%S", gmtime()) + ' [r-a] ' + data

            # Write to log
            self.logfile.write(output + '\n')

            # Write to tty
            print output

    def __del__(self):
        self.logfile.close()


class ProgressBar:
    DEFAULT_BAR_LENGTH = float(45)

    def __init__(self, desc, end, start=0):
        import time
        import os
        self.desc   = desc
        self.end    = end
        self.start  = start
        self._barLength = ProgressBar.DEFAULT_BAR_LENGTH
        self.ts     = int(time.time())
        self.eta    = "..:.."
        self.info   = ""
        self.curper = 0

        self.setLevel(self.start)
        self._plotted = False
        os.system('setterm -cursor off')

    def setLevel(self, level, initial=False):
        self._level = level
        if level < self.start:  self._level = self.start
        if level > self.end:    self._level = self.end

        self._ratio = float(self._level - self.start) / float(self.end - self.start)
        self._levelChars = int(self._ratio * self._barLength)

    def plotProgress(self):
        import time
        import sys

        # Start calculating > 3%
        if int(self._ratio * 100.0) > 3:
            self.sectoeta = ((int(time.time()) - self.ts) / int(self._ratio * 100.0) * 100) - (int(time.time()) - self.ts)   # Calculate total time - minus elapsed time
            self.eta      = time.strftime("%M:%S", time.gmtime(self.sectoeta))

        if int(self._ratio * 100.0) == 100:
            self.eta      = "00:00"

        # Print bar
        sys.stdout.write("\r%s %3i%% [%s%s%s%s]   ETA %s   %s" %(
            self.desc,
            int(self._ratio * 100.0),
            bcolors.OKBLUE,
            '=' * int(self._levelChars),
            ' ' * int(self._barLength - self._levelChars),
            bcolors.ENDC,
            self.eta,
            self.info,
        ))
        sys.stdout.flush()
        self._plotted = True

    def setAndPlot(self, level, info):
        oldChars = self._levelChars
        self.setLevel(level)
        self.info = info
        #if (not self._plotted) or (oldChars != self._levelChars):
        self.plotProgress()

    def __del__(self):
        import os
        import sys

        os.system('setterm -cursor on')
        sys.stdout.write("\n")
        sys.stdout.flush()


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


def module_exists(module_name):
    try:
        __import__(module_name)
    except ImportError:
        # print '[rocksolid-agent] Python module %s missing. Please install ... trying to continue without this module.' % module_name
        # modules_missing.append(module_name)
        return False
    else:
        return True


def get_path():
    import os
    dirname, filename = os.path.split(os.path.abspath(__file__))

    return dirname[:-5]


# Base modules

def cal_md5_file(targetfile):
    # Hashlib introduced in 2.5, md5 module deprecated
    # Try Hashlib, fall back on md5 module if hashlib is missing
    from base import module_exists

    try:
        if module_exists('hashlib'):
            import hashlib
            checksum = hashlib.md5(open(targetfile, 'rb').read(512000)).hexdigest()
        elif module_exists('md5'):
            import md5
            m = md5.new()
            m.update(open(targetfile, 'rb').read(512000))
            checksum = m.hexdigest()
        else:
            return 0
    except Exception, e:
        return 0

    return checksum


def get_user(targetfile):
    user = targetfile.split('/')
    return user[2]


def get_domain(cp, targetfile):
    domain = ''
    try:
        import re
        import os

        tmpvar = targetfile.split('/')
        user = tmpvar[2]

        if   (cp == 'cpanel'):
            # Lookup in user config file
            lines = open('/var/cpanel/users/%s' % user[2], 'r').read(512000)
            result = re.search('DNS=(.*?)', lines)
            if result:
                domain = result.group(1)
        elif (cp == 'directadmin'):
            # Lookup in domainowners file
            lines = open('/etc/virtual/domainowners', 'r').read(512000)
            result = re.search('(.*?) :%s' % user, lines)
            if result:
                domain = result.group(1)
            else:
                # Fall back on pathname
                domain = tmpvar[4]
        elif (cp == 'ensim'):
            if module_exists('os'):
                domain = os.popen('/usr/bin/sitelookup -s %s 2>&1' % user[2]).read()
                domain = domain.split(',')
                domain = domain[0]
        elif (cp == 'plesk'):
            # Domain is part of the directory
            domain = user[4]
        elif (cp == 'syncer'):
            # Lookup in Apache vhost file
            lines = open('/usr/local/syncer/vhost.conf', 'r').read(512000)
            result = re.search('ServerName (.*?)\n.*?/var/www/%s' % user, lines)
            if result:
                domain = result.group(1)
    except Exception, e:
        # Failed to lookup domain
        pass

    return domain



def get_email(cp, user):
    email = ''
    try:
        import re
        if   (cp == 'cpanel'):
            # Lookup in user config file
            lines = open('/var/cpanel/users/%s' % user[2], 'r').read(512000)
            result = re.search('CONTACTEMAIL=(.*?)', lines)
            if result:
                email = result.group(1)
        elif (cp == 'directadmin'):
            # Lookup in domainowners file
            conf = '/usr/local/directadmin/data/users/' + user + '/user.conf'
            lines = open(conf, 'r').read(512000)
            result = re.search('email=(.*?)\n', lines)
            if result:
                email = result.group(1)
    except Exception, e:
        # Failed to lookup domain
        pass

    return email