import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import xacro

PKG_SRC = 'labsim'
MODELS_SRC = 'urdf'
WORLDS_SRC = 'worlds'
ROBOT = 'adsmt-wheeled.xacro'
ROLLE = 'roll_e.xacro'
CONES_TEST_WORLD = 'cones_test.sdf'
EASY_WORLD = 'easy.sdf'
START_WORLD = 'start.sdf'
WORLD = "easy"

def generate_launch_description():
    robot_name = "ads-mt"
    rolle_name = "roll-e"
    name_package = "labsim"

    # Robot file
    robot_file = os.path.join(
        get_package_share_directory(name_package),
        PKG_SRC,
        MODELS_SRC,
        ROBOT
    )

    # ROLL-E
    rolle_file = os.path.join(
        get_package_share_directory(name_package),
        PKG_SRC,
        MODELS_SRC,
        ROLLE
    )

    # World file
    world = os.path.join(
        get_package_share_directory(name_package),
        WORLDS_SRC,
        EASY_WORLD
    )

    # Gazebo launcher
    gazebo_ros_launch = PythonLaunchDescriptionSource(
        os.path.join(
            get_package_share_directory('ros_gz_sim'),
            'launch',
            'gz_sim.launch.py'
        )
    )

    gazebo_launch_des = IncludeLaunchDescription(
        gazebo_ros_launch,
        launch_arguments={
            'gz_args': f'-r -v -v4 {world}',
            'on_exit_shutdown': 'true',
        }.items()
    )

    # Process xacro
    # robot_xml = xacro.process_file(robot_file).toxml()
    rolle_xml = xacro.process_file(rolle_file).toxml()

    # Spawn main robot
    spawn_model_gazebo = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', robot_name,
            '-topic', 'robot_description',
        ],
        output='screen',
    )

    # Spawn ROLL-E
    spawn_rolle_gazebo = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', rolle_name,
            '-topic', 'robot_description',
        ],
        output='screen',
    )

    # # Robot state publishers
    # robot_state_publisher = Node(
    #     package='robot_state_publisher',
    #     executable='robot_state_publisher',
    #     output='screen',
    #     parameters=[{
    #         'robot_description': robot_xml,
    #         'use_sim_time': True,
    #     }],
    # )

    rolle_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': rolle_xml,
            'use_sim_time': True,
        }],
    )

    vcu = Node(
        package="vcu_package",
        executable= "sim_endpoint",
        output="screen")
    
    ppo = Node(
        package="cltm_package",
        executable= "vcu_eval",
        output="screen")


    control = Node(
        package="control_package",
        executable= "rolle",
        output="screen")

    # Bridge config (this may fail at runtime if path is wrong, but it won't break parsing)
   

    # ROLL-E Specific Bridge
    rolle_bridge_file =  os.path.join(
        get_package_share_directory(name_package),
        'labsim',
        'parameters',
        'rolle_bridge.yaml'
    )

    rolle_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            # === Services we want bridged ===
            # SetEntityPose: move roll-e around
            f"/world/{WORLD}/set_pose@ros_gz_interfaces/srv/SetEntityPose",
            # (Optional) world control: pause/reset/etc
            f"/world/{WORLD}/control@ros_gz_interfaces/srv/ControlWorld",

            # === Existing YAML config for topics ===
            "--ros-args",
            "-p", f"config_file:={rolle_bridge_file}",
        ],
        output='screen',
    )


    ld = LaunchDescription()

    # Gazebo
    ld.add_action(gazebo_launch_des)

    # Robot + ROLL-E
    # ld.add_action(spawn_model_gazebo)
    # ld.add_action(robot_state_publisher)

    ld.add_action(spawn_rolle_gazebo)
    ld.add_action(rolle_state_publisher)


    ld.add_action(rolle_bridge)
    ld.add_action(vcu)
    ld.add_action(ppo)

    return LaunchDescription(ld.entities)
    # or simply: `return ld`
