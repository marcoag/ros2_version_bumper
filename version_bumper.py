import argparse
import logging
import git
import github
import os
import requests
import subprocess
import sys
import tempfile
import yaml

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('create-release-branches')

ROS2_REPOS_URL = 'https://github.com/ros2/ros2'

def github_raw_from_url(url: str, filename: str):
    # Given something like https://github.com/ros2/ros2 and '/rolling/ros.repos',
    # this will produce 'https://raw.githubusercontent.com/ros2/ros2/rolling/ros2.repos'
    if not url.startswith('https://github.com/'):
        raise Exception('URL must start with https://github.com/')
    return url.replace('https://github.com', 'https://raw.githubusercontent.com') + filename

def download_ros2_repos(release_name):
    ros2_repos_file_url = github_raw_from_url(ROS2_REPOS_URL, f'/{release_name}/ros2.repos')

    logger.info(f'Downloading ros2.repos file from {ros2_repos_file_url}')

    response = requests.get(ros2_repos_file_url)
    if not response.ok:
        raise Exception('Failed to fetch %s: %s' % (ros2_repos_file_url, str(response)))
    return yaml.safe_load(response.text)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--commit', help='Actually push to remote repositories and open PRs', action='store_true', default=False)
    parser.add_argument('--release_name', help='Rosdistro to be used with spring', action='store_true', default='rolling')
    args = parser.parse_args()

    # Download the ros2.repos file
    ros2_repos = download_ros2_repos(args.release_name)

    SKIPLIST = ('ament/ament_index', 'eProsima/Fast-CDR', 'eProsima/Fast-DDS', 'eProsima/foonathan_memory_vendor', 'eclipse-cyclonedds/cyclonedds', 'eclipse-iceoryx/iceoryx', 'osrf/osrf_pycommon', 'ros/urdfdom', 'ros/urdfdom_headers', 'gazebo-release/gz_utils_vendor', 'gazebo-release/gz_math_vendor', 'gazebo-release/gz_cmake_vendor')

    for name, repo_info in ros2_repos['repositories'].items():
        if name in SKIPLIST:
            logger.info(f'Skipping repository {name} in SKIP_LIST')
            continue
        logger.info(f'Bumping minor version of {name} on {args.release_name}.')

        #git clone repo_
        tmpdirname = tempfile.mkdtemp()
        logger.info(f'Cloning {name} in {tmpdirname}')
        gitrepo = git.Repo.clone_from(repo_info['url'], tmpdirname)
        gitrepo.git.checkout(repo_info['version'])
        os.chdir(gitrepo.working_dir)

        #generate_changelog + commit
        subprocess.check_call(['catkin_generate_changelog', '-y'])
        gitrepo.git.add(A=True)
        gitrepo.git.commit('-s', m='Changelog.')

        #release prepare and push
        if (args.commit):
            subprocess.check_call(['catkin_prepare_release', '--bump', 'minor', '-y'])
        else:    
            subprocess.check_call(['catkin_prepare_release', '--bump', 'minor', '-y', '--no-push'])

        #bloom
        if (args.commit):
            subprocess.check_call(['bloom-release', name.split('/')[1], '--rosdistro', args.release_name, '--non-interactive'])
        else:
            subprocess.check_call(['bloom-release', name.split('/')[1], '--rosdistro', args.release_name, '--non-interactive', '--pretend'])

if __name__ == '__main__':
    sys.exit(main())
