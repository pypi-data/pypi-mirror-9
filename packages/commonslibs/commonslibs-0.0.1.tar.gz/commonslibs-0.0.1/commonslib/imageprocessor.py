#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 2011-8-15

@author: huwei
"""

from __future__ import division
from StringIO import StringIO
from app.commons.fileutil import force_mkdir
from PIL import Image
import os.path


class ImageWrapper(object):
    
    def __init__(self, image_data):
        self.image = Image.open(StringIO(image_data)).copy()
        (self.width, self.height) = self.image.size


class ImageRender(object):

    def __init__(self, image_render):
        self.image_render = image_render
    
    def render(self):
        pass


class WriteParameter(object):

    def __init__(self, write_file):
        self.write_file = write_file


class WriteRender(ImageRender):

    def __init__(self, image_wrapper, write_param, image_render=None):
        ImageRender.__init__(self, image_render)
        self.image_wrapper = image_wrapper
        self.write_param = write_param

    def render(self):
        if self.image_render:
            self.image_wrapper = self.image_render.render()
        force_mkdir(os.path.dirname(self.write_param.write_file))
        self.image_wrapper.image.save(self.write_param.write_file)
        return self.image_wrapper


class CropParameter(object):
    """图片切割参数类."""
    CROP_TYPE_CENTER = 'center'
    """居中自适应缩放切割."""
    CROP_TYPE_OFFSET = 'offset'
    """基于坐标偏移切割."""

    def __init__(self, width, height, crop_type='center', x=0, y=0, background_file=None):
        """图片切割.

        :param width: float
        :param height: float
        :param crop_type: string 当值为CROP_TYPE_CENTER的时候，无需x y参数
        :param x: float
        :param y: float
        :param background_file: string 背景图片
        """
        self.width = width
        self.height = height
        self.crop_type = crop_type
        self.x = x
        self.y = y
        self.background_image = None
        if background_file:
            self.background_image = Image.open(background_file)


class CropRender(ImageRender):
    """切割渲染类
    """

    def __init__(self, image_wrapper, crop_param, image_render=None):
        """切割渲染.

        :param image_wrapper:
        :param crop_param:
        :param image_render:
        """
        ImageRender.__init__(self, image_render)
        self.image_wrapper = image_wrapper
        self.crop_param = crop_param
    
    def render(self):
        """执行渲染逻辑.

        :return: image_wrapper
        """
        if self.image_render:
            self.image_wrapper = self.image_render.render()
        
        if self.crop_param is None:
            return self.image_wrapper
        
        crop_image = Image.new('F', (self.crop_param.width, self.crop_param.height))
        if CropParameter.CROP_TYPE_OFFSET == self.crop_param.crop_type:
            # 按照偏移位置剪切
            region = self.image_wrapper.image.crop((
                self.crop_param.x,
                self.crop_param.y,
                self.crop_param.x+self.crop_param.width,
                self.crop_param.y+self.crop_param.height))
            crop_image = crop_image.paste(region, (0, 0, self.crop_param.width, self.crop_param.height))
        else:
            # 居中剪切
            actual_width = self.image_wrapper.width
            actual_height = self.image_wrapper.height
            #切割后的宽长的比率
            rate = self.crop_param.width/self.crop_param.height
            rate_hw = self.crop_param.height/self.crop_param.width
            if self.image_wrapper.width/self.image_wrapper.height > rate:
                #宽度过宽，需要一定x坐标
                self.crop_param.x = int((self.image_wrapper.width-self.image_wrapper.height*rate)/2)
                actual_width = int(actual_height*rate)
            elif self.image_wrapper.width/self.image_wrapper.height < rate:
                #长度过长
                self.crop_param.y = int((self.image_wrapper.height-self.image_wrapper.width*rate_hw)/2)
                actual_height = int(actual_width*rate_hw)

            region = self.image_wrapper.image.crop((
                self.crop_param.x,
                self.crop_param.y,
                self.crop_param.x+actual_width,
                self.crop_param.y+actual_height))

            size = (self.crop_param.width, self.crop_param.height)
            crop_image = region.resize(size, Image.ANTIALIAS)
        self.image_wrapper.image = crop_image
        self.image_wrapper.height = self.crop_param.height
        self.image_wrapper.width = self.crop_param.width
        return self.image_wrapper


def process(file_name, write_param, crop_param=None):
    image_wrapper = ImageWrapper(file_name)
    crop_render = CropRender(image_wrapper, crop_param)
    write_render = WriteRender(image_wrapper, write_param, crop_render)
    return write_render.render()
