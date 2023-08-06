class FIL:
    # hex, mat, md5, src (File based modules)
    def __init__(self, catalog, definitions, agent):
        # Use self.catalog and definitions
        self.catalog     = catalog
        self.definitions = definitions
        self.agent       = agent

    # Add any() function for lower Python version (< 2.4)
    try:
        any
    except NameError:
        def any(s):
            for v in s:
                if v:
                    return True
                return False

    def scan (self, fb, taskid):
        import os
        import fnmatch
        import re
        from datetime import datetime
        from base import bcolors, ProgressBar, get_domain, get_email, get_user, cal_md5_file

        analytics = {} # tmp fix

        # Analyse CMS systems and scan for viruses, trojans and hacks
        # self.definitions stored in rocksolid-self.definitions.txt
        results = {}
        nr_scanned = 0
        nr_userdir_found = {}
        nr_userdir_scanned = 0
        nr_found = 0
        pb_ctr = 0
        mat_patterns = ['*.php', '*.asp']
        openfilename = ''
        scanstart = datetime.now()
    
        fb.add(1, 'Scanning files started at ' + bcolors.OKBLUE + str(datetime.now()) + bcolors.ENDC)
    
        nr_userdirs = len(list(os.walk(str(self.catalog['param']['user_basedir'])).next()[1]))
        fb.add(1, 'Total number of userdirs to be scanned is ' + str(nr_userdirs))
    
        from time import gmtime, strftime
    
        pb = ProgressBar(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + ' [r-a] Scanning files', nr_userdirs)
        pb.setAndPlot(nr_userdir_scanned, "Pass " + bcolors.OKGREEN + str(0) + bcolors.ENDC + ", hits " + bcolors.WARNING + str(0) + bcolors.ENDC + "  (" + str(nr_userdir_scanned) + "/" + str(nr_userdirs) + ")")

        # Walk the folder
        #try:
        for root, dirs, files in os.walk(str(self.catalog['param']['user_basedir'])):
            # Determine base root for progress bar and userdir limit
            baseroot = root.replace(str(self.catalog['param']['user_basedir']) + "/", "")
            try:
                if userdir != baseroot.split("/")[0]:
                    nr_userdir_scanned += 1
                    userdir = baseroot.split("/")[0]
            except Exception, e:
                userdir = self.catalog['param']['user_basedir']

            for basename in files:
                filename  = os.path.join(root, basename)
                nr_scanned += 1

                # Update progress bar on each 1000 files
                dt = datetime.now() - scanstart;
                sec = ((dt.days * 24 * 60 * 60 + dt.seconds) * 1000 + dt.microseconds / 1000.0) / 1000.0
                #pb_ctr +=1
                if sec >= 1:
                    pb.setAndPlot(nr_userdir_scanned, "Pass " + bcolors.OKGREEN + str(nr_scanned) + bcolors.ENDC + ", hits " + bcolors.WARNING + str(nr_found) + bcolors.ENDC + "  (" + str(nr_userdir_scanned) + "/" + str(nr_userdirs) + ")")
                    #pb_ctr = 0
                    scanstart = datetime.now()

                if 'MAT' in self.catalog['tasks'][taskid]['apps'] and any(fnmatch.fnmatch(filename, p) for p in mat_patterns):
                    from libs import mat
                    matobj = mat.MAT()

                    # Do the MAT checks
                    # Calculate entropy to check for obfuscation
                    content = open(filename, 'rb').read(10240) # Read maximum of 10KB into memory
                    openfilename = filename

                    # Skip further processing on empty files
                    if len(content) == 0:
                        break

                    entropy = matobj.cal_entropy(content)
                    # Everything above 6 is to be considered an anolomy
                    if entropy > 6:
                        fb.add(1, 'Entropy value for file ' + filename + ' = ' + entropy)

                    # Check for long strings to check for encrypted code
                    longeststring = matobj.cal_longeststring(content)
                    if longeststring > 1000:
                        if not re.search('Zend', content, flags=re.DOTALL):
                            fb.add(1, 'Possible encrypted code in file '+ filename + ' = ' + longeststring)

                # Match against all self.definitions
                i = 0
                while i < len(self.definitions):
                    # SRC: Sourcecode recognition with version lookup
                    # HEX: Signature based filtering to identify harmful and infected files
                    # Load matching patterns
                    patterns = self.definitions[i]['file'].split("|")

                    if any(fnmatch.fnmatch(filename, p) for p in patterns):
                        if self.definitions[i]['type'] == 'SRC' and 'SRC' in self.catalog['tasks'][taskid]['apps']:
                            # Source code match, lookup version
                            # Read entire file into memory
                            content = open(filename, 'rb').read(512000) # Read maximum of 500KB into memory  << re-open because need larger sample
                            openfilename = filename

                            result = re.search(self.definitions[i]['regex'], content, flags=re.DOTALL)  # re.DOTALL = multiline search
                            if result:
                                # Call group only if we've got a hit to avoid crash and strip non-digits (aka: Magento notation)
                                cms_version = ".".join(re.findall(r'\d+', result.group(1)))

                            #print '[rocksolid-agent] Hit %s on file %s, detected %s version %s' % (nr_found, filename, self.definitions[i]['name'], cms_version)

                            # Count number of hits in this userdir
                            nr_userdir_found[userdir] = nr_userdir_found.get(userdir, 0) + 1

                            # Only store result for further processing if user limit is not reached yet
                            if nr_userdir_found[userdir] < self.catalog['param']['user_limit']:
                                nr_found += 1
                                user   = get_user(filename)
                                domain = get_domain(self.agent['namecp'], filename)
                                email  = get_email(self.agent['namecp'], user)
                                results[nr_found] = {'type': 'SRC', 'path': filename, 'name': self.definitions[i]['name'], 'version': cms_version, 'user': user, 'domain': domain, 'email': email, 'md5': cal_md5_file(filename), 'mtime': os.path.getmtime(filename), 'atime': os.path.getatime(filename), 'ctime': os.path.getctime(filename)}
                            #else:
                               # print '[rocksolid-agent] Skipping hit %s because userdir limit is reached' % filename


                        if self.definitions[i]['type'] == 'HEX' and 'HEX' in self.catalog['tasks'][taskid]['apps']:
                            # scan file for trojans and hacks
                            # compile regex (use in future release, might save resources
                            # sig  = re.compile(self.definitions[i]['regex'] , flags=re.IGNORECASE)
                            if filename != openfilename:
                                content = open(filename, 'rb').read(10240) # Read maximum of 10KB into memory
                                openfilename = filename

                            if re.search(self.definitions[i]['regex'], content, flags=re.DOTALL):  # re.DOTALL = multiline search
                                #print '[rocksolid-agent] Hit %s on file %s, detected %s' % (nr_found, filename, self.definitions[i]['name'])

                                # Count number of hits in this userdir
                                nr_userdir_found[userdir] = nr_userdir_found.get(userdir, 0) + 1

                                # Only store result for further processing if user limit is not reached yet
                                if nr_userdir_found[userdir] < self.catalog['param']['user_limit']:
                                    nr_found += 1
                                    user   = get_user(filename)
                                    domain = get_domain(self.agent['namecp'], filename)
                                    email  = get_email(self.agent['namecp'], user)
                                    results[nr_found] = {'type': 'SIG', 'path': filename, 'name': self.definitions[i]['name'], 'version': '', 'user': user, 'domain': domain, 'email': email, 'md5': cal_md5_file(filename), 'mtime': os.path.getmtime(filename), 'atime': os.path.getatime(filename), 'ctime': os.path.getctime(filename)}
                                #else:
                                   # print '[rocksolid-agent] Skipping hit %s because userdir limit is reached' % filename

                                #break # Don't scan file again using other signatures... mistake... can hit on multiple signatures

                    #next
                    i += 1

                # Handle runtime limits
                if (nr_found == self.catalog['param']['debug_limit']):
                    print "\n[rocksolid-agent] Debug limit of %s reached: returning results" % self.catalog['param']['debug_limit']
                    analytics['nrscanned'] = nr_scanned
                    analytics['nrfound']   = nr_found
                    return results
        #except Exception, e:
        #    print "File walker failed with error %s" % e
    
        # Set progressbar to 100% and destroy
        pb.setAndPlot(nr_userdirs, "Pass " + bcolors.OKGREEN + str(0) + bcolors.ENDC + ", hits " + bcolors.WARNING + str(0) + bcolors.ENDC  + "  (" + str(nr_userdirs) + "/" + str(nr_userdirs) + ")")
        del pb
    
        # Store analytical data
        analytics['nrscanned'] = nr_scanned
        analytics['nrfound']   = nr_found
    
        fb.add(1, 'Scanning files finished at ' + str(datetime.now()) + '(' + str(nr_scanned) + ' files scanned, ' + str(nr_found) + ' files found)')
    
        return results