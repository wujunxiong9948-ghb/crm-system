#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统设置API模块
"""

from flask import Blueprint

settings_bp = Blueprint('settings', __name__)

# 导入路由
from . import users
from . import roles
from . import company
from . import dictionary
from . import logs
from . import profile
from . import notifications
