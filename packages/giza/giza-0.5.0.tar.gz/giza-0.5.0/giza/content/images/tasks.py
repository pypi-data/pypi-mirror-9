# Copyright 2014 MongoDB, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os.path
import logging

import wand.image
import wand.api
import wand.color
import libgiza.task

import giza.content.images.views
import giza.tools.files

logger = logging.getLogger('giza.content.images')


def generate_image(build_type, dpi, width, target, source):
    with wand.image.Image(filename=source, resolution=dpi) as image:
        if image.width != width:
            image.transform(resize=str(width))

        if build_type == 'png':
            alpha = 0.0
        elif build_type == 'eps':
            alpha = 1.0
        else:
            raise TypeError(build_type + " is not supported")

        try:
            image.transparent_color(color=wand.color.Color('white'), alpha=alpha)
        except:
            pass

        with open(target, 'wb') as out:
            out.write(image.make_blob(build_type))

    logger.info('wrote: ' + target)


def image_tasks(conf):
    tasks = []

    deps = conf.system.files.get_configs('images')
    deps.append(os.path.abspath(__file__))

    if 'images' not in conf.system.files.data:
        return []

    for image in conf.system.files.data.images:
        if not os.path.isfile(image.source_core):
            logger.error('"{0}" does not exist'.format(image.source_core))
            continue

        description = "generating rst include file {0} for {1}".format(image.rst_file,
                                                                       image.source_core)
        t = libgiza.task.Task(job=giza.content.images.views.generate_image_pages,
                              args=(image, conf),  # as kwargs
                              target=image.rst_file,
                              dependency=deps,
                              description=description)
        tasks.append(t)

        if conf.runstate.fast is True:
            continue

        for output in image.outputs:
            description = 'generating image file {0} from {1}'.format(output.target,
                                                                      image.source_core)
            t = libgiza.task.Task(job=generate_image,
                                  args=(output.build_type, output.dpi, output.width,
                                        output.output, image.source_file),
                                  target=output.output,
                                  dependency=image.source_core,
                                  description=description)
            tasks.append(t)

    logger.info('registered {0} image generation tasks'.format(len(tasks)))

    return tasks


def image_clean(conf):
    if 'images' not in conf.system.files.data:
        logger.info('no images to clean')
        return []

    tasks = []
    for image in conf.system.files.data.images:
        for output in image.outputs:
            t = libgiza.task.Task(job=giza.tools.files.verbose_remove,
                                  args=output.output,
                                  target=True,
                                  dependency=None,
                                  description="removing img file")
            tasks.append(t)

    return tasks
