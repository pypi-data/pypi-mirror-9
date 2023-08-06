#   Copyright 2009-2015 Oli Schacher
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
from fuglu.shared import ScannerPlugin, Suspect, DELETE, DUNNO, string_to_actioncode, actioncode_to_string
from fuglu.bounce import Bounce
import fuglu.extensions.sql
import time
import re
import mimetypes
import os
import os.path
import logging
from fuglu.extensions.sql import DBFile
import threading

from threading import Lock
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO
import zipfile

MAGIC_AVAILABLE = 0
MAGIC_PYTHON_FILE = 1
MAGIC_PYTHON_MAGIC = 2

try:
    import magic
    # python-file or python-magic? python-magic does not have an open attribute
    if hasattr(magic, 'open'):
        MAGIC_AVAILABLE = MAGIC_PYTHON_FILE
    else:
        MAGIC_AVAILABLE = MAGIC_PYTHON_MAGIC

except ImportError:
    pass


FUATT_NAMESCONFENDING = "-filenames.conf"
FUATT_CTYPESCONFENDING = "-filetypes.conf"
FUATT_ARCHIVENAMESCONFENDING = "-archivenames.conf"
FUATT_ARCHIVECTYPESCONFENDING = "-archivefiletypes.conf"

FUATT_DEFAULT = u'default'

FUATT_ACTION_ALLOW = u'allow'
FUATT_ACTION_DENY = u'deny'
FUATT_ACTION_DELETE = u'delete'

FUATT_CHECKTYPE_FN = u'filename'
FUATT_CHECKTYPE_CT = u'contenttype'

FUATT_CHECKTYPE_ARCHIVE_FN = u'archive-filename'
FUATT_CHECKTYPE_ARCHIVE_CT = u'archive-contenttype'

ATTACHMENT_DUNNO = 0
ATTACHMENT_BLOCK = 1
ATTACHMENT_OK = 2
ATTACHMENT_SILENTDELETE = 3

KEY_NAME = u"name"
KEY_CTYPE = u"ctype"
KEY_ARCHIVENAME = u"archive-name"
KEY_ARCHIVECTYPE = u"archive-ctype"

threadLocal = threading.local()


