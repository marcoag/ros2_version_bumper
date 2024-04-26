# ros2_version_bumper
Script that bumps minor version and releases ROS 2 core packages.

# Usage:

It is highly recommened to run a dry-run with:
`python3 version_bumper.py`

Once everything seems correct you can run the real bump with:
`python3 version_bumper.py --commit`

By default it bumps on `Rolling` but you can choose a different distro with `--release-name`.

For skipping repos from the ros2.repos file have a look at the SKIPLIST variable and adjust to your neeeds.

Happy Bumping!
