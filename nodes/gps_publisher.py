#!/usr/bin/env python

# Copyright (c) 2014 Michael Ferguson
# Copyright (c) 2013 Vanadium Labs LLC.
# All right reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of Vanadium Labs LLC nor the names of its
#     contributors may be used to endorse or promote products derived
#     from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL VANADIUM LABS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import socket
import time

import rospy
from nmea_msgs.msg import Sentence
from etherbotix_python.etherbotix import *

## @brief This is a simple wrapper that connects to the Etherbotix,
##        sets up USART3 to forward packets that are '\n' terminated,
##        and publishes those packets as GPS sentences.
class GPSPublisher(Etherbotix):

    def __init__(self, ip="192.168.0.42", port=6707):
        Etherbotix.__init__(self, ip, port)
        self.publisher = rospy.Publisher("nmea_sentence", Sentence, queue_size=10)
        self.frame_id = rospy.get_param("~frame_id", "base_link")

    def setup(self):
        # Set baud to 9600, set terminating character to '\n' (10)
        self.write(253, self.P_USART_BAUD, [207, 10])

    def run(self):
        self.setup()
        while not rospy.is_shutdown():
            packet = self.getPacket()
            if packet:
                s = Sentence()
                s.header.frame_id = self.frame_id
                s.header.stamp = rospy.Time.now()
                s.sentence = packet.params.rstrip()
                self.publisher.publish(s)

if __name__=="__main__":
    rospy.init_node("gps_publisher")
    g = GPSPublisher()
    g.run()