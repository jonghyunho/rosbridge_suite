#!/usr/bin/env python
PKG = 'rosbridge_library'
import roslib
roslib.load_manifest(PKG)
roslib.load_manifest("std_msgs")
import rospy
from rospy import get_published_topics

from rosbridge_library.protocol import Protocol
from rosbridge_library.protocol import InvalidArgumentException, MissingArgumentException
from rosbridge_library.capabilities.advertise import Registration, Advertise
from rosbridge_library.internal.publishers import manager
from rosbridge_library.internal import ros_loader

from std_msgs.msg import String

from json import loads, dumps

import unittest


class TestAdvertise(unittest.TestCase):

    def setUp(self):
        rospy.init_node("test_advertise")

    def is_topic_published(self, topicname):
        return topicname in dict(get_published_topics()).keys()

    def test_missing_arguments(self):
        proto = Protocol("hello")
        adv = Advertise(proto)
        msg = {"op": "advertise"}
        self.assertRaises(MissingArgumentException, adv._advertise, None, loads(dumps(msg)))

        msg = {"op": "advertise", "topic": "/jon"}
        self.assertRaises(MissingArgumentException, adv._advertise, None, loads(dumps(msg)))

        msg = {"op": "advertise", "type": "std_msgs/String"}
        self.assertRaises(MissingArgumentException, adv._advertise, None, loads(dumps(msg)))

    def test_invalid_arguments(self):
        proto = Protocol("hello")
        adv = Advertise(proto)

        msg = {"op": "advertise", "topic": 3, "type": "std_msgs/String"}
        self.assertRaises(InvalidArgumentException, adv._advertise, None, loads(dumps(msg)))

        msg = {"op": "advertise", "topic": "/jon", "type": 3}
        self.assertRaises(InvalidArgumentException, adv._advertise, None, loads(dumps(msg)))

    def test_invalid_msg_typestrings(self):
        invalid = ["", "/", "//", "///", "////", "/////", "bad", "stillbad",
       "not/better/still", "not//better//still", "not///better///still",
       "better/", "better//", "better///", "/better", "//better", "///better",
       "this\isbad", "\\"]

        proto = Protocol("hello")
        adv = Advertise(proto)

        for invalid_type in invalid:
            msg = {"op": "advertise", "topic": "/test_invalid_msg_typestrings",
                   "type": invalid_type}
            self.assertRaises(ros_loader.InvalidTypeStringException,
                              adv._advertise, None, loads(dumps(msg)))

    def test_invalid_msg_package(self):
        nonexistent = ["wangle_msgs/Jam", "whistleblower_msgs/Document",
        "sexual_harrassment_msgs/UnwantedAdvance", "coercion_msgs/Bribe",
        "airconditioning_msgs/Cold", "pr2thoughts_msgs/Escape"]

        proto = Protocol("hello")
        adv = Advertise(proto)

        for invalid_type in nonexistent:
            msg = {"op": "advertise", "topic": "/test_invalid_msg_package",
                   "type": invalid_type}
            self.assertRaises(ros_loader.InvalidPackageException,
                              adv._advertise, None, loads(dumps(msg)))

    def test_invalid_msg_module(self):
        no_msgs = ["roslib/Time", "roslib/Duration", "roslib/Header",
        "std_srvs/ConflictedMsg", "topic_tools/MessageMessage"]

        proto = Protocol("hello")
        adv = Advertise(proto)

        for invalid_type in no_msgs:
            msg = {"op": "advertise", "topic": "/test_invalid_msg_module",
                   "type": invalid_type}
            self.assertRaises(ros_loader.InvalidModuleException,
                              adv._advertise, None, loads(dumps(msg)))

    def test_invalid_msg_classes(self):
        nonexistent = ["roscpp/Time", "roscpp/Duration", "roscpp/Header",
        "rospy/Time", "rospy/Duration", "rospy/Header", "std_msgs/Spool",
        "geometry_msgs/Tetrahedron", "sensor_msgs/TelepathyUnit"]

        proto = Protocol("hello")
        adv = Advertise(proto)

        for invalid_type in nonexistent:
            msg = {"op": "advertise", "topic": "/test_invalid_msg_classes",
                   "type": invalid_type}
            self.assertRaises(ros_loader.InvalidClassException,
                              adv._advertise, None, loads(dumps(msg)))

    def test_valid_msg_classes(self):
        assortedmsgs = ["geometry_msgs/Pose", "actionlib_msgs/GoalStatus",
        "geometry_msgs/WrenchStamped", "stereo_msgs/DisparityImage",
        "nav_msgs/OccupancyGrid", "geometry_msgs/Point32", "std_msgs/String",
        "trajectory_msgs/JointTrajectoryPoint", "diagnostic_msgs/KeyValue",
        "visualization_msgs/InteractiveMarkerUpdate", "nav_msgs/GridCells",
        "sensor_msgs/PointCloud2"]

        proto = Protocol("hello")
        adv = Advertise(proto)

        for valid_type in assortedmsgs:
            msg = {"op": "advertise", "topic": "/" + valid_type,
                   "type": valid_type}
            adv.advertise(loads(dumps(msg)))
            adv.unadvertise(loads(dumps(msg)))

    def test_do_advertise(self):
        proto = Protocol("hello")
        adv = Advertise(proto)
        topic = "/test_do_advertise"
        type = "std_msgs/String"

        msg = {"op": "advertise", "topic": topic, "type": type}
        adv.advertise(loads(dumps(msg)))
        self.assertTrue(self.is_topic_published(topic))
        adv.unadvertise(loads(dumps(msg)))
        self.assertFalse(self.is_topic_published(topic))


if __name__ == '__main__':
    import rostest
    rostest.rosrun(PKG, 'test_publish', TestAdvertise)