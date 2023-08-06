from os import path as osp

from lib.middleware import db  # noqa: convenience for apps using this library

cdir = osp.abspath(osp.dirname(__file__))
VERSION = open(osp.join(cdir, 'version.txt')).read().strip()
