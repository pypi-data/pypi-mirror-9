# (c) 2015, Ian Clegg <ian.clegg@sourcewarp.com>
#
# ntlmlib is licensed under the Apache License, Version 2.0 (the "License");
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
"""
         _   _           _ _ _
   _ __ | |_| |_ __ ___ | (_) |__
  | '_ \| __| | '_ ` _ \| | | '_ \
  | | | | |_| | | | | | | | | |_) |
  |_| |_|\__|_|_| |_| |_|_|_|_.__/

  A robust, fast and efficient 'first-class' Python Library for NTLM authentication, signing and encryption

"""

__title__ = 'ntlmlib'
__author__ = 'ian.clegg@sourcewarp.com'
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright 2015 Ian Clegg'

# Use version information supplied by versioneer during the build
from ._version import get_versions
__version__ = get_versions()['version']
del get_versions


# Set default logging handler to avoid "No handler found" warnings.
import logging

try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())
