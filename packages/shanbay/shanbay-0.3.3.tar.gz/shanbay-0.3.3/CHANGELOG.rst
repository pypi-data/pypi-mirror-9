Changelog
=========

0.3.3 (2015-01-13)
------------------
- 修复扇贝改版导致"无法获取组员用户名导致发送短信失败"的问题
- 修复扇贝改版导致"无法成功踢人"的问题

0.3.2 (2014-08-22)
------------------
- 小组管理页面改版

0.3.1 (2014-08-05)
-------------------
- 修复"小组成员页面改版导致无法获取组员信息"


0.3.0 (2014-07-19)
-------------------
- 封装 `新版扇贝官方 API`__
- 修复"扇贝更改小组成员页面的 URL 导致无法获取组员信息"

__ http://www.shanbay.com/developer/wiki/api_v1/


0.2.1 (2014-06-24)
-------------------

- 修复 team.info 无法处理打卡率是 0% 的情况
- 登录成功时，shanbay.login() 的返回值改为 True


0.2.0 (2014-06-09)
-------------------

- 删除 ``shanbay.API``, 因为扇贝网不再支持 API v0.8, 并且新的 API 尚未释出
- 各 api 接口移除 @property 装饰器


0.1.1 (2014-05-15)
------------------

- 新增站内消息 api
- 新增小组管理 api
- 调整 api 接口

具体用法可以参考 tests/ 以及 python-shanbay-team-assistant_

.. _python-shanbay-team-assistant:  https://github.com/mozillazg/python-shanbay-team-assistant/blob/develop/assistant.py


0.1.0 (2014-03-31)
------------------

- 封装 `扇贝网 API v0.8 <http://www.shanbay.com/help/developer/api>`__.