class RulesCache(object):

    """caches rule files"""

    __shared_state = {}

    def __init__(self, rulesdir):
        self.__dict__ = self.__shared_state
        if not hasattr(self, 'rules'):
            self.rules = {}
        if not hasattr(self, 'lock'):
            self.lock = Lock()
        if not hasattr(self, 'logger'):
            self.logger = logging.getLogger(
                'fuglu.plugin.FiletypePlugin.RulesCache')
        if not hasattr(self, 'lastreload'):
            self.lastreload = 0
        self.rulesdir = rulesdir
        self.reloadifnecessary()

    def getRules(self, ruletype, key):
        self.logger.debug('Rule cache request: [%s] [%s]' % (ruletype, key))
        if not self.rules.has_key(ruletype):
            self.logger.error('Invalid rule type requested: %s' % ruletype)
            return None
        if not self.rules[ruletype].has_key(key):
            self.logger.debug(
                'Ruleset not found : [%s] [%s]' % (ruletype, key))
            return None
        self.logger.debug('Ruleset found : [%s] [%s] ' % (ruletype, key))

        ret = self.rules[ruletype][key]
        return ret

    def getCTYPERules(self, key):
        return self.getRules(KEY_CTYPE, key)

    def getARCHIVECTYPERules(self, key):
        return self.getRules(KEY_ARCHIVECTYPE, key)

    def getNAMERules(self, key):
        return self.getRules(KEY_NAME, key)

    def getARCHIVENAMERules(self, key):
        return self.getRules(KEY_ARCHIVENAME, key)

    def reloadifnecessary(self):
        """reload rules if file changed"""
        if not self.rulesdirchanged():
            return
        if not self.lock.acquire():
            return
        try:
            self._loadrules()
        finally:
            self.lock.release()

    def rulesdirchanged(self):
        statinfo = os.stat(self.rulesdir)
        ctime = statinfo.st_ctime
        if ctime > self.lastreload:
            return True
        return False

    def _loadrules(self):
        """effectively loads the rules, do not call directly, only through reloadifnecessary"""
        self.logger.debug('Reloading attachment rules...')

        # set last timestamp
        statinfo = os.stat(self.rulesdir)
        ctime = statinfo.st_ctime
        self.lastreload = ctime

        filelist = os.listdir(self.rulesdir)

        newruleset = {KEY_NAME: {}, KEY_CTYPE: {},
                      KEY_ARCHIVENAME: {}, KEY_ARCHIVECTYPE: {}}

        rulecounter = 0
        okfilecounter = 0
        ignoredfilecounter = 0

        for filename in filelist:
            endingok = False
            for ending in (FUATT_NAMESCONFENDING, FUATT_CTYPESCONFENDING, FUATT_ARCHIVENAMESCONFENDING, FUATT_ARCHIVECTYPESCONFENDING):
                if filename.endswith(ending):
                    endingok = True
                    break

            if endingok:
                okfilecounter += 1
            else:
                ignoredfilecounter += 1
                self.logger.debug('Ignoring file %s' % filename)
                continue

            ruleset = self._loadonefile("%s/%s" % (self.rulesdir, filename))
            if ruleset == None:
                continue
            rulesloaded = len(ruleset)
            self.logger.debug('%s rules loaded from file %s' %
                              (rulesloaded, filename))
            ruletype = KEY_NAME
            key = filename[0:-len(FUATT_NAMESCONFENDING)]
            if(filename.endswith(FUATT_CTYPESCONFENDING)):
                ruletype = KEY_CTYPE
                key = filename[0:-len(FUATT_CTYPESCONFENDING)]
            elif(filename.endswith(FUATT_ARCHIVENAMESCONFENDING)):
                ruletype = KEY_ARCHIVENAME
                key = filename[0:-len(FUATT_ARCHIVENAMESCONFENDING)]
            elif(filename.endswith(FUATT_ARCHIVECTYPESCONFENDING)):
                ruletype = KEY_ARCHIVECTYPE
                key = filename[0:-len(FUATT_ARCHIVECTYPESCONFENDING)]

            newruleset[ruletype][key] = ruleset
            self.logger.debug('Updating cache: [%s][%s]' % (ruletype, key))
            rulecounter += rulesloaded

        self.rules = newruleset
        self.logger.info('Loaded %s rules from %s files in %s (%s files ignored)' %
                         (rulecounter, okfilecounter,  self.rulesdir, ignoredfilecounter))

    def _loadonefile(self, filename):
        """returns all rules in a file"""
        if not os.path.exists(filename):
            self.logger.error('Rules File %s does not exist' % filename)
            return None
        if not os.path.isfile(filename):
            self.logger.warning('Ignoring file %s - not a file' % filename)
            return None
        handle = open(filename)
        return self.get_rules_from_config_lines(handle.readlines())

    def get_rules_from_config_lines(self, lineslist):
        ret = []
        for line in lineslist:
            line = line.strip()
            if line.startswith('#') or line == '':
                continue
            tpl = line.split(None, 2)
            if (len(tpl) != 3):
                self.logger.debug(
                    'Ignoring invalid line  (length %s): %s' % (len(tpl), line))
                continue
            (action, regex, description) = tpl
            action = action.lower()
            if action not in [FUATT_ACTION_ALLOW, FUATT_ACTION_DENY, FUATT_ACTION_DELETE]:
                self.logger.error('Invalid rule action: %s' % action)
                continue

            tp = (action, regex, description)
            ret.append(tp)
        return ret


