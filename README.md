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

# Update Enum types
ALTER TYPE enum_type ADD VALUE 'new_value'; -- appends to list
ALTER TYPE enum_type ADD VALUE 'new_value' BEFORE 'old_value';
ALTER TYPE enum_type ADD VALUE 'new_value' AFTER 'old_value';
```


管理:
```
# 创建表格
$ python manage.py --command=create_table

# 单元测试
$ py.test -s # -s to show verbose message
```

表格迁移：
```
alembic revision --autogenerate -m "change log"
alembic upgrade head
```

权限控制：
  * 私密与公开, 游客可见

资料导出：
  * Notebook 导出成 PDF

列表 API 相关的分页

基础增强：
  * 支持用户上传图片文件，并存储到用户 Git 文件夹内
  * 内容搜索 - Elasticsearch
