import os
import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from pathlib import Path


def generate_launch_description():

    pkg_share = get_package_share_directory('robot_description')

    xacro_file = os.path.join(
        pkg_share,
        'urdf',
        'robot_description.urdf.xacro'
    )

    robot_description = xacro.process_file(xacro_file).toxml()

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[
            {'robot_description': robot_description,
             "use_sim_time": True
            }
        ]
    )

    world_file = os.path.join(
        pkg_share,
        'worlds',
        'world.sdf'
    )

    gazebo_resource_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=[
            str(Path(pkg_share).parent.resolve())
        ]
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('ros_gz_sim'),
                'launch',
                'gz_sim.launch.py'
            )
        ),
        launch_arguments=[
            ("gz_args", [" -v 4", " -r ", world_file])
        ]
    )

    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        output="screen",
        arguments=[
            '-topic', 'robot_description',
            '-name', 'mobile_manipulator_robot',
            '-z', '0.1',
            '-Y', '1.57'
        ],
    )

    clock_bridge = Node(
    package='ros_gz_bridge',
    executable='parameter_bridge',
    arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'],
    output='screen'
)

    return LaunchDescription([
        robot_state_publisher,
        gazebo_resource_path,
        gazebo,
        spawn_robot,
        clock_bridge
    ])