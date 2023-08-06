#!/usr/bin/env python

# Agent parameters
__version__     = '1.0.14'
__author__      = 'bjbuijs'
__author__      = 'aukeschotanus'

# Copyright rocksolid 2013,2014 (c) All rights reserved.
# created by Bart Jan Buijs & Auke Schotanus

# Available apps:
# HEX = HEX (regex) based signature check
# MAT = Mathematical checks to detect obfuscated and encrypted files
# MD5 = MD5 based signature check
# SRC = Sourcecode check
# MOD = Sourcecode module check (requires source check to be enabled)
# PAC = Packages check (supports rpm/yum (rpm -qa) and apt)
# PRT = Analyse open ports aka listening sockets and firewall rules
# CNF = Check system configuration files for possible weaknesses

# Initiate feedback to tty and logfile
from libs import base
fb = base.FeedBack()

if base.module_exists('datetime')    : from datetime import datetime
if base.module_exists('xml.dom')     : from xml.dom import minidom
if base.module_exists('os')          : import os
if base.module_exists('platform')    : import platform
if base.module_exists('urllib')      : import urllib
if base.module_exists('urllib2')     : import urllib2
if base.module_exists('re')          : import re
if base.module_exists('sys')         : import sys
if base.module_exists('signal')      : import signal
if base.module_exists('socket')      : import socket
if base.module_exists('subprocess')  : import subprocess
if base.module_exists('shelve')      : import shelve

# Initiate signal handlers
def signal_handler(signal, frame):
    from time import gmtime, strftime
    print('\n%s [r-a] Received termination request (you pressed ctrl+c)' % strftime("%Y-%m-%d %H:%M:%S", gmtime()))
    sys.exit()

# Check we're not using an old version of Python. Do this before anything else
# We need 2.4 above because some modules (like subprocess) were only introduced in 2.4.
if sys.version_info < (2,4):
    print 'You are using an outdated version of Python. Please update to v2.4 or above (v3 is not supported). For newer OSs, you can update Python without affecting your system install. See http://blog.boxedice.com/2010/01/19/updating-python-on-rhelcentos/ If you are running RHEl 4 / CentOS 4 then you will need to compile Python manually.'
    sys.exit(1)

def set_proc_name(newname):
    if base.module_exists('c_type') :
        from ctypes import cdll, byref, create_string_buffer

        libc = cdll.LoadLibrary('libc.so.6')
        buff = create_string_buffer(len(newname) + 1)
        buff.value = newname
        libc.prctl(15, byref(buff), 0, 0, 0)
    else :
        fb.add(1, 'Unable to set proc name. Module ctype missing. please install the module for optimal functionality.')


def get_proc_name():
    if base.module_exists('c_type') :
        from ctypes import cdll, byref, create_string_buffer

        libc = cdll.LoadLibrary('libc.so.6')
        buff = create_string_buffer(128)
        # 16 == PR_GET_NAME from <linux/prctl.h>
        libc.prctl(16, byref(buff), 0, 0, 0)
        return buff.value
    else :
        fb.add(1, 'Unable to set proc name. Module ctype missing, please install the module for optimal functionality')
        return 0


# returns the elapsed milliseconds since the start of the program
def detect_runtime():
    dt = datetime.now() - analytics['starttime']
    sec = ((dt.days * 24 * 60 * 60 + dt.seconds) * 1000 + dt.microseconds / 1000.0) / 1000.0
    return sec


def detect_os():
    return platform.system()


def detect_release():
    return platform.release()


def get_interface_ip():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('www.rocksolid.io', 80))
    ip = sock.getsockname()[0]
    sock.close()
    return ip


# Determine external ip address. Should be replaced by our own url that returns ip's.
def get_external_ip():
    site = urllib.urlopen("https://www.rocksolid.io/ip/").read()
    grab = re.findall('\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}', site)
    try:
        address = grab[0]
    except Exception, e:
        address = '0.0.0.0'

    return address


def get_default_user_basedir(cp):
    if  cp == 'cpanel':
        return '/home'
    elif cp == 'directadmin':
        return '/home'
    elif cp == 'ensim':
        return '/home'
    elif cp == 'plesk':
        return '/home/httpd/vhosts'
    elif cp == 'syncer':
        return '/var/www'
    else:
        # No control panel detected, scan entire disk
        return '/'

