#!/bin/bash
export HOME=/root
set -eo pipefail

CHEF_WORKSTATION_UNINSTALL=0

# Install Chef Workstation from S3 if not already installed
if ! [ -x "$(command -v chef)" ]; then
  echo "Installing Chef Workstation from S3"
  aws s3 cp s3://chf-binaries/chef/chef-workstation.rpm /tmp/chef-workstation.rpm
  if [ $? -ne 0 ]; then
    echo "Failed to download Chef Workstation RPM from S3"
    exit 1
  fi

  echo "Installing Chef Workstation RPM"
  dnf install -y /tmp/chef-workstation.rpm
  if [ $? -ne 0 ]; then
    echo "Failed to install Chef Workstation"
    exit 1
  fi

  CHEF_WORKSTATION_UNINSTALL=1
else
  echo "Using existing Chef"
fi

# Use Chef version of Ruby
eval "$(chef shell-init sh)"

# Install aws-sdk-ssm gem from S3
# echo "Installing aws-sdk-ssm gem from S3"
# aws s3 cp s3://chf-binaries/gems/aws-sdk-ssm-1.207.0.gem /tmp/aws-sdk-ssm.gem
# if [ $? -ne 0 ]; then
#   echo "Failed to download aws-sdk-ssm gem from S3"
#   exit 1
# fi

# /opt/chef-workstation/embedded/bin/gem install /tmp/aws-sdk-ssm.gem --local
# /opt/chef-workstation/embedded/bin/gem list | grep aws-sdk-ssm

# Run InSpec tests against this server and report compliance
EXITCODE=0
echo "Executing InSpec tests"

# Accept Chef license
export CHEF_LICENSE=accept-no-persist
export CHEF_LICENSE_ACCEPT=yes

# Prevent RubyGems ambiguity warnings
# export GEM_HOME=/opt/chef-workstation/embedded/lib/ruby/gems
# export GEM_PATH=$GEM_HOME
# export GEM_SPEC_CACHE=/opt/chef-workstation/embedded/spec_cache

# unset pipefail as InSpec exits with error code if any tests fail
set +eo pipefail

set +e
inspec exec . --reporter json > Report-Compliance-20200225
INSPEC_RC=$?
set -e


case "$INSPEC_RC" in
  0)
    echo "InSpec: all controls passed"
    EXITCODE=0
    ;;
  100)
    echo "InSpec: compliance findings detected"
    EXITCODE=0
    ;;
  *)
    echo "InSpec execution failed with code $INSPEC_RC"
    EXITCODE=2
    ;;
esac

# Optionally uninstall Chef Workstation if we installed it above
if [ "$CHEF_WORKSTATION_UNINSTALL" = "1" ]; then
  echo "Uninstalling Chef Workstation"
  if [ -x "$(command -v dnf)" ]; then
    PACKAGE=$(rpm -qa chef-workstation)
    dnf remove -y $PACKAGE
  elif [ -x "$(command -v yum)" ]; then
    PACKAGE=$(rpm -qa chef-workstation)
    yum remove -y $PACKAGE
  fi
fi

exit $EXITCODE
