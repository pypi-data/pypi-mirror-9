from setuptools import setup, find_packages
import glob
import os

version = '0.48'
name = 'slapos.toolbox'
long_description = open("README.txt").read() + "\n" + \
    open("CHANGES.txt").read() + "\n"

for f in sorted(glob.glob(os.path.join('slapos', 'README.*.txt'))):
  long_description += '\n' + open(f).read() + '\n'

# Provide a way to install additional requirements
additional_install_requires = []
try:
  import argparse
except ImportError:
  additional_install_requires.append('argparse')

setup(name=name,
      version=version,
      description="SlapOS toolbox.",
      long_description=long_description,
      classifiers=[
          "Programming Language :: Python",
        ],
      keywords='slapos toolbox',
      license='GPLv3',
      namespace_packages=['slapos'],
      packages=find_packages(),
      include_package_data=True,
      install_requires=[
        'Flask', # needed by servers
        'atomize', # needed by pubsub
        'feedparser', # needed by pubsub
        'apache_libcloud>=0.4.0', # needed by cloudmgr
        'lockfile', # used by equeue
        'lxml', # needed for xml parsing
        'paramiko', # needed by cloudmgr
        'psutil', # needed for playing with processes in portable way
        'setuptools', # namespaces
        'slapos.core', # as it provides library for slap
        'xml_marshaller', # needed to dump information
        'GitPython', #needed for git manipulation into slaprunner
        'netifaces', 'rpdb'
      ] + additional_install_requires,
      extras_require = {
        'lampconfigure':  ["mysql-python"], #needed for MySQL Database access
        'zodbpack': ['ZODB3'], # needed to play with ZODB
        'agent': ['erp5.util'],
        'flask_auth' : ["Flask-Auth"],
        'check_web_page_http_cache_hit' : ['pycurl'], # needed for check_web_page_http_cache_hit module
      },
      zip_safe=False, # proxy depends on Flask, which has issues with
                      # accessing templates
      entry_points={
        'console_scripts': [
          'agent = slapos.agent.agent:main [agent]',
          'check-web-page-http-cache-hit = slapos.promise.check_web_page_http_cache_hit:main',
          'clouddestroy = slapos.cloudmgr.destroy:main',
          'cloudgetprivatekey = slapos.cloudmgr.getprivatekey:main',
          'cloudgetpubliciplist = slapos.cloudmgr.getpubliciplist:main',
          'cloudlist = slapos.cloudmgr.list:main',
          'cloudmgr = slapos.cloudmgr.cloudmgr:main',
          'cloudstart = slapos.cloudmgr.start:main',
          'cloudstop = slapos.cloudmgr.stop:main',
          'equeue = slapos.equeue:main',
          'htpasswd = slapos.htpasswd:main',
          'is-local-tcp-port-opened = slapos.promise.is_local_tcp_port_opened:main',
          'killpidfromfile = slapos.systool:killpidfromfile', # BBB
          'runResiliencyUnitTestTestNode = slapos.resiliencytest:runUnitTest',
          'runResiliencyScalabilityTestNode = slapos.resiliencytest:runResiliencyTest',
          'runStandaloneResiliencyTest = slapos.resiliencytest:runStandaloneResiliencyTest',
          'lampconfigure = slapos.lamp:run [lampconfigure]',
          'onetimedownload = slapos.onetimedownload:main',
          'onetimeupload = slapos.onetimeupload:main',
          'pubsubnotifier = slapos.pubsub.notifier:main',
          'pubsubserver = slapos.pubsub:main',
          'qemu-qmp-client = slapos.qemuqmpclient:main',
          'shacache = slapos.shacache:main',
          'slapbuilder = slapos.builder:main',
          'slapcontainer = slapos.container:main',
          'slapmonitor = slapos.monitor:run_slapmonitor',
          'slapmonitor-xml = slapos.monitor:run_slapmonitor_xml',
          'slapos-kill = slapos.systool:kill',
          'slapreport = slapos.monitor:run_slapreport',
          'slaprunnertest = slapos.runner.runnertest:main',
          'slaprunnerteststandalone = slapos.runner.runnertest:runStandaloneUnitTest',
          'zodbpack = slapos.zodbpack:run [zodbpack]',
          'networkbench = slapos.networkbench:main'
        ]
      },
    )
