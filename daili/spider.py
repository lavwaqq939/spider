#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-08-15 19:54:22
# @Author  : 金建峰 (jinjianfeng_@139.com)
# @Link    : http://www.cnblogs.com/yingyunsyc/
# @Version : $Id$

import sys
import time

sys.path.append('./')

from ProxyGetter.getFreeProxy import GetFreeProxy

def test():
	proxy = GetFreeProxy.freeProxyFirst()
	print(proxy)

if __name__ == '__main__':
	test()
