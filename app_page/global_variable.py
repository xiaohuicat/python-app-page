#!/usr/bin/env python3
# -*- coding:utf-8-*-
# 全局变量管理模块global_variable

def _init():
    """在主模块初始化"""
    global IS_INIT
    IS_INIT = False
    
    global GLOBALS_DICT
    GLOBALS_DICT = {}

def set(name, value):
    """设置"""
    try:
        GLOBALS_DICT[name] = value
        return True
    except KeyError:
        return False

def get(name, default=None):
    """取值"""
    if name in GLOBALS_DICT:
        return GLOBALS_DICT[name]
    else:
        return default

def printParam(name):
    """打印参数"""
    if not name:
        import json
        print('GLOBALS_DICT:', json.dumps(GLOBALS_DICT, indent=2, ensure_ascii=False))
        return
    if name in GLOBALS_DICT:
        print(name+':', get(name))
    else:
        print('Not Found')

def getDict():
    """取值"""
    try:
        return GLOBALS_DICT
    except KeyError:
        return "Not Found"