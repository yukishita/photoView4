import configparser

import photoview4.controller.photoviewcontroller

"""Configファイルの読み込み"""
config = configparser.ConfigParser()
config.read('config.ini')

photoView = photoview4.controller.photoviewcontroller.raspiCloudController( config )
photoView.startup()