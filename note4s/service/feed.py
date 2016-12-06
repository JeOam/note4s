# -*- coding: utf-8 -*-

"""
    feed.py
    ~~~~~~~
    维护个人 timeline 的 feed 流；队列入库，生成缓存

    1. 关注的人、团队内的人新建了 Note
    2. 关注的 note 新增了 subnote
    3. 某人关注了某人
    4. 某人 star 了某 note
    5. 自己的 timeline feed
"""