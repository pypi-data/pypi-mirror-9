#!/usr/bin/python
"""
A read-only python driver for Micromeritics 3Flex surface characterization
analyzers.

Distributed under the GNU General Public License v2
Copyright (C) 2015 NuMat Technologies
"""
import socket
import sys
from telnetlib import Telnet


def try_float(value):
    """Attempts to convert to float, and returns value if not possible."""
    try:
        return float(value)
    except ValueError:
        return value


class Analyzer(object):
    """Python driver for [Micromeritics 3Flex surface characterization
    analyzers](http://www.micromeritics.com/Product-Showcase/
    3Flex-Surface-Characterization-Analyzer.aspx).

    This reads the state of the 3Flex through a raw TCP/IP connection. This
    interface is read-only, providing no means to control the equipment.
    """
    red = "\033[01;31m"
    native = "\033[m\r\n"
    error_message = "Could not connect to 3Flex. Is it running?"

    def __init__(self, address="192.168.77.100", timeout=2):
        """Connects to the appropriate IP address.

        Args:
            address: The IP address of the 3Flex. Default 192.168.77.100.
            timeout: Maximum time to wait for reply, in seconds.
        """
        self.timeout = timeout
        try:
            self.conn = Telnet(address, 54000, timeout)
        except socket.timeout:
            sys.stderr.write(self.red + self.error_message + self.native)
            raise
        self.first_line = self.read_line()

    def get(self):
        """Returns the current state of the 3Flex, as a dictionary.

        On every read, the 3Flex returns 58 fields. This method organizes these
        fields into a hierarchical object with three top-level keys: time,
        manifold, and ports. Ports contains the most information, providing
        independent data for each of the three ports on the 3Flex.

        Units are in milliseconds, torr, Kelvin, cc, and cc (STP).
        """
        row = [try_float(item) for item in self.read_line().split("\t")]
        return {"time": row[3],
                "manifold": {"pressure": row[0], "volume": row[1],
                             "temperature": row[2]},
                "ports": [{"pressure": r[0],
                           "volume": r[1],
                           "temperatures": {"overall": r[2],
                                            "ambient": r[3],
                                            "analysis": r[4]},
                           "freespace": {"warm": r[5],
                                         "cold": r[6]},
                           "dosed": r[7],
                           "adsorbed": r[8],
                           "has_manifold": bool(r[9]),
                           "valve_open": bool(r[10]),
                           "data_points_taken": int(r[11]),
                           "pressure_table_index": int(r[12]),
                           "last_data_point": {"elapsed_time": r[13],
                                               "pressure": r[14],
                                               "p0": r[17],
                                               "dosed": r[15],
                                               "adsorbed": r[16]}}
                          for r in [row[4:22], row[22:40], row[40:]]]}

    def read_line(self):
        try:
            line = self.conn.read_until(b"\r\n", timeout=self.timeout)
        except socket.timeout:
            sys.stderr.write(self.red + self.error_message + self.native)
            raise
        return line.decode("utf-8").strip()

    def close(self):
        """Closes the connection to the 3Flex."""
        self.conn.close()


def command_line():
    """Runs the command-line interface to this driver."""
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Read the state of a "
                                     "Micromeritics 3Flex from the command "
                                     "line.")
    parser.add_argument("address", nargs="?", default="192.168.77.100",
                        help="The IP address of the 3Flex. Default "
                        "192.168.77.100.")
    parser.add_argument("--stream", "-s", action="store_true",
                        help="Sends a constant stream of 3Flex data, "
                             "formatted as a tab-separated table.")
    args = parser.parse_args()

    analyzer = Analyzer(args.address)

    if args.stream:
        try:
            print(analyzer.first_line)
            while True:
                print(analyzer.read_line())
        except KeyboardInterrupt:
            pass
    else:
        print(json.dumps(analyzer.get(), indent=2, sort_keys=True))
    analyzer.close()


if __name__ == "__main__":
    command_line()
