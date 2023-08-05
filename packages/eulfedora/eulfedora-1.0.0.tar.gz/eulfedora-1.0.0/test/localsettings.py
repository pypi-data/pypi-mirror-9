# file localsettings.py.dist
#
#   Copyright 2011 Emory University Libraries
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import logging

# dev_tunnel to salk:8743 (fedora34-test)
# FEDORA_ROOT = 'https://localhost.library.emory.edu:7100/fedora/'
# FEDORA_ROOT_NONSSL = 'https://localhost.library.emory.edu:7100/fedora/'

FEDORA_ROOT = 'https://wlibdev002.library.emory.edu:8743/fedora/'
# FEDORA_ROOT_NONSSL = 'https://wlibdev002.library.emory.edu:8743/fedora/'
FEDORA_ROOT_NONSSL = 'http://wlibdev002.library.emory.edu:8380/fedora/'

#FEDORA_ROOT_NONSSL = 'http://localhost:8080/fedora/'
FEDORA_USER = 'fedoraAdmin'
FEDORA_PASSWORD = 'fedoraAdmin'
FEDORA_PIDSPACE = 'eulfedora-test'

#logging.basicConfig(level=logging.INFO)
