cmake_minimum_required(VERSION 3.5)
project(labsim)

# Find required packages
find_package(ament_cmake REQUIRED)

# Install the URDF and STL files
install(
  DIRECTORY labsim/urdf/
  DESTINATION share/${PROJECT_NAME}/labsim/urdf
)

# Install parameters
install(
  DIRECTORY labsim/parameters/
  DESTINATION share/${PROJECT_NAME}/labsim/parameters
)

# Install worlds
install(
  DIRECTORY worlds/
  DESTINATION share/${PROJECT_NAME}/worlds
)

# Install Launch
install(
  DIRECTORY launch/
  DESTINATION share/${PROJECT_NAME}/launch
)

# Export package dependencies
ament_package()




