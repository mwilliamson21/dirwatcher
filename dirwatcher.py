#!/usr/bin/env python2

import time
import datetime
import logging
import signal
import argparse
import os

__author__ = 'Mwilliamson with help from instructor and Zach'


logging.basicConfig(
    format='%(asctime)s.%(msecs)03d  :  %(name)-12s:  %(levelname)-8s:'
    + ' :  %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
app_start_time = datetime.datetime.now()
exit_flag = False

signames = dict((k, v) for v, k in reversed(sorted(signal.__dict__.items()))
                if v.startswith('SIG') and not v.startswith('SIG_'))

tracking_dict = {}


def watch_directory(args):
    dir_files = os.listdir(args.path)
    for f in dir_files:
        if f.endswith(args.ext) and f not in tracking_dict:
            tracking_dict[f] = 1
            logger.info("now tracking {}".format(f))

    for file in tracking_dict:
        if file not in dir_files:
            del tracking_dict[file]
            logger.info("remove {} from tracking".format(file))

    for file in tracking_dict:
        last_line = search_text(file, tracking_dict[file], args.text)
        tracking_dict[file] = last_line


def search_text(file, skip_line, magic_word):
    """reports all magic words in file starting after skipped line"""

    line_num = 0

    with open(file) as f:
        for line_num, line in enumerate(f, 1):
            if line_num < skip_line:
                continue
            if magic_word in line:
                logger.info(
                    "found magic word {} on line {} in file {}".format(
                        magic_word, line_num, file)
                    )
        # returns last line read of file
        return line_num


def signal_handler(sig_num, frame):
    """
    This is a handler for SIGTERM and SIGINT. Other signals can be mapped here
    as well (SIGHUP?)
    Basically it just sets a global flag, and main() will exit it's loop if the
    signal is trapped.
    :param sig_num: The integer signal number that was trapped from the OS.
    :param frame: Not used
    :return None
    """
    # log the associated signal name (the python3 way)
    global exit_flag
    # logger.warn('Received ' + signal.Signals(sig_num).name)
    # log the signal name (the python2 way)

    logger.warn('Received ' + signames[sig_num])
    exit_flag = True


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--ext", type=str, default=".txt",
                        help="text file extension to watch")
    parser.add_argument("-i", "--interval", type=float, default=1.0,
                        help="how often to watch the text files")
    parser.add_argument("path", help="directory to watch")
    parser.add_argument("magic", help="string to watch for")
    return parser


def main():
    # Hook these two signals from the OS ..
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    # Now my signal_handler will get called if OS sends either of these
    # to my process.
    parser = create_parser()
    args = parser.parse_args()
    uptime = datetime.datetime.now() - app_start_time
    logger.info("starting dirwatcher")
    while not exit_flag:
        try:
            # call my directory watching function..
            watch_directory(args)
            time.sleep(args.interval)
        except OSError as e:
            logger.error(str(e))
            time.sleep(5.0)

        except Exception as e:
            logger.error("unhandled exception {}".format(e))
            # This is an UNHANDLED exception
            # Log an ERROR level message here

            # put a sleep inside my while loop so I don't peg the cpu
            # usage at 100%
            time.sleep(5.0)

    # final exit point happens here
    # Log a message that we are shutting down
    # Include the overall uptime since program start.
    logger.info(
        '\n'
        '----------------------------------------------------\n'
        '   Stopped {0}\n'
        '   Uptime was {1}\n'
        '----------------------------------------------------\n'
        .format(__file__, str(uptime))
    )


if __name__ == '__main__':
    main()
