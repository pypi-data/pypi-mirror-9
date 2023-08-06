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
        # getting reasonable defaults
        app_dir = os.getcwd()
        app_name = os.path.basename(app_dir)
        default_lock_file = os.path.join('/tmp', app_name)

        parser.add_option(
            '--lock-file', action='store',
            default=default_lock_file,
            dest='lock_file',
            help='Use this file to acquire lock (default: {0})'.format(
                default_lock_file))

    def configure(self, options, conf):
        super(NoseLock, self).configure(options, conf)
        if not self.enabled:
            self.lock = None
        else:
            lock_file = options.lock_file
            self.lock = FileLock(lock_file)

            if self.lock.is_locked():
                owner = get_owner(lock_file + '.lock')
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