def detect_controlpanel():
    try:
        if   ( os.path.exists('/var/cpanel/users')):
            return 'cpanel'   # cpanel/WHM
        elif ( os.path.exists('/etc/virtual/domainowners')):
            return 'directadmin'
        elif ( os.path.exists('/home/virtual/FILESYSTEMTEMPLATE')):
            return 'ensim'
        elif ( os.path.exists('/etc/rc.d/init.d/epld')):
            return 'plesk'
        elif ( os.path.exists('/usr/local/syncer')):
            return 'syncer'
        else:
            return 'Unsupported'
    except OSError:
        # OS error
        pass


def detect_controlpanel_version(cp):
    version = 'Unknown'

    try:
        if   (cp == 'cpanel'):
            version = open('/usr/local/cpanel/version', 'r').read(512000)
        elif (cp == 'directadmin'):
            if base.module_exists('os'):
                version = os.popen('/usr/local/directadmin/directadmin v').read()
                version = version.split(' ')
                version = version[2].rsplit()
        elif (cp == 'ensim'):
            version = open('/usr/lib/opcenter/VERSION', 'r').read(512000)
        elif (cp == 'plesk'):
            version = open('/usr/local/psa/version', 'r').read(512000)
        elif (cp == 'syncer'):
            version = open('/usr/local/syncer/version', 'r').read(512000)
    except Exception, e:
        # Failed to lookup cp
        pass

    return version


def detect_php():
    phpv = ''

    try:
        # Use the newer subprocess.Popen as it is considered to be safer then os.popen
        cmd = subprocess.Popen(["php", "-v"], stdout=subprocess.PIPE)
        phpv, _ = cmd.communicate()
        phpv = phpv.split("\n")
        phpv = phpv[0]
    except Exception, e:
        # Failed to lookup cp
        pass

    return phpv


def get_agent_parameters():
    import sys
    agent = {}

    agent['customerkey']   = sys.argv[2]
    agent['version']       = __version__
    agent['hostname']      = platform.node()
    agent['interfaceip']   = get_interface_ip()
    agent['externalip']    = get_external_ip()
    agent['nameos']        = detect_os()
    agent['namecp']        = detect_controlpanel()
    agent['versionos']     = detect_release()
    agent['versioncp']     = detect_controlpanel_version(agent['namecp'])
    agent['versionpython'] = str(sys.version_info[0])+'.'+str(sys.version_info[1])+'.'+str(sys.version_info[2])
    agent['versionphp']    = detect_php()

    return agent


def load_definitions():
    # Load definitions into the agent
    definitions = {}
    nr = 0

    f = open(base.get_path() + '/rocksolid-agent.def')
    lines = f.readlines()
    f.close()

    for line in lines:
        # strip EOL
        line = line.rstrip()

        # put columns in array
        definition = line.split(":::", 3)

        # Use dictionary to store results (NEW)
        definitions[nr] = {'type':definition[0], 'name':definition[1], 'file':definition[2].decode("base64"), 'regex':definition[3]}
        nr = nr + 1

        # print '[rocksolid-agent] Loaded %s definition for %s (    %s    %s    )' % (definition[0], definition[1], definition[2].decode("base64"), definition[3])

    fb.add(1, 'Loaded definitions into memory')

    return definitions



def get_load_avg():
    if base.module_exists('os'):
        return str(os.getloadavg())
    else:
        return 'null'


