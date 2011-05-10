# Usage example:
# 
#    $ wget http://arsip-dev.blankonlinux.or.id/blankon/pool/extras/liba/libass/libass_0.9.11-1.debian.tar.gz
#    $ tar xzf libass_0.9.11-1.debian.tar.gz
#    $ python blankon-branding.py debian/ pattimura
#
# Check:
#
#    $ head debian/changelog
#    $ head debian/control
#

import os
import tempfile
import sys
import shutil
import tarfile
from subprocess import Popen, PIPE
from datetime import datetime

from debian_bundle.deb822 import Packages
from debian_bundle.changelog import Changelog, ChangeBlock

AUTHOR = 'BlankOn Developers <blankon-dev@googlegroups.com>'
CHANGES = '''
  * BlankOn branding
'''

def get_date():
    p = Popen(['date', '-R'], stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    return out.strip()

dirname = sys.argv[1]
dist = sys.argv[2]

# Check directory
if os.path.isdir(os.path.join(dirname, 'debian')):
    dirname = os.path.join(dirname, 'debian')

if not os.path.isfile(os.path.join(dirname, 'changelog')):
    print 'File not found:', os.path.join(dirname, 'changelog')
    sys.exit(1)

if not os.path.isfile(os.path.join(dirname, 'control')):
    print 'File not found:', os.path.join(dirname, 'control')
    sys.exit(1)

# Modify Maintainer

fcontrol = os.path.join(dirname, 'control')
entries = []
for pkg in Packages.iter_paragraphs(open(fcontrol)):
    if 'Source' in pkg:
        if 'XSBC-Original-Maintainer' in pkg:
            pkg['XSBC-Original-Maintainer'] = '%s, %s' % \
                                              (pkg['Maintainer'],
                                               pkg['XSBC-Original-Maintainer'])
        else:
            pkg['XSBC-Original-Maintainer'] = pkg['Maintainer']
        pkg['Maintainer'] = 'BlankOn Developers <BlankOn-dev@googlegroups.com>'
    entries.append(pkg.dump())

control = '\n'.join(entries)
f = open(fcontrol, 'w')
f.write(control)
f.close()

# Add changelog

fchangelog = os.path.join(dirname, 'changelog')
changelog = Changelog(open(fchangelog))

version = changelog.version
if version.debian_version is None:
    version = '%s-0blankon1' % version.full_version
else:
    version = '%s+blankon1' % version.full_version

changes = ['%s\n' % line for line in CHANGES.rstrip().splitlines()] + \
          ['\n']

changelog.new_block(
    package=changelog.package,
    version=version,
    distributions=dist,
    urgency='low',
    changes=changes,
    author=AUTHOR,
    date='%s\n' % get_date(),
)

f = open(fchangelog, 'w')
f.write(str(changelog).replace('\n\n', '\n'))
f.close()

