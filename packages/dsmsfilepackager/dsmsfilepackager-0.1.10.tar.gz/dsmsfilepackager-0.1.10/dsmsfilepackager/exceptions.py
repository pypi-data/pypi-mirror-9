import sftpsyncer.exceptions
import sys

# Massage exceptions from sftpsyncer into the local namespace.
# This is probably not advisable.
# TODO: review and make more advisable.

module = sys.modules[globals()['__name__']]

for attr in dir(sftpsyncer.exceptions):
    exception_candidate = getattr(sftpsyncer.exceptions, attr)
    # i.e. it's class-like
    if isinstance(exception_candidate, type):
        setattr(module, attr, exception_candidate)