def fetch_catalog( agent ):
    # Catalog contains instructions and parameters
    fb.add(1, 'Fetching catalog with customerkey ' + bcolors.OKBLUE + agent['customerkey'] + bcolors.ENDC + ', please wait....')

    # The catalog
    catalog = {}

     # Open the catalog stored @ disk
    try:
        dc = shelve.open(base.get_path() + "/rocksolid-agent.cat") # Create file when doesn't exists
        local_dc = 'yes'
    except Exception, e:
        fb.add(1, 'Unable to open/store local catalog')
        local_dc = 'no'

    # Prepare the data
    query_args = { 'task'        : 'fetchcatalog',
                   'customerkey' : agent['customerkey'] }

    # Query the rocksolid cloud
    try:
        data = urllib.urlencode(query_args)
        response = urllib.urlopen("https://www.rocksolid.io/agents/?%s" % data).read()
        fb.add(1, 'Received catalog. Extracting parameters and tasks')

    except Exception, e:
        fb.add(1, 'Unable to fetch catalog ... where did the cloud go? error: ' + str(e))
        sys.exit(1)

    # Process the XML
    try:
        xmldoc = minidom.parseString(response)
    except Exception, e:
        fb.add(1, 'Unable to load the catalog from cloud, using defaults .. error: ' + str(e))
        pass

    # Process parameters
    try:
        parameters = xmldoc.getElementsByTagName('parameters')

        catalog['param'] = {}

        for parameter in parameters[0].childNodes:
            try:
                key   = parameter.nodeName
                value = parameter.firstChild.data
                catalog['param'][key] = value
                fb.add(1, 'Using parameter ' + bcolors.OKBLUE + key + bcolors.ENDC + ' = ' + bcolors.OKBLUE + value + bcolors.ENDC)
            except:
                pass
    except:
        fb.add(1, 'No parameters defined, using defaults')

    # Set defaults
    try:
        parameters = catalog['param']
    except Exception, e:
        catalog['param'] = {}
        parameters = catalog['param']

    if 'user_basedir' not in parameters.items():
        # Detect default basedir if no basedir is set in the cloud
        user_basedir = get_default_user_basedir(agent['namecp'])
        fb.add(1, 'Userdir set to ' + bcolors.OKBLUE + user_basedir + bcolors.ENDC + ' based on control panel ' + bcolors.OKBLUE + agent['namecp'] + bcolors.ENDC + ' defaults. If wrong please change on www.rocksolid.io')
        catalog['param']['user_basedir'] = user_basedir
    if 'user_limit' not in parameters.items():
        catalog['param']['user_limit']   = str(10000)
    if 'debug_level' not in parameters.items():
        catalog['param']['debug_level']  = str(2)
    if 'debug_limit' not in parameters.items():
        catalog['param']['debug_limit']  = str(10000000)

    # Process tasks
    try:
        tasks = xmldoc.getElementsByTagName('task')
        fb.add(1, 'Catalog contains' + str(len(tasks)) + ' tasks')

        catalog['tasks'] = {}

        for task in tasks:
            try:
                id       = task.getAttribute("id")
                fb.add(1, 'Loading task ID #' + bcolors.OKBLUE + id + bcolors.ENDC)

                action   = task.getElementsByTagName('action')[0].firstChild.data
                interval = task.getElementsByTagName('interval')[0].firstChild.data

                fb.add(1, '#' + bcolors.OKBLUE + id + bcolors.ENDC + ' action = ' + bcolors.OKBLUE + action + bcolors.ENDC)
                fb.add(1, '#' + bcolors.OKBLUE + id + bcolors.ENDC + ' interval = ' + bcolors.OKBLUE + interval + bcolors.ENDC)

                catalog['tasks'][id]             = {}
                catalog['tasks'][id]['action']   = action
                catalog['tasks'][id]['interval'] = interval
                catalog['tasks'][id]['apps']     = []       # array within dict

                apps     = task.getElementsByTagName('apps')
                for app in apps[0].childNodes:
                    try:
                        catalog['tasks'][id]['apps'].append(app.firstChild.data)
                        fb.add(1, '#' + bcolors.OKBLUE + id + bcolors.ENDC + ' run app ' + app.firstChild.data + bcolors.ENDC)
                    except:
                        pass
            except Exception, e:
                fb.add(1, 'Failed loading task ID #' + task.getAttribute("id") + ' error: ' + str(e))

    except:
        fb.add(1, 'No tasks defined, adding default task SRC+MOD')
        catalog['tasks']                  = {}
        catalog['tasks']['1']             = {}
        catalog['tasks']['1']['action']   = 'new'
        catalog['tasks']['1']['interval'] = 'runonce'
        catalog['tasks']['1']['apps']     = []
        catalog['tasks']['1']['apps'].append('SRC')
        catalog['tasks']['1']['apps'].append('MOD')

    if local_dc == 'yes':
        # Store the catalog on disk
        dc['param'] = catalog['param']
        dc['tasks'] = catalog['tasks']

        # Close the catalog stored @ disk
        dc.close()

    return catalog


def dumpclean(obj):
    if type(obj) == dict:
        for k, v in obj.items():
            if hasattr(v, '__iter__'):
                print k
                dumpclean(v)
            else:
                print '%s : %s' % (k, v)
    elif type(obj) == list:
        for v in obj:
            if hasattr(v, '__iter__'):
                dumpclean(v)
            else:
                print v
    else:
        print obj


