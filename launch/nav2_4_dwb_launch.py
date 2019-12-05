# Copyright (c) 2018 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

""" This is all-in-one launch script intended for use by nav2 developers. """

import os

from ament_index_python.packages import get_package_prefix
from ament_index_python.packages import get_package_share_directory
from launch.conditions import IfCondition
from nav2_common.launch import RewrittenYaml

import launch.actions
import launch_ros.actions


def generate_launch_description():
    # Get the launch directory
    launch_dir = os.path.join(get_package_share_directory('nav2_bringup'), 'launch')

    # Create the launch configuration variables
    autostart = launch.substitutions.LaunchConfiguration('autostart')
    bt_xml_file = launch.substitutions.LaunchConfiguration('bt')
    params_file = launch.substitutions.LaunchConfiguration('params')

    # Create our own temporary YAML files that include the following parameter substitutions
    param_substitutions = {
        'autostart': autostart,
        'bt_xml_filename': bt_xml_file,
    }
    configured_params = RewrittenYaml(
        source_file=params_file, rewrites=param_substitutions, convert_types=True)

    # Declare the launch arguments
    declare_autostart_cmd = launch.actions.DeclareLaunchArgument(
        'autostart',
        default_value='true',
        description='Automatically startup the nav2 stack')

    declare_bt_xml_cmd = launch.actions.DeclareLaunchArgument(
        'bt',
        default_value=os.path.join(
            get_package_prefix('nav2_bt_navigator'),
            'behavior_trees/navigate_w_replanning_and_recovery.xml'),
        description='Full path to the Behavior Tree XML file to use for the BT navigator')

    declare_params_file_cmd = launch.actions.DeclareLaunchArgument(
        'params',
        default_value=[launch.substitutions.ThisLaunchFileDir(), '/../params/nav2_params.yaml'],
        description='Full path to the ROS2 parameters file to use for all launched nodes')

    stdout_linebuf_envvar = launch.actions.SetEnvironmentVariable(
        'RCUTILS_CONSOLE_STDOUT_LINE_BUFFERED', '1')

    start_dwb_cmd = launch.actions.ExecuteProcess(
        cmd=[
            os.path.join(
                get_package_prefix('dwb_controller'),
                'lib/dwb_controller/dwb_controller'),
            ['__params:=', configured_params]],
        cwd=[launch_dir], output='screen')

    # Create the launch description and populate
    ld = launch.LaunchDescription()

    # Declare the launch options
    ld.add_action(declare_autostart_cmd)
    ld.add_action(declare_bt_xml_cmd)
    ld.add_action(declare_params_file_cmd)

    # Set environment variables
    ld.add_action(stdout_linebuf_envvar)

    # Add the actions to launch all of the navigation nodes
    ld.add_action(start_dwb_cmd)

    return ld
