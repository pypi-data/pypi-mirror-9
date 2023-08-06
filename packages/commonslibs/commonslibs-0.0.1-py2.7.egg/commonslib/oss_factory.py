#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 2014-9-16
upload file function.
author: wanglei
"""
import logging
import os.path

from oss.oss_api import OssAPI
import yaml

from configs.settings import Settings


class OssFactory(object):
    """oss阿里云存储
    """
    oss_file_config = None

    @staticmethod
    def download_site(name, runmod='development'):
        if OssFactory.oss_file_config is None:
            file_stream = file(os.path.join(Settings.SITE_ROOT_PATH, 'configs/oss_config.yaml'), 'r')
            yml = yaml.load(file_stream)
            OssFactory.oss_file_config = yml.get(runmod)
        oss_file_config = OssFactory.oss_file_config.get(name)
        if oss_file_config is not None:
            return oss_file_config.get('download_site')
        else:
            return None

    @staticmethod
    def get_instance(name, runmod='development'):
        if OssFactory.oss_file_config is None:
            file_stream = file(os.path.join(Settings.SITE_ROOT_PATH, 'configs/oss_config.yaml'), 'r')
            yml = yaml.load(file_stream)
            OssFactory.oss_file_config = yml.get(runmod)
        oss_file_config = OssFactory.oss_file_config.get(name)
        if oss_file_config:
            return OssFactory(regional_node=oss_file_config.get('regional_node'),
                              id=oss_file_config.get('id'),
                              key=oss_file_config.get('key'),
                              bucket=oss_file_config.get('bucket'))
        else:
            return None

    def __init__(self, regional_node=None, id=None, key=None, bucket="eking-test1",max_idle_time=7 * 3600):
        self.regional_node = regional_node
        self.id = id
        self.key = key
        self.bucket = bucket
        self.max_idle_time = max_idle_time

    def upload_file(self, file_data, file_path):
        """上传文件到oss服务器上

        :param file_data: 文件的数据
        :param file_path: 保存到OSS的路径
        :return:
        """
        oss = OssAPI(self.regional_node, self.id, self.key)
        res = oss.put_object_from_string(self.bucket, file_path, file_data)
        if 200 == res.status:
            return True, file_path
        else:
            #log
            res_message = "OSS ERROR\n%s\n%s" % (res.status, res.read())
            logging.info(res_message)
            return False, u'上传文件出错！'

    def delete_file(self, file_path):
        oss = OssAPI(self.regional_node, self.id, self.key)
        res = oss.delete_object(self.bucket, file_path)
        if 204 == res.status:
            #log
            res_message = "\n%s\n%s" % (res.status, '删除原来文件成功')
            logging.info(res_message)
        else:
            #log
            res_message = "\n%s\n%s" % (res.status, '删除原来文件失败')
            logging.info(res_message)