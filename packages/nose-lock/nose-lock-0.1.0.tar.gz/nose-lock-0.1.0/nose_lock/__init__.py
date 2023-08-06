import sys
import logging
import os
import pwd

from nose.plugins import Plugin
from lockfile import FileLock

log = logging.getLogger('nose.plugins.lock')


def get_owner(path):
    stat = os.stat(path)
    data = pwd.getpwuid(stat.st_uid)
    return data.pw_name


class NoseLock(Plugin):
    name = 'lock'

    def options(self, parser, env=os.environ):
        super(NoseLock, self).options(parser, env=env)

    def configure(self, options, conf):
        super(NoseLock, self).configure(options, conf)
        if not self.enabled:
            self.lock = None
        else:
            # getting reasonable defaults
            app_dir = os.getcwd()
            app_name = os.path.basename(app_dir)
            lock_path = os.path.join('/tmp', app_name)
            self.lock = FileLock(lock_path)

            if self.lock.is_locked():
                owner = get_owner(lock_path + '.lock')
                if owner:
                    print ('User {0} already running the tests, '
                           'please keep calm.').format(owner)
            try:
                self.lock.acquire()
            except KeyboardInterrupt:
                print '\nYou are so impatient today!\nBye.'
                sys.exit(1)


    def finalize(self, result):
        log.info('Hello pluginized world!')
        if self.lock:
            self.lock.release()
