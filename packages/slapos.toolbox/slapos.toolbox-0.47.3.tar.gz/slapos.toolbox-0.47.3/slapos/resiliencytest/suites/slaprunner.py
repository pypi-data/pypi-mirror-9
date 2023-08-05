# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2013 Vifib SARL and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from .resiliencytestsuite import ResiliencyTestSuite

import base64
import cookielib
import json
from lxml import etree
import random
import ssl
import string
import time
import urllib2

class NotHttpOkException(Exception):
  pass

class SlaprunnerTestSuite(ResiliencyTestSuite):
  """
  Run Slaprunner Resiliency Test.
  It is highly suggested to read ResiliencyTestSuite code.
  """
  def __init__(self, *args, **kwargs):
    # Setup urllib2 with cookie support
    cookie_jar = cookielib.CookieJar()
    ssl_context = ssl._create_unverified_context()

    self._opener_director = urllib2.build_opener(
        urllib2.HTTPCookieProcessor(cookie_jar),
        urllib2.HTTPSHandler(context=ssl_context)
    )

    ResiliencyTestSuite.__init__(self, *args, **kwargs)

  def _getPartitionParameterDict(self):
    """
    Helper.
    Return the partition parameter dict of the main root ("resilient") instance.
    """
    # XXX Hardcoded parameters, should be obtained dynamically
    return self.partition.request(
      software_release=self.software,
      software_type='resilient',
      partition_reference=self.root_instance_name,
      partition_parameter_kw={
        'resiliency-backup-periodicity': '*/6 * * * *',
        'auto-deploy-instance': 'false',
        'auto-deploy': 'true',
        # XXX HACK!
        "slapos-reference": 'slaprunner-erp5-resiliency'
        }
    ).getConnectionParameterDict()
    self.deleteTimestamp()

  def _connectToSlaprunner(self, resource, data=None):
    """
    Utility.
    Connect through HTTP to the slaprunner instance.
    Require self.slaprunner_backend_url to be set.
    """
    url = "%s/%s" % (self.slaprunner_backend_url, resource)
    if data:
      result = self._opener_director.open(url, data=data)
    else:
      result = self._opener_director.open(url)

    if result.getcode() is not 200:
      raise NotHttpOkException(result.getcode())
    return result.read()

  def _login(self):
    self.logger.debug('Logging in...')
    b64string = base64.encodestring('%s:%s' % (self.slaprunner_user, self.slaprunner_password))[:-1]
    self._opener_director.addheaders = [('Authorization', 'Basic %s'%b64string)]

  def _retrieveInstanceLogFile(self):
    """
    Store the logfile (=data) of the instance, check it is not empty nor it is
    html.
    """
    time.sleep(30)
    data = self._connectToSlaprunner(
        resource='getFileContent',
        data="file=instance_root/slappart0/var/log/log.log"
    )
    try:
        data = json.loads(data)['result']
        self.logger.info('Retrieved data are:\n%s' % data)
    except (ValueError, KeyError):
        if data.find('<') is not -1:
          raise IOError(
              'Could not retrieve logfile content: retrieved content is html.'
          )
        if data.find('Could not load') is not -1:
          raise IOError(
              'Could not retrieve logfile content: server could not load the file.'
          )
        if data.find('Hello') is -1:
          raise IOError(
              'Could not retrieve logfile content: retrieve content does not match "Hello".'
          )
    return data


  def _waitForSoftwareBuild(self, limit=5000):
    """
    Wait until SR is built or limit reach 0
    """
    def getSRStatus():
      """
      Return current status (-1 in case of connection problem)
      """
      try:
        return self._connectToSlaprunner(resource='isSRReady')
      except (NotHttpOkException, urllib2.HTTPError) as error:
        # The nginx frontend might timeout before software release is finished.
        self.logger.warning('Problem occured when contacting the server: %s' % error)
        return -1

    status = getSRStatus()
    while limit > 0 and status != '1':
      status = getSRStatus()
      limit -= 1
      self.logger.info('Software release is still building. Sleeping...')
      time.sleep(60)


  def _buildSoftwareRelease(self):
    self.logger.info('Building the Software Release...')
    try:
      self._connectToSlaprunner(resource='runSoftwareProfile')
    except (NotHttpOkException, urllib2.HTTPError):
      # The nginx frontend might timeout before software release is finished.
      pass

    self._waitForSoftwareBuild()

  def _deployInstance(self):
    self.logger.info('Deploying instance...')
    try:
      self._connectToSlaprunner(resource='runInstanceProfile')
    except (NotHttpOkException, urllib2.HTTPError):
      # The nginx frontend might timeout before someftware release is finished.
      pass
    while True:
      time.sleep(15)
      result = json.loads(self._connectToSlaprunner(resource='slapgridResult', data='position=0&log='))
      if result['instance']['state'] is False:
        break
      self.logger.info('Buildout is still running. Sleeping...')
    self.logger.info('Instance has been deployed.')

  def _gitClone(self):
    self.logger.debug('Doing git clone of git.erp5.org/repos/slapos.git...')
    try:
      self._connectToSlaprunner(
          resource='cloneRepository',
          data='repo=http://git.erp5.org/repos/slapos.git&name=workspace/slapos&email=slapos@slapos.org&user=slapos'
      )
    except (NotHttpOkException, urllib2.HTTPError):
      # cloning can be very long.
      # XXX: quite dirty way to check.
      while self._connectToSlaprunner('getProjectStatus', data='project=workspace/slapos').find('On branch master') is -1:
        self.logger.info('git-cloning ongoing, sleeping...')

  def _openSoftwareRelease(self, software_name):
    self.logger.debug('Opening %s software release...' % software_name)
    self._connectToSlaprunner(
        resource='setCurrentProject',
        data='path=workspace/slapos/software/%s/' % software_name
    )

  def _getRcode(self):
    #XXX-Nicolas: hardcoded url. Best way right now to automate the tests...
    monitoring_password = "passwordtochange"
    monitor_url = self.monitor_url + "?script=zero-knowledge%2Fsettings.cgi"
    result = self._opener_director.open(monitor_url,
                                       "password=" + monitoring_password + ";password_2=" + monitoring_password)

    if result.getcode() is not 200:
      raise NotHttpOkException(result.getcode())

    page = result.read().strip()
    html = etree.HTML(page)

    input = html.xpath("//input[@name='recovery-code']")
    return input[0].get('value')

  def generateData(self):
    self.slaprunner_password = ''.join(
        random.SystemRandom().sample(string.ascii_lowercase, 8)
    )
    self.slaprunner_user = 'slapos'
    self.logger.info('Generated slaprunner user is: %s' % self.slaprunner_user)
    self.logger.info('Generated slaprunner password is: %s' % self.slaprunner_password)

  def pushDataOnMainInstance(self):
    """
    Create a dummy Software Release,
    Build it,
    Wait for build to be successful,
    Deploy instance,
    Wait for instance to be started.
    Store the main IP of the slaprunner for future use.
    """
    self.logger.debug('Getting the backend URL and recovery code...')
    parameter_dict = self._getPartitionParameterDict()
    self.slaprunner_backend_url = parameter_dict['backend_url']
    self.logger.info('backend_url is %s.' % self.slaprunner_backend_url)
    self.monitor_url = parameter_dict['monitor_backend_url']
    slaprunner_recovery_code = self._getRcode()

    self.logger.debug('Creating the slaprunner account...')
    self._connectToSlaprunner(
        resource='configAccount',
        data='name=slapos&username=%s&email=slapos@slapos.org&password=%s&rcode=%s' % (
            self.slaprunner_user,
            self.slaprunner_password,
            slaprunner_recovery_code
        )
    )

    self._login()

    self._gitClone()
    # XXX should be taken from parameter.
    self._openSoftwareRelease('helloworld')

    self._buildSoftwareRelease()
    time.sleep(15)
    self._deployInstance()

    self.data = self._retrieveInstanceLogFile()

  def checkDataOnCloneInstance(self):
    """
    Check that:
      * backend_url is different
      * Software Release profile is the same,
      * Software Release is built and is the same, (?)
      * Instance is deployed and is the same.
    """
    # XXX: does the promise wait for the software to be built and the instance to be ready?
    old_slaprunner_backend_url = self.slaprunner_backend_url
    self.slaprunner_backend_url = self._returnNewInstanceParameter(
        parameter_key='backend_url',
        old_parameter_value=old_slaprunner_backend_url
    )
    self._login()
    self._waitForSoftwareBuild()
    time.sleep(15)
    new_data = self._retrieveInstanceLogFile()

    if new_data == self.data:
      self.logger.info('Data are the same: success.')
      return True
    else:
      self.logger.info('Data are different: failure.')


def runTestSuite(*args, **kwargs):
  """
  Run Slaprunner Resiliency Test.
  """
  return SlaprunnerTestSuite(*args, **kwargs).runTestSuite()

