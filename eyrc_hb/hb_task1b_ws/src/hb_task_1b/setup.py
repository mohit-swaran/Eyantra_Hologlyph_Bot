from setuptools import find_packages, setup
import os
from glob import glob       
package_name = 'hb_task_1b'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        
        (os.path.join('share',package_name),glob('launch/*.launch.py')),
        (os.path.join('share',package_name, 'urdf'),    glob('urdf/*.xacro')),
        (os.path.join('share',package_name, 'meshes'),  glob('meshes/*')),
        (os.path.join('share',package_name, 'scripts'), glob('scripts/*')),
        (os.path.join('share',package_name, 'worlds'), glob('worlds/*')),

        
          
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='mohit',
    maintainer_email='mohit.swaran@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'hb_task1b_controller=hb_task_1b.controller:main',
            'service_node=hb_task_1b.service_node:main',
            'Go-To-Goal_Node=hb_task_1b.t_gtg:main',
        ],
    },
)
