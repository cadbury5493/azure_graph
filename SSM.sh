 curl -s \
  "https://omnitruck.chef.io/stable/chef-workstation/metadata?v=25.9.1094&p=amazon&pv=2&m=x86_64" \
  > metadata.json

  curl -L -o chef-workstation.rpm https://packages.chef.io/files/stable/chef-workstation/25.9.1094/el/7/chef-workstation-25.9.1094-1.el7.x86_64.rpm

file chef-workstation.rpm



# Detect OS version
PLATFORM=$(awk -F= '/^NAME/{print $2}' /etc/os-release | tr -d '"')
PLATFORM_VERSION=$(awk -F= '/^VERSION_ID/{print $2}' /etc/os-release | tr -d '"')

echo "Detected platform: $PLATFORM $PLATFORM_VERSION"

# Decide S3 path based on platform
if [[ "$PLATFORM" == "Amazon Linux" && "$PLATFORM_VERSION" == "2" ]]; then
  CHEF_S3_PATH="s3://chf-binaries/chef/al2/chef-workstation.rpm"
elif [[ "$PLATFORM" == "Amazon Linux" && "$PLATFORM_VERSION" == "2023" ]]; then
  CHEF_S3_PATH="s3://chf-binaries/chef/amazon2023/chef-workstation.rpm"
else
  echo "Unsupported platform: $PLATFORM $PLATFORM_VERSION"
  exit 1
fi

----------
# On public machine Download chef rpm

curl -s \
  "https://omnitruck.chef.io/stable/chef-workstation/metadata?v=25.9.1094&p=amazon&pv=2023&m=x86_64" \
  > metadata.json

curl -L -o chef-workstation.rpm "$RPM_URL"

file chef-workstation.rpm

#  Upload to S3
aws s3 cp chef-workstation.rpm s3://chf-binaries/chef/

# On private machine download the binary and install it
aws s3 cp s3://chf-binaries/chef/chef-workstation.rpm /tmp/
dnf install -y /tmp/chef-workstation.rpm

# Verify installed includes inspec
chef --version
inspec version

----------
# On Public machine fetch the gem and upload to s3
gem fetch aws-sdk-ssm
aws s3 cp aws-sdk-ssm-*.gem s3://my-secure-bucket/gems/

# On private machine install the gem

which gem


aws s3 cp s3://chf-binaries/gems/aws-sdk-ssm-1.207.0.gem /tmp/aws-sdk-ssm.gem


/opt/chef-workstation/embedded/bin/gem install /tmp/aws-sdk-ssm-1.149.0.gem --local

/opt/chef-workstation/embedded/bin/gem list | grep aws-sdk-ssm

-----

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
echo "Installing aws-sdk-ssm gem from S3"
aws s3 cp s3://chf-binaries/gems/aws-sdk-ssm-1.207.0.gem /tmp/aws-sdk-ssm.gem
if [ $? -ne 0 ]; then
  echo "Failed to download aws-sdk-ssm gem from S3"
  exit 1
fi

/opt/chef-workstation/embedded/bin/gem install /tmp/aws-sdk-ssm.gem --local
/opt/chef-workstation/embedded/bin/gem list | grep aws-sdk-ssm

# Run InSpec tests against this server and report compliance
EXITCODE=0
echo "Executing InSpec tests"

# Accept Chef license
export CHEF_LICENSE=accept-no-persist

# unset pipefail as InSpec exits with error code if any tests fail
set +eo pipefail
inspec exec . --reporter json | ruby ./Report-Compliance-20200225
if [ $? -ne 0 ]; then
  echo "Failed to execute InSpec tests: see stderr"
  EXITCODE=2
fi

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