def run_tasks( catalog, definitions, agent ):
    fb.add(1, 'Running the tasks based on instructions and parameters in the catalog, please wait....')

    results = {}
    #dumpclean(catalog['tasks'])

    tasks = catalog['tasks']
    for k, v in tasks.items():
        fb.add(1, 'Processing task ID #' + bcolors.OKBLUE + str(k) + bcolors.ENDC)
        #print '%s : %s' % (k, v)

        apps = v['apps']

        # if execute now then
        for app in apps:
            try:
                fb.add(1, 'Running app ' + bcolors.OKBLUE + app + bcolors.ENDC + ' for task ID #' + bcolors.OKBLUE + k + bcolors.ENDC)
                if   app == 'HEX' or app == 'MAT' or app == 'MD5' or app == 'SRC':
                    # Initiate all the file based apps (combined in one run to open files only ones)
                    # hex, mat, md5, src
                    from libs import fil
                    filobj = fil.FIL(catalog, definitions, agent)
                    results['fil'] = filobj.scan(fb, k)
                elif app == 'MOD':
                    # mod (adds context)
                    from libs import mod
                    modobj = mod.MOD(catalog, definitions)
                    results['fil'] = modobj.scan(fb, results['fil'])
                elif app == 'PAC':
                    from libs import pac
                    pacobj = pac.PAC(catalog, definitions)
                    results['pac'] = pacobj.scan(fb)
                elif app == 'PRT':
                    from libs import prt
                    prtobj = prt.PRT(catalog, definitions)
                    results['prt'] = prtobj.scan(fb)
            except SystemExit:
                "Caught system signal when running apps"
                sys.exit()
            except Exception, e:
                "Failed to run app %s" % app

    fb.add(1, 'Finished apps, processing')

    return results


def upload_results(agent, results):
    xml  = "<rocksolid-agent>\n"
    xml += "   <agent>\n"
    for k, v in agent.items():
        xml += "      <%s>%s</%s>\n" % (k, v, k)
    xml += "      <missingpythonmodules>\n"
    i = 0
    while i < len(modules_missing):
        xml += "         <module>%s</module>\n" % modules_missing[i]
        i += 1
    xml += "      </missingpythonmodules>\n"
    xml += "   </agent>\n"

    # File based app (SRC,MOD)
    try:
        xml += "   <files>\n"

        # mtime = Last modified time aka creation date
        # atime = Last accessed time
        # ctime = Last changed time

        xmlTemplate = """         <path>%(path)s</path>
         <type>%(type)s</type>
         <name>%(name)s</name>
         <version>%(version)s</version>
         <user>%(user)s</user>
         <domain>%(domain)s</domain>
         <email>%(email)s</email>
         <md5>%(md5)s</md5>
         <mtime>%(mtime)s</mtime>
         <atime>%(atime)s</atime>
         <ctime>%(ctime)s</ctime>\n"""

        for hit, file in results['fil'].items():
            print '[rocksolid-agent] File %s %s' % (hit, file)
            xml += '      <file>\n'
            xml += xmlTemplate%file
            xml += '         <modules>\n'
            try:
                for k, v in file['modules'].items():
                    xml += '            <module>\n'
                    xml += '               <name>%s</name>\n' % k
                    xml += '               <version>%s</version>\n' % v
                    xml += '            </module>\n'
            except Exception, e:
                xml += ''
            xml += '         </modules>\n'
            xml += '      </file>\n'

        xml += "   </files>\n"
    except:
        pass

    # Packages app
    xml += "   <packages>\n"
    try:
        for package in results['pac']:
            xml += "      <package>%s</package>\n" % package
    except:
        pass

    xml += "   </packages>\n"
    xml += "   <analytics>\n"
    for k, v in analytics.items():
        xml += "      <%s>%s</%s>\n" % (k, v, k)
    xml += "   </analytics>\n"

    xml += "</rocksolid-agent>"

    #print 'XML output'
    #print xml

    # Communicate
    mydata   = [('xml',xml),('apikey',sys.argv[2])]  #The first is the var name the second is the value
    mydata   = urllib.urlencode(mydata)
    path     = 'https://www.rocksolid.io/report/'   #the url you want to POST to
    req      = urllib2.Request(path, mydata)
    req.add_header("Content-type", "application/x-www-form-urlencoded")

    try:
        response = urllib2.urlopen(req).read()
        fb.add(1, 'Uploaded data to rocksolid cloud. Processing....\n' + response)
    except urllib2.HTTPError, error:
        response = error.read()
        fb.add(1, 'Unable to upload data to rocksolid cloud.\n' + response)

    return 'finished'


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