class FiletypePlugin(ScannerPlugin):

    """This plugin checks message attachments. You can configure what filetypes or filenames are allowed to pass through fuglu. If a attachment is not allowed, the message is deleted and the sender receives a bounce error message. The plugin uses the '''file''' library to identify attachments, so even if a smart sender renames his executable to .txt, fuglu will detect it.

Attachment rules can be defined globally, per domain or per user.

Actions: This plugin will delete messages if they contain blocked attachments.

Prerequisites: You must have the python ``file`` or ``magic`` module installed


The attachment configuration files are in ``/etc/fuglu/rules``. You whould have two default files there: ``default-filenames.conf`` which defines what filenames are allowed and ``default-filetypes.conf`` which defines what content types a attachment may have. 

For domain rules, create a new file ``<domainname>-filenames.conf`` / ``<domainname>-filetypes.conf`` , eg. ``fuglu.org-filenames.conf`` / ``fuglu.org-filetypes.conf``

For individual user rules, create a new file ``<useremail>-filenames.conf`` / ``<useremail>-filetypes.conf``, eg. ``oli@fuglu.org-filenames.conf`` / ``oli@fuglu.org-filetypes.conf``

The format of those files is as follows: Each line should have three parts, seperated by tabs (or any whitespace):
<action>    <regular expression>   <description or error message>

<action> can be one of:
 * allow : this file is ok, don't do further checks (you might use it for safe content types like text). Do not blindly create 'allow' rules. It's safer to make no rule at all, if no other rules hit, the file will be accepted
 * deny : delete this message and send the error message/description back to the sender
 * delete : silently delete the message, no error is sent back, and 'blockaction' is ignored


<regular expression> is a standard python regex. in x-filenames.conf this will be applied to the attachment name . in x-filetypes.conf this will be applied to the mime type of the file as well as the file type returned by the ``file`` command.

example of default-filetypes.conf:

::

    allow    text        -        
    allow    \bscript    -        
    allow    archive        -            
    allow    postscript    -            
    deny    self-extract    No self-extracting archives
    deny    executable    No programs allowed
    deny    ELF        No programs allowed
    deny    Registry    No Windows Registry files allowed



small extract from default-filenames.conf:

::

    deny    \.ico$            Windows icon file security vulnerability    
    deny    \.ani$            Windows animated cursor file security vulnerability    
    deny    \.cur$            Windows cursor file security vulnerability    
    deny    \.hlp$            Windows help file security vulnerability

    allow    \.jpg$            -    
    allow    \.gif$            -    



Note: The files will be reloaded automatically after a few seconds (you do not need to kill -HUP / restart fuglu)

The bounce template (eg /etc/fuglu/templates/blockedfile.tmpl) should look like this:

::

    To: ${from_address}
    Subject: Blocked attachment

    Your message to ${to_address} contains a blocked attachment and has not been delivered.

    ${blockinfo}



eg. define headers for your message at the beginning, followed by a blank line. Then append the message body.

``${blockinfo}`` will be replaced with the text you specified in the third column of the rule that blocked this message.

The other common template variables are available as well.


"""

    def __init__(self, config, section=None):
        ScannerPlugin.__init__(self, config, section)
        self.requiredvars = {
            'template_blockedfile': {
                'default': '/etc/fuglu/templates/blockedfile.tmpl',
                'description': 'Mail template for the bounce to inform sender about blocked attachment',
            },

            'sendbounce': {
                'default': '1',
                'description': 'inform the sender about blocked attachments.\nIf a previous plugin tagged the message as spam or infected, no bounce will be sent to prevent backscatter',
            },

            'rulesdir': {
                'default': '/etc/fuglu/rules',
                'description': 'directory that contains attachment rules',
            },

            'blockaction': {
                'default': 'DELETE',
                'description': 'what should the plugin do when a blocked attachment is detected\nREJECT : reject the message (recommended in pre-queue mode)\nDELETE : discard messages\nDUNNO  : mark as blocked but continue anyway (eg. if you have a later quarantine plugin)',
            },

            'dbconnectstring': {
                'default': '',
                'description': 'sqlalchemy connectstring to load rules from a database and use files only as fallback. requires SQL extension to be enabled',
                'confidential': True,
            },

            'query': {
                'default': 'SELECT action,regex,description FROM attachmentrules WHERE scope=:scope AND checktype=:checktype ORDER BY prio',
                'description': "sql query to load rules from a db. #:scope will be replaced by the recipient address first, then by the recipient domain\n:check will be replaced 'filename','contenttype','archive-filename' or 'archive-contenttype'",
            },

            'checkarchivenames': {
                'default': '0',
                'description': "enable scanning of filenames within archives (currently, only ZIP archives supported). This does not actually extract the files, it just looks at the filenames found in the archive."
            },

            'checkarchivecontent': {
                'default': '0',
                'description': 'extract compressed archives(only ZIP supported currently) and check file content type with libmagics\nnote that the files will be extracted into memory - tune archivecontentmaxsize  accordingly.\nfuglu does not extract archives within the archive(recursion)',
            },

            'archivecontentmaxsize': {
                'default': '5000000',
                'description': 'only extract and examine files up to this amount of (uncompressed) bytes',
            },

        }

        self.logger = self._logger()
        self.rulescache = None
        self.extremeverbosity = False

    def _get_file_magic(self):
        # initialize one magic instance per thread for the libmagic bindings
        # (ahupps file magic seems to do that by itself)
        if not hasattr(threadLocal, 'magic'):
            ms = magic.open(magic.MAGIC_MIME)
            ms.load()
            threadLocal.magic = ms
        return threadLocal.magic

    def examine(self, suspect):
        if self.rulescache == None:
            self.rulescache = RulesCache(
                self.config.get(self.section, 'rulesdir'))

        self.blockedfiletemplate = self.config.get(
            self.section, 'template_blockedfile')

        returnaction = self.walk(suspect)
        return returnaction

    def getFiletype(self, path):
        if MAGIC_AVAILABLE == MAGIC_PYTHON_FILE:
            ms = self._get_file_magic()
            ftype = ms.file(path)
        elif MAGIC_AVAILABLE == MAGIC_PYTHON_MAGIC:
            ftype = magic.from_file(path, mime=True)
        return ftype

    def getBuffertype(self, buffercontent):
        if MAGIC_AVAILABLE == MAGIC_PYTHON_FILE:
            ms = self._get_file_magic()
            btype = ms.buffer(buffercontent)
        elif MAGIC_AVAILABLE == MAGIC_PYTHON_MAGIC:
            btype = magic.from_buffer(buffercontent, mime=True)
        return btype

    def asciionly(self, stri):
        """return stri with all non-ascii chars removed"""
        return "".join([x for x in stri if ord(x) < 128])

    def matchRules(self, ruleset, obj, suspect, attachmentname=None):
        if attachmentname == None:
            attachmentname = ""
        attachmentname = self.asciionly(attachmentname)

        if obj == None:
            self.logger.warning(
                "%s: message has unknown name or content-type attachment %s" % (suspect.id, attachmentname))
            return ATTACHMENT_DUNNO

        # remove non ascii chars
        asciirep = self.asciionly(obj)

        displayname = attachmentname
        if asciirep == attachmentname:
            displayname = ''

        if ruleset == None:
            return ATTACHMENT_DUNNO

        for action, regex, description in ruleset:
            prog = re.compile(regex, re.I)
            if self.extremeverbosity:
                self.logger.debug('Attachment %s Rule %s' % (obj, regex))
            if prog.search(obj):
                self.logger.debug('Rulematch: Attachment=%s Rule=%s Description=%s Action=%s' % (
                    obj, regex, description, action))
                suspect.debug('Rulematch: Attachment=%s Rule=%s Description=%s Action=%s' % (
                    obj, regex, description, action))
                if action == 'deny':
                    self.logger.info('suspect %s contains blocked attachment %s %s' % (
                        suspect.id, displayname, asciirep))
                    blockinfo = "%s %s: %s" % (
                        displayname, asciirep, description)
                    suspect.tags['FiletypePlugin.errormessage'] = blockinfo
                    if self.config.getboolean(self.section, 'sendbounce'):
                        if suspect.is_spam() or suspect.is_virus():
                            self.logger.info(
                                "backscatter prevention: not sending attachment block bounce to %s - the message is tagged spam or virus" % suspect.from_address)
                        else:
                            self.logger.info(
                                "Sending attachment block bounce to %s" % suspect.from_address)
                            bounce = Bounce(self.config)
                            bounce.send_template_file(
                                suspect.from_address, self.blockedfiletemplate, suspect, dict(blockinfo=blockinfo))
                    return ATTACHMENT_BLOCK

                if action == 'delete':
                    self.logger.info(
                        'suspect %s contains blocked attachment %s %s -- SILENT DELETE! --' % (suspect.id, displayname, asciirep))
                    return ATTACHMENT_SILENTDELETE

                if action == 'allow':
                    return ATTACHMENT_OK
        return ATTACHMENT_DUNNO

    def matchMultipleSets(self, setlist, obj, suspect, attachmentname=None):
        """run through multiple sets and return the first action which matches obj"""
        self.logger.debug(
            'Checking object %s against attachment rulesets' % obj)
        for ruleset in setlist:
            res = self.matchRules(ruleset, obj, suspect, attachmentname)
            if res != ATTACHMENT_DUNNO:
                return res
        return ATTACHMENT_DUNNO

    def walk(self, suspect):
        """walks through a message and checks each attachment according to the rulefile specified in the config"""

        blockaction = self.config.get(self.section, 'blockaction')
        blockactioncode = string_to_actioncode(blockaction)

        # try db rules first
        self.rulescache.reloadifnecessary()
        dbconn = ''
        if self.config.has_option(self.section, 'dbconnectstring'):
            dbconn = self.config.get(self.section, 'dbconnectstring')

        if dbconn.strip() != '':
            self.logger.debug('Loading attachment rules from database')
            query = self.config.get(self.section, 'query')
            dbfile = DBFile(dbconn, query)
            user_names = self.rulescache.get_rules_from_config_lines(
                dbfile.getContent({'scope': suspect.to_address, 'checktype': FUATT_CHECKTYPE_FN}))
            user_ctypes = self.rulescache.get_rules_from_config_lines(
                dbfile.getContent({'scope': suspect.to_address, 'checktype': FUATT_CHECKTYPE_CT}))
            user_archive_names = self.rulescache.get_rules_from_config_lines(
                dbfile.getContent({'scope': suspect.to_address, 'checktype': FUATT_CHECKTYPE_ARCHIVE_FN}))
            user_archive_ctypes = self.rulescache.get_rules_from_config_lines(
                dbfile.getContent({'scope': suspect.to_address, 'checktype': FUATT_CHECKTYPE_ARCHIVE_CT}))
            self.logger.debug('Found %s filename rules, %s content-type rules, %s archive filename rules, %s archive content rules for address %s' %
                              (len(user_names), len(user_ctypes), len(user_archive_names), len(user_archive_ctypes), suspect.to_address))

            domain_names = self.rulescache.get_rules_from_config_lines(
                dbfile.getContent({'scope': suspect.to_domain, 'checktype': FUATT_CHECKTYPE_FN}))
            domain_ctypes = self.rulescache.get_rules_from_config_lines(
                dbfile.getContent({'scope': suspect.to_domain, 'checktype': FUATT_CHECKTYPE_CT}))
            domain_archive_names = self.rulescache.get_rules_from_config_lines(
                dbfile.getContent({'scope': suspect.to_domain, 'checktype': FUATT_CHECKTYPE_ARCHIVE_FN}))
            domain_archive_ctypes = self.rulescache.get_rules_from_config_lines(
                dbfile.getContent({'scope': suspect.to_domain, 'checktype': FUATT_CHECKTYPE_ARCHIVE_CT}))
            self.logger.debug('Found %s filename rules, %s content-type rules, %s archive filename rules, %s archive content rules for domain %s' %
                              (len(domain_names), len(domain_ctypes), len(domain_archive_names), len(domain_archive_ctypes), suspect.to_domain))
        else:
            self.logger.debug('Loading attachment rules from filesystem')
            user_names = self.rulescache.getNAMERules(suspect.to_address)
            user_ctypes = self.rulescache.getCTYPERules(suspect.to_address)
            user_archive_names = self.rulescache.getARCHIVENAMERules(
                suspect.to_address)
            user_archive_ctypes = self.rulescache.getARCHIVECTYPERules(
                suspect.to_address)

            domain_names = self.rulescache.getNAMERules(suspect.to_domain)
            domain_ctypes = self.rulescache.getCTYPERules(suspect.to_domain)
            domain_archive_names = self.rulescache.getARCHIVENAMERules(
                suspect.to_domain)
            domain_archive_ctypes = self.rulescache.getARCHIVECTYPERules(
                suspect.to_domain)

        # always get defaults from file
        default_names = self.rulescache.getNAMERules(FUATT_DEFAULT)
        default_ctypes = self.rulescache.getCTYPERules(FUATT_DEFAULT)
        default_archive_names = self.rulescache.getARCHIVENAMERules(
            FUATT_DEFAULT)
        default_archive_ctypes = self.rulescache.getARCHIVECTYPERules(
            FUATT_DEFAULT)

        m = suspect.get_message_rep()
        for i in m.walk():
            if i.is_multipart():
                continue
            contenttype_mime = i.get_content_type()
            att_name = i.get_filename(None)

            if not att_name:
                # workaround for mimetypes, it always takes .ksh for text/plain
                if i.get_content_type() == 'text/plain':
                    ext = '.txt'
                else:
                    ext = mimetypes.guess_extension(i.get_content_type())

                if ext == None:
                    ext = ''
                att_name = 'unnamed%s' % ext

            res = self.matchMultipleSets(
                [user_names, domain_names, default_names], att_name, suspect, att_name)
            if res == ATTACHMENT_SILENTDELETE:
                self._debuginfo(
                    suspect, "Attachment name=%s SILENT DELETE : blocked by name" % att_name)
                return DELETE
            if res == ATTACHMENT_BLOCK:
                self._debuginfo(
                    suspect, "Attachment name=%s : blocked by name)" % att_name)
                message = suspect.tags['FiletypePlugin.errormessage']
                return blockactioncode, message

            # go through content type rules
            res = self.matchMultipleSets(
                [user_ctypes, domain_ctypes, default_ctypes], contenttype_mime, suspect, att_name)
            if res == ATTACHMENT_SILENTDELETE:
                self._debuginfo(
                    suspect, "Attachment name=%s content-type=%s SILENT DELETE: blocked by mime content type (message source)" % (att_name, contenttype_mime))
                return DELETE
            if res == ATTACHMENT_BLOCK:
                self._debuginfo(
                    suspect, "Attachment name=%s content-type=%s : blocked by mime content type (message source)" % (att_name, contenttype_mime))
                message = suspect.tags['FiletypePlugin.errormessage']
                return blockactioncode, message

            if MAGIC_AVAILABLE:
                pl = i.get_payload(decode=True)
                contenttype_magic = self.getBuffertype(pl)
                res = self.matchMultipleSets(
                    [user_ctypes, domain_ctypes, default_ctypes], contenttype_magic, suspect, att_name)
                if res == ATTACHMENT_SILENTDELETE:
                    self._debuginfo(
                        suspect, "Attachment name=%s content-type=%s SILENT DELETE: blocked by mime content type (magic)" % (att_name, contenttype_mime))
                    return DELETE
                if res == ATTACHMENT_BLOCK:
                    self._debuginfo(
                        suspect, "Attachment name=%s content-type=%s : blocked by mime content type (magic)" % (att_name, contenttype_mime))
                    message = suspect.tags['FiletypePlugin.errormessage']
                    return blockactioncode, message

            # archives
            if self.config.getboolean(self.section, 'checkarchivenames') or self.config.getboolean(self.section, 'checkarchivecontent'):
                # some .docs can actually be zips as well.. we might have to
                # try these as well in the future
                if att_name.lower().endswith('.zip'):
                    self._debuginfo(
                        suspect, "Archive check: scanning file names in %s" % att_name)
                    try:
                        pl = StringIO(i.get_payload(decode=True))
                        zip = zipfile.ZipFile(pl)
                        namelist = zip.namelist()
                        if self.config.getboolean(self.section, 'checkarchivenames'):
                            for name in namelist:
                                res = self.matchMultipleSets(
                                    [user_archive_names, domain_archive_names, default_archive_names], name, suspect, name)
                                if res == ATTACHMENT_SILENTDELETE:
                                    self._debuginfo(
                                        suspect, "Blocked filename in archive %s SILENT DELETE" % att_name)
                                    return DELETE
                                if res == ATTACHMENT_BLOCK:
                                    self._debuginfo(
                                        suspect, "Blocked filename in archive %s" % att_name)
                                    message = suspect.tags[
                                        'FiletypePlugin.errormessage']
                                    return blockactioncode, message

                        if MAGIC_AVAILABLE and self.config.getboolean(self.section, 'checkarchivecontent'):
                            for name in namelist:
                                safename = self.asciionly(name)
                                zinfo = zip.getinfo(name)
                                if zinfo.file_size > self.config.getint(self.section, 'archivecontentmaxsize'):
                                    self._debuginfo(
                                        suspect, 'not extracting %s - uncompressed size %s too large' % (safename, zinfo.file_size))
                                    continue
                                else:
                                    self._debuginfo(
                                        suspect, 'extracting %s' % (safename))
                                extracted = zip.read(name)

                                contenttype_magic = self.getBuffertype(
                                    extracted)
                                res = self.matchMultipleSets(
                                    [user_archive_ctypes, domain_archive_ctypes, default_archive_ctypes], contenttype_magic, suspect, name)
                                if res == ATTACHMENT_SILENTDELETE:
                                    self._debuginfo(
                                        suspect, "Extracted file %s from archive %s content-type=%s SILENT DELETE: blocked by mime content type (magic)" % (safename, att_name, contenttype_magic))
                                    return DELETE
                                if res == ATTACHMENT_BLOCK:
                                    self._debuginfo(
                                        suspect, "Extracted file %s from archive %s content-type=%s : blocked by mime content type (magic)" % (safename, att_name, contenttype_magic))
                                    message = suspect.tags[
                                        'FiletypePlugin.errormessage']
                                    return blockactioncode, message

                    except Exception, e:
                        self.logger.warning(
                            "ZIP name scanning failed in attachment %s: %s" % (att_name, str(e)))
        return DUNNO

    def _debuginfo(self, suspect, message):
        """Debug to log and suspect"""
        suspect.debug(message)
        self.logger.debug(message)

    def __str__(self):
        return "Attachment Blocker"

    def lint(self):
        allok = (self.checkConfig() and self.lint_magic() and self.lint_sql())
        return allok

    def lint_magic(self):
        if not MAGIC_AVAILABLE:
            print "python libmagic bindings (python-file or python-magic) not available. Will only do content-type checks, no real file analysis"
            if self.config.getboolean(self.section, 'checkarchivecontent'):
                print "->checkarviecontent setting ignored"
            return False
        if MAGIC_AVAILABLE == MAGIC_PYTHON_FILE:
            print "Found python-file/libmagic bindings (http://www.darwinsys.com/file/)"
        if MAGIC_AVAILABLE == MAGIC_PYTHON_MAGIC:
            print "Found python-magic (https://github.com/ahupp/python-magic)"
        return True

    def lint_sql(self):
        dbconn = ''
        if self.config.has_option(self.section, 'dbconnectstring'):
            dbconn = self.config.get(self.section, 'dbconnectstring')
        if dbconn.strip() != '':
            print "Reading per user/domain attachment rules from database"
            if not fuglu.extensions.sql.ENABLED:
                print "Fuglu SQL Extension not available, cannot load attachment rules from database"
                return False
            query = self.config.get(self.section, 'query')
            dbfile = DBFile(dbconn, query)
            try:
                dbfile.getContent(
                    {'scope': 'lint', 'checktype': FUATT_CHECKTYPE_FN})
            except Exception, e:
                import traceback
                print "Could not get attachment rules from database. Exception: %s" % str(e)
                print traceback.format_exc()
                return False
        else:
            print "No database configured. Using per user/domain file configuration from %s" % self.config.get(self.section, 'rulesdir')
        return True
