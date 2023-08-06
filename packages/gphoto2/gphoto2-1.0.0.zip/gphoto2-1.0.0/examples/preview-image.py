#!/usr/bin/env python

# python-gphoto2 - Python interface to libgphoto2
# http://github.com/jim-easterbrook/python-gphoto2
# Copyright (C) 2015  Jim Easterbrook  jim@jim-easterbrook.me.uk
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function

import logging
import os
import io
import subprocess
import sys
import time

import PIL.Image

import gphoto2 as gp

def main():
    logging.basicConfig(
        format='%(levelname)s: %(name)s: %(message)s', level=logging.WARNING)
    gp.check_result(gp.use_python_logging())
    context = gp.gp_context_new()
    camera = gp.check_result(gp.gp_camera_new())
    gp.check_result(gp.gp_camera_init(camera, context))
    for n in range(5):
        print('Capturing image')
        cam_file = gp.check_result(gp.gp_camera_capture_preview(camera, context))
        gp.check_result(gp.gp_file_save(cam_file, 'test.jpg'))
        print(cam_file)
##        data = gp.check_result(gp.gp_file_get_data_and_size(cam_file))
##        print(type(data), len(data), map(ord, data[:40]))
##        buff = io.BytesIO(data)
##        print(map(ord, buff.read(40)))
##        buff.seek(0)
##        image = PIL.Image.open(buff)
##        print(image.size, image.mode)
        time.sleep(0.01)
##    print('Camera file path: {0}/{1}'.format(file_path.folder, file_path.name))
##    target = os.path.join('/tmp', file_path.name)
##    print('Copying image to', target)
##    camera_file = gp.check_result(gp.gp_camera_file_get(
##            camera, file_path.folder, file_path.name,
##            gp.GP_FILE_TYPE_NORMAL, context))
##    gp.check_result(gp.gp_file_save(camera_file, target))
##    subprocess.call(['xdg-open', target])
    gp.check_result(gp.gp_camera_exit(camera, context))
    return 0

if __name__ == "__main__":
    sys.exit(main())
