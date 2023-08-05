# Copyright (c) 2014 Scopely, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
# http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

import jmespath

from skew.resources.aws import AWSResource


class AutoScalingGroup(AWSResource):

    class Meta(object):
        service = 'autoscaling'
        type = 'autoScalingGroup'
        name = 'AutoScalingGroupName'
        date = 'CreatedTime'
        dimension = 'AutoScalingGroupName'
        enum_spec = ('DescribeAutoScalingGroups', 'AutoScalingGroups')
        detail_spec = None
        id = 'AutoScalingGroupName'
        filter_name = 'auto_scaling_group_names'
        filter_type = 'list'

    def __init__(self, endpoint, data, query=None):
        super(AutoScalingGroup, self).__init__(endpoint, data, query)
        self._arn_query = jmespath.compile('AutoScalingGroupARN')

    @property
    def arn(self):
        return self._arn_query.search(self.data)


class LaunchConfiguration(AWSResource):

    class Meta(object):
        service = 'autoscaling'
        type = 'launchConfigurationName'
        name = 'LaunchConfigurationName'
        date = 'CreatedTime'
        dimension = 'AutoScalingGroupName'
        enum_spec = ('DescribeLaunchConfigurations', 'LaunchConfigurations')
        detail_spec = None
        id = 'LaunchConfigurationName'
        filter_name = 'launch_configuration_names'
        filter_type = 'list'

    def __init__(self, endpoint, data, query=None):
        super(LaunchConfiguration, self).__init__(endpoint, data, query)
        self._arn_query = jmespath.compile('LaunchConfigurationARN')

    @property
    def arn(self):
        return self._arn_query.search(self.data)
