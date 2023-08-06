''' 
--------------------------------------------------------------------------------------
project_conf.py
--------------------------------------------------------------------------------------
Configuration settings that detail your EC2 instances and other info about your Django
servers

author : Ashok Fernandez (github.com/ashokfernandez/)
credit : Derived from files in https://github.com/gcollazo/Fabulous
date   : 11 / 3 / 2014

Make sure you fill everything out that looks like it needs to be filled out, there are links 
in the comments to help.
'''

import os.path

fabconf = {}

#  Do not edit
fabconf['FAB_CONFIG_PATH'] = os.path.dirname(__file__)

# Project name
fabconf['PROJECT_NAME'] = "crawlnmine"

# Username for connecting to EC2 instaces - Do not edit unless you have a reason to
fabconf['SERVER_USERNAME'] = "ubuntu"

# Full local path for .ssh
fabconf['SSH_PATH'] = "~/.ssh"

# Name of the private key file you use to connect to EC2 instances
fabconf['EC2_KEY_NAME'] = "pug-ec2.pem"

# Don't edit. Full path of the ssh key you use to connect to EC2 instances
fabconf['SSH_PRIVATE_KEY_PATH'] = '%s/%s' % (fabconf['SSH_PATH'], fabconf['EC2_KEY_NAME'])

# Where to install apps
fabconf['APPS_DIR'] = "/home/%s/webapps" % fabconf['SERVER_USERNAME']

# Where you want your project installed: /APPS_DIR/PROJECT_NAME
fabconf['PROJECT_PATH'] = "%s/%s" % (fabconf['APPS_DIR'], fabconf['PROJECT_NAME'])

# App domains
fabconf['DOMAINS'] = "storydecoder.com www.storydecoder.com"

# Path for virtualenvs
fabconf['VIRTUALENV_DIR'] = "/home/%s/.virtualenvs" % fabconf['SERVER_USERNAME']

# Email for the server admin
fabconf['ADMIN_EMAIL'] = "admin@example.com"

# Git username for the server
fabconf['GIT_USERNAME'] = "EC2"

# Name of the private key file used for github deployments
fabconf['BITBUCKET_DEPLOY_KEY_NAME'] = "bitbucket_rsa"

# Don't edit. Local path for deployment key you use for github
fabconf['BITBUCKET_DEPLOY_KEY_PATH'] = "%s/%s" % (fabconf['SSH_PATH'], fabconf['BITBUCKET_DEPLOY_KEY_NAME'])

# Path to the repo of the application you want to install
fabconf['BITBUCKET_USERNAME'] = 'hobson'
fabconf['BITBUCKET_REPO_NAME'] = 'pug'

# Creates the ssh location of your bitbucket repo from the above details
fabconf['BITBUCKET_REPO'] = "ssh://git@bitbucket.org/%s/%s.git" % (fabconf['BITBUCKET_USERNAME'], fabconf['BITBUCKET_REPO_NAME'])

# Virtualenv activate command
fabconf['ACTIVATE'] = "source /home/%s/.virtualenvs/%s/bin/activate" % (fabconf['SERVER_USERNAME'], fabconf['PROJECT_NAME'])

# Name tag for your server instance on EC2
fabconf['INSTANCE_NAME_TAG'] = "pug-ec2"

# EC2 key. http://bit.ly/j5ImEZ
fabconf['AWS_ACCESS_KEY'] = 'AKIAIHGDFYXCTIQXRRAA'

# EC2 secret. http://bit.ly/j5ImEZ
fabconf['AWS_SECRET_KEY'] = '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'

#EC2 region. http://amzn.to/12jBkm7
ec2_region = 'us-west-2b'

# AMI name. http://bit.ly/liLKxj
ec2_amis = ['ami-3d50120d']  # ubuntu-trusty-14.04-amd64-server-20140927 

# Name of the keypair you use in EC2. http://bit.ly/ldw0HZ
ec2_keypair = 'pug-ec2'

# Name of the security group. http://bit.ly/kl0Jyn
ec2_secgroups = ['pug-env']

# API Name of instance type. http://bit.ly/mkWvpn
ec2_instancetype = 't1.micro'

# public IP: 54.149.151.42

# Existing instances - add the public dns of your instances here when you have spawned them
fabconf['EC2_INSTANCES'] = ["ec2-54-149-151-42.us-west-2.compute.amazonaws.com"]