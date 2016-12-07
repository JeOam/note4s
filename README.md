#note4s


测试管理员帐号密码：

test@test.com
123456

test@test.cn
123456

配置:
```
# 开发环境
CREATE USER note4s WITH PASSWORD 'note4s';
CREATE DATABASE note4s OWNER note4s;
GRANT ALL PRIVILEGES ON DATABASE note4s to note4s;

# 测试环境
CREATE USER note4s_test WITH PASSWORD 'note4s_test';
CREATE DATABASE note4s_test OWNER note4s_test;
GRANT ALL PRIVILEGES ON DATABASE note4s_test to note4s_test;
```

管理:
```
# 创建表格
$ python manage.py --command=sync_db

# 单元测试
$ py.test -s # -s to show verbose message
```

表格迁移：
```
alembic revision --autogenerate -m "change log"
alembic upgrade head
```

Timeline 系统：
个人 timeline
团队 timeline
关注的人 timeline
缓存与分页

通知系统：
个人通知
团队通知