def main():
    if base.module_exists('sys') and base.module_exists('signal'):
        #print "Registered signal handler"
        signal.signal(signal.SIGINT, signal_handler)

    # Set process name when running on Linux
    if detect_os() == 'Linux':
        set_proc_name('rocksolid-agent')

    # Set timing
    global analytics
    global modules_missing
    global packages
    modules_missing = []
    packages = []
    analytics = {}
    analytics['starttime'] = datetime.now()

    # Get the number of arguments passed
    argLen = len(sys.argv)

    if argLen > 1:
        if sys.argv[1] == 'run':
            # Require customerkey
            if argLen == 2:
                print "[r-a] Please provide your customer key: %s run [customerkey]" % sys.argv[0]
                sys.exit(1)

            # Store server load at start
            analytics['startload'] = get_load_avg()

            # Set agent parameters
            agent       = get_agent_parameters()

            fb.add(1, 'Starting security scan at '      + bcolors.OKBLUE + str(analytics['starttime']) + bcolors.ENDC)
            fb.add(1, 'System load upon start '         + bcolors.OKBLUE + str(analytics['startload']) + bcolors.ENDC)
            fb.add(1, 'Detected hostname '              + bcolors.OKBLUE + str(agent['hostname'])      + bcolors.ENDC)
            fb.add(1, 'Detected interface ip '          + bcolors.OKBLUE + str(agent['interfaceip'])   + bcolors.ENDC)
            fb.add(1, 'Detected external ip '           + bcolors.OKBLUE + str(agent['externalip'])    + bcolors.ENDC)
            fb.add(1, 'Detected operating system '      + bcolors.OKBLUE + str(agent['nameos']) + ',release '+ str(agent['versionos']) + bcolors.ENDC)
            fb.add(1, 'Detected control panel '         + bcolors.OKBLUE + str(agent['namecp'])        + bcolors.ENDC)
            fb.add(1, 'Detected control panel version ' + bcolors.OKBLUE + str(agent['versioncp'])     + bcolors.ENDC)
            fb.add(1, 'Detected python version '        + bcolors.OKBLUE + str(agent['versionpython']) + bcolors.ENDC)
            fb.add(1, 'Detected PHP version '           + bcolors.OKBLUE + str(agent['versionphp'])    + bcolors.ENDC)

            # Load definitions
            definitions = load_definitions()

            # Fetch catalog (instructions and parameters)
            catalog     = fetch_catalog(agent)                             # Pass customerkey

            # Run tasks based on catalog
            results     = run_tasks(catalog, definitions, agent)

            # Analytical data
            analytics['endtime'] = datetime.now()
            analytics['runtime'] = detect_runtime()
            analytics['endload'] = get_load_avg()
            modules_missing      = sorted(set(modules_missing))                  # !?!?!?? is this the right place?

            # Upload results
            upload_results(agent, results)

            # Output footer
            i = 0
            while i < len(modules_missing):
                fb.add(1, 'Module ' + modules_missing[i] + ' is missing. Please install for optimal usage of the agent')
                i += 1
            fb.add(1, 'Finished security scan at ' + str(analytics['endtime']) + '(in ' + str(analytics['runtime']) + ' seconds)')
            fb.add(1, 'System load upon finish = ' + str(analytics['endload']))

        elif sys.argv[1] == 'help':
            print '\n                           Welcome to rocksolid.\n'
            print '***********************************************************************************************\n'
            print 'To use this software agent, you can use the following commands:'
            print ' -run [customerkey]: run the agent; find the [customerkey] on http://www.rocksolid.io dashboard'
            print ' -help: this screen'
            print ' -update: check for updates of the agent and or signature file'
            print '\n***********************************************************************************************'

        elif sys.argv[1] == 'update':
            print 'Please update using # pip upgrade rocksolid-agent\n'
    else:
        print 'usage: %s run [customerkey]|help|update' % sys.argv[0]
        sys.exit(1)

# Start the proces
if __name__ == '__main__':
    main()
