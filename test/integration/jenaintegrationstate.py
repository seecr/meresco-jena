## begin license ##
#
# The Meresco Jena package is an Jena Fuseki Triplestore
#
# Copyright (C) 2014 Seecr (Seek You Too B.V.) http://seecr.nl
#
# This file is part of "Meresco Jena"
#
# "Meresco Jena" is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# "Meresco Jena" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with "Meresco Jena"; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

from os import system
from os.path import join, dirname, abspath

from seecr.test.integrationtestcase import IntegrationState
from seecr.test.portnumbergenerator import PortNumberGenerator


myDir = dirname(abspath(__file__))
serverBinDir = join(dirname(dirname(myDir)), 'bin')

class JenaIntegrationState(IntegrationState):
    def __init__(self, stateName, tests=None, fastMode=False):
        IntegrationState.__init__(self, stateName=stateName, tests=tests, fastMode=fastMode)

        self.jenaDataDir = join(self.integrationTempdir, 'jena-data')
        self.jenaPort = PortNumberGenerator.next()
        self.testdataDir = join(dirname(myDir), 'data')
        if not fastMode:
            system('rm -rf ' + self.integrationTempdir)
            system('mkdir --parents ' + self.jenaDataDir)

    def setUp(self):
        self.startJenaServer()

    def binDir(self):
        return serverBinDir

    def startJenaServer(self):
        self._startServer('jena', self.binPath('start-jena'), 'http://localhost:%s/query' % self.jenaPort, port=self.jenaPort, stateDir=self.jenaDataDir)

    def restartJenaServer(self):
        self.stopJenaServer()
        self.startJenaServer()

    def stopJenaServer(self):
        self._stopServer('jena')

