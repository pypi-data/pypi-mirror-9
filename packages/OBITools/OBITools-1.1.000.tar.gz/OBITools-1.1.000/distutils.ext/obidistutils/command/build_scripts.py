'''
Created on 20 oct. 2012

@author: coissac
'''

import os.path

from distutils.command.build_scripts import build_scripts as ori_build_scripts,\
    first_line_re
from distutils.util import convert_path
from distutils import log, sysconfig
from distutils.dep_util import newer
from stat import ST_MODE



class build_scripts(ori_build_scripts):
            
    def copy_scripts (self):
        """Copy each script listed in 'self.scripts'; if it's marked as a
        Python script in the Unix way (first line matches 'first_line_re',
        ie. starts with "\#!" and contains "python"), then adjust the first
        line to refer to the current Python interpreter as we copy.
        """        
        self.mkpath(self.build_dir)
        rawbuild_dir = os.path.join(os.path.dirname(self.build_dir),'raw_scripts')
        self.mkpath(rawbuild_dir)
        
        outfiles = []
        for script in self.scripts:
            adjust = 0
            script = convert_path(script)
            outfile = os.path.join(self.build_dir, os.path.splitext(os.path.basename(script))[0])
            rawoutfile = os.path.join(rawbuild_dir, os.path.basename(script))
            outfiles.append(outfile)

            if not self.force and not newer(script, outfile):
                log.debug("not copying %s (up-to-date)", script)
                continue

            # Always open the file but ignore failures in dry-run mode --
            # that way, we'll get accurate feedback if we can read the
            # script.
            try:
                f = open(script, "r")
            except IOError:
                if not self.dry_run:
                    raise
                f = None
            else:
                first_line = f.readline()
                if not first_line:
                    self.warn("%s is an empty file (skipping)" % script)
                    continue

                match = first_line_re.match(first_line)
                if match:
                    adjust = 1
                    post_interp = match.group(1) or ''
            
            log.info("Store the raw script %s -> %s", script,rawoutfile)        
            self.copy_file(script, rawoutfile)


            if adjust:
                log.info("copying and adjusting %s -> %s", script,
                         self.build_dir)
                if not self.dry_run:
                    outf = open(outfile, "w")
                    if not sysconfig.python_build:
                        outf.write("#!%s%s\n" %
                                   (self.executable,
                                    post_interp))
                    else:
                        outf.write("#!%s%s\n" %
                                   (os.path.join(
                            sysconfig.get_config_var("BINDIR"),
                           "python%s%s" % (sysconfig.get_config_var("VERSION"),
                                           sysconfig.get_config_var("EXE"))),
                                    post_interp))
                    outf.writelines(f.readlines())
                    outf.close()
                if f:
                    f.close()
            else:
                if f:
                    f.close()
                self.copy_file(script, outfile)

        if os.name == 'posix':
            for F in outfiles:
                if self.dry_run:
                    log.info("changing mode of %s", F)
                else:
                    oldmode = os.stat(F)[ST_MODE] & 07777
                    newmode = (oldmode | 0555) & 07777
                    if newmode != oldmode:
                        log.info("changing mode of %s from %o to %o",
                                 F, oldmode, newmode)
                        os.chmod(F, newmode)

