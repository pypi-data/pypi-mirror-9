from client.protocols.common import models
from client.utils import format
import hmac
import logging

log = logging.getLogger(__name__)

class LockProtocol(models.Protocol):
    """Locking protocol that wraps that mechanism."""

    name = 'lock'

    def on_start(self):
        """Responsible for locking each test."""
        if not self.args.lock:
            return

        format.print_line('~')
        print('Locking tests')
        print()

        for test in self.assignment.test_map.values():
            log.info('Locking {}'.format(test.name))
            test.lock(self._hash_fn)

    def _hash_fn(self, text):
        text = format.normalize(text)
        return hmac.new(self.assignment.name.encode('utf-8'),
                        text.encode('utf-8')).hexdigest()

protocol = LockProtocol
