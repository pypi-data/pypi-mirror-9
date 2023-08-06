#!/usr/bin/env python
# -*- coding: utf-8 -*-
import MySQLdb
import getpass
import os
import platform
import re
import time

import inflection
from tornado.template import Template, Loader
import yaml

from configs.settings import Settings


__author__ = 'wangshubin'


class MyLoader(Loader):
    """
        不对空格进行过滤，保留文件的原始格式
        原Loader对html，js进行了空格过滤，破坏了原始的文件格式
    """

    def _create_template(self, name):
        path = os.path.join(self.root, name)
        with open(path, "rb") as f:
            my_template = Template(f.read(), name=name, loader=self, compress_whitespace=False)
            return my_template


class MyTemplate(object):
    @staticmethod
    def get_template_string(template_path, template_file_name, namespace):
        loader = MyLoader(template_path)
        t = loader.load(template_file_name)
        return t.generate(**namespace)


class DBMessage(object):
    """
        获取数据库相关信息类
    """
    runmod = "development"
    database_config = None

    def __init__(self, config_name=None):
        self.conn = self.get_conn(config_name)

    def get_conn(self, config_name=None):
        """获取数据库连接，当前使用的是MySql数据库，如果更换数据库，新建子类，重写该方法即可

        :param config_name:
        :return:
        """
        if config_name is None:
            config_name = "default"
        if not self.database_config:
            file_stream = file(os.path.join(Settings.SITE_ROOT_PATH, 'configs/databases.yaml'), 'r')
            yml = yaml.load(file_stream)
            databases_config = yml.get(self.runmod)
            config = databases_config[config_name]
            url = config["url"]  # sqlA的连接字符串，要截取mysqlDB所要的信息
            self.database_config = dict()
            self.database_config["user"] = url[16:url.rindex(":")]
            self.database_config["passwd"] = url[url.rindex(":") + 1:url.rindex("@")]
            self.database_config["host"] = url[url.rindex("@") + 1:url.rindex("/")]
            self.database_config["database"] = url[url.rindex("/") + 1:url.rindex("?")]
            self.database_config["charset"] = url[url.rindex("charset=") + 8:]
        else:
            pass

        # 建立和数据库系统的连接
        conn = MySQLdb.connect(host=self.database_config["host"], user=self.database_config["user"], passwd=self.database_config["passwd"], charset=self.database_config["charset"])
        conn.select_db("information_schema")
        return conn

    def get_schema_names(self):
        """获取所有数据库名  获取数据库连接，当前使用的是MySql数据库，如果更换数据库，新建子类，重写该方法即可


        :return:
        """
        cursor = self.conn.cursor()
        # 执行SQL 获取所有字段信息
        cursor.execute("SELECT DISTINCT table_schema FROM columns ")
        row = cursor.fetchall()
        schema_names = list()
        ignore_names = ("information_schema", "mysql")
        for (table_schema,) in row:
            if table_schema not in ignore_names:
                schema_names.append(table_schema)
        return tuple(schema_names)

    def get_table_names(self, table_schema):
        """获取数据库中所有表名 获取数据库连接，当前使用的是MySql数据库，如果更换数据库，新建子类，重写该方法即可

        :param table_schema:
        :return:
        """
        cursor = self.conn.cursor()
        # 执行SQL 获取所有字段信息
        cursor.execute("SELECT DISTINCT table_name FROM columns WHERE table_schema='" + table_schema + "'")
        row = cursor.fetchall()
        table_names = list()
        for (table_name,) in row:
            table_names.append(table_name)
        return tuple(table_names)

    def get_columns(self, table_name):
        """根据表名，获取数据库字段信息 获取数据库连接，当前使用的是MySql数据库，如果更换数据库，新建子类，重写该方法即可

        :return: 所有的字段信息
        """
        cursor = self.conn.cursor()
        # 执行SQL 获取所有字段信息
        cursor.execute(""" SELECT column_name,
                             column_default,
                             is_nullable,
                             data_type,
                             column_type,
                             column_comment
                             FROM columns
                             WHERE table_schema='""" + self.database_config["database"] + """' AND table_name = '""" + table_name + """' """)
        row = cursor.fetchall()
        method_keys = self.get_where_types()
        order_by_keys = ("asc", "desc")
        edit_keys = self.get_edit_types()
        columns = list()
        for (column_name, column_default, is_nullable, data_type, column_type, column_comment) in row:
            column_length = self.get_column_length(column_type)
            sql_a_type = self.get_sql_a_type(data_type)
            column_title = self.get_first_word(column_comment)
            col_msg = dict()
            col_msg["column_name"] = column_name  # 字段
            col_msg["column_title"] = column_title  # 字段对应的中文 默认为column_comment中截取；用于生成页面
            col_msg["column_comment"] = ""  # 数据库中的备注，用于生成title  .py文件中的注释等
            col_msg["data_type"] = data_type  # sql类型
            col_msg["column_default"] = column_default  # 默认值
            col_msg["is_nullable"] = is_nullable  # 是否为空
            col_msg["column_length"] = column_length  # 字段长度

            col_msg["sql_a_type"] = sql_a_type  # 对应的sqlA类型

            col_msg["condition_search"] = False  # 是否参与条件查询 及 参与条件查询类型 where条件
            col_msg["order_by"] = False  # 是否参与排序 及 排序方式
            col_msg["edit_type"] = self.get_sql_edit_type(data_type)  # 编辑类型 默认数据库类型 或 input
            col_msg["option_type"] = None  # 下拉类型 大写字符串
            col_msg["gets_by"] = False  # 按字段查询所有
            col_msg["get_by"] = False  # 按字段查询第一个
            # file_path=""  # service handler view 子文件夹  这个应该在表注释中 好像没有表注释 通过命令参数形式给出吧

            if column_comment:
                comments = column_comment.split("\n")
                col_msg["column_comment"] = comments[0]  # 数据库中的备注，用于生成title  .py文件中的注释等
                if len(comments) > 1:
                    # 存在第二行的配置
                    config_str = comments[1]
                    configs = config_str.split(" ")
                    for conf in configs:
                        if conf in method_keys:
                            col_msg["condition_search"] = conf
                        if conf in order_by_keys:
                            col_msg["order_by"] = conf
                        if conf in edit_keys:
                            col_msg["edit_type"] = conf
                        if conf.isupper():
                            col_msg["option_type"] = conf
                        if conf == "get_by":
                            col_msg["get_by"] = True
                        if conf == "gets_by":
                            col_msg["gets_by"] = True

            columns.append(col_msg)
        return columns

    def get_namespace(self, table_name, ext_namespace=None):
        """获取到文件魔板所需的变量


        :return:
        """
        columns = self.get_columns(table_name)
        singular_table_name = inflection.singularize(table_name)
        model_name = self.get_model_name(table_name)
        sys_user_name = self.get_sys_user_name()
        created_at = time.strftime('%Y-%m-%d %H:%M:%S')
        sql_a_types = self.get_all_sql_a_type(columns)
        mixins = self.get_all_mixin(columns)

        condition_search_columns = list()
        get_by_columns = list()
        gets_by_columns = list()
        order_by_columns = list()
        for col in columns:
            if col["condition_search"]:
                condition_search_columns.append(col)
            if col["get_by"]:
                get_by_columns.append(col)
            if col["gets_by"]:
                gets_by_columns.append(col)
            if col["order_by"]:
                order_by_columns.append(col)

        namespace = dict(model_name=model_name,  # sqlA 映射对象名, 用于生成类名等
                         table_name=table_name,  # 表名（复数形式） 可以用户列表的变量命名
                         singular_table_name=singular_table_name,  # 表名的单数形式 可用于单数实例的命名
                         sys_user_name=sys_user_name,  # 系统用户名，一般用于生成文件头部的注释
                         created_at=created_at,  # 当前系统时间，一般用于文件头部的注释
                         sql_a_types=sql_a_types,  # 对应的sqlA类型（不仅限于sqlA，如果以后使用其他框架，修改get_all_sql_a_type方法即可）
                         mixins=mixins,  # 相关mixin IdMixin等。。。
                         columns=columns,  # 数据库字段信息，自定义编辑信息等一些关于字段的信息
                         condition_search_columns=condition_search_columns,  # 存产于条件查询的列信息 便于模版处理
                         order_by_columns=order_by_columns,  # 存产于条件查询的排序信息 便于模版处理
                         gets_by_columns=gets_by_columns,  # 存产于字段查询的列信息 便于模版处理
                         get_by_columns=get_by_columns  # 存产于字段查询的列信息 便于模版处理
        )
        # 定制参数
        if ext_namespace:
            namespace.update(ext_namespace)
        return namespace

    @staticmethod
    def get_dirs(dir_type):
        dirs = dict(
            dao=os.path.join(Settings.SITE_ROOT_PATH, 'app/daos'),
            service=os.path.join(Settings.SITE_ROOT_PATH, 'app/services'),
            handler=os.path.join(Settings.SITE_ROOT_PATH, 'app/handlers'),
            view=os.path.join(Settings.SITE_ROOT_PATH, 'app/views')
        )
        dir_str_long = dirs[dir_type]
        dir_str_shot = ""
        return dir_str_long

    def get_config_schema_name(self):
        return self.database_config["database"]

    @staticmethod
    def get_edit_types():
        """所有编辑类型关键字

        :return:
        """
        return ("input", "text", "radio", "checkbox", "select", "date", "datetime", "time")

    @staticmethod
    def get_sql_edit_type(data_type):
        """数据库类型默认编辑类型

        :return:
        """
        types_map = dict(
            datetime="datetime",
            smallinteger="input",
            numeric="input",
            unicodetext="text",
            varchar="input",
            char="input",
            pickletype="input",
            bigint="input",
            unicode="input",
            binary="input",
            enum="input",
            date="date",
            int="input",
            interval="input",
            time="time",
            text="text",
            float="input",
            largebinary="input",
            tinyint="radio")
        if data_type in types_map:
            return types_map[data_type]
        else:
            return "input"


    @staticmethod
    def get_where_types():
        return ("==", "!=", "llike", "rlike", "like", "between")

    @staticmethod
    def get_first_word(word_str):
        """获取第一个特殊符号（非数字 字母 中文）前所有字符，待匹配字符为unicode
        用于数据库注释中获取字段中文名

        :param word_str:
        :return:
        """
        r = re.compile(ur'[\w]*[\u4E00-\u9FA5]*[\w]*')  # 这个要加上ur
        s_match = r.findall(word_str)
        if s_match and len(s_match) > 0:
            return s_match[0]
        return ""

    @staticmethod
    def get_column_length(column_type):
        """获取数据库字段长度

        :param column_type: 数据库字段类型（长度）
        :return: 字段长度
        """
        pattern = re.compile("\w*\((\d*)\)w*")
        res = pattern.search(column_type)
        if res is None:
            return None
        else:
            return res.groups()[0]

    @staticmethod
    def get_sql_a_type(sql_type):
        """根据数据库字段类型获取对应的SQLA数据类型
            这个类型对应还有待完善

        :param sql_type:数据库字段类型
        :return:SQLA数据类型字符串
        """
        types_map = dict(
            datetime="DateTime",
            smallinteger="SmallInteger",
            numeric="Numeric",
            unicodetext="UnicodeText",
            varchar="String",
            char="String",
            pickletype="PickleType",
            bigint="BigInteger",
            unicode="Unicode",
            binary="Binary",
            enum="Enum",
            date="Date",
            int="Integer",
            interval="Interval",
            time="Time",
            text="Text",
            float="Float",
            largebinary="LargeBinary",
            tinyint="Boolean")

        if sql_type in types_map:
            return types_map[sql_type]
        else:
            return None

    @staticmethod
    def get_model_name(table_name):
        """将‘user_categories’ 转换成‘UserCategory’,用作数据库表名转换成对应的实体名

        :param table_name: 需要传入的表名
        :return:
        """
        model_name = inflection.singularize(inflection.camelize(table_name))
        return model_name

    @staticmethod
    def get_all_sql_a_type(columns):
        """获取指定columns中所有的sqlA类型

        :param columns:
        :return:
        """
        sql_a_types = set()
        for col in columns:
            # 过滤掉不存在类型，以及默认字段类型
            if col["sql_a_type"] and col["column_name"] not in ("id", "created_at", "updated_at", "is_deleted"):
                sql_a_types.add(col["sql_a_type"])
        return sql_a_types

    @staticmethod
    def get_all_mixin(columns):
        """获取指定columns中所有的 mixin

        :param columns:
        :return:
        """
        mixins = dict()
        for col in columns:
            col_name = col["column_name"]
            if col_name == "id":
                mixins.setdefault("id", "IdMixin")
            if col_name == "created_at":
                mixins.setdefault("created_at", "CreatedAtMixin")
            if col_name == "updated_at":
                mixins.setdefault("updated_at", "UpdatedAtMixin")
            if col_name == "is_deleted":
                mixins.setdefault("is_deleted", "IsDeletedMixin")
        return mixins

    @staticmethod
    def get_sys_user_name():
        """获取当前系统用户名

        :return:
        """
        return getpass.getuser()


class GenerateFileService(object):
    """
    生成文件通用服务 准备模版参数，调用模版生成字符串，读写文件等功能
    """

    def __init__(self, table_name, columns=None):
        self.table_name = table_name
        self.dbm = DBMessage()
        self.namespace = self.dbm.get_namespace(self.table_name)
        if columns is not None:
            self.namespace.update(dict(columns=columns))
        self.template_path = os.path.join(os.path.dirname(__file__), u"templates")
        self.templates = dict(dao="dao_template.txt",
                              service="service_template.txt",
                              handler="handler_template.txt",
                              list_page="list_page_template.txt",
                              add_edit_page="add_edit_page_template.txt",
                              detail_page="detail_page_template.txt",
                              route="route_template.txt"
                              )
    def get_dao_string(self):
        template_file_name = self.templates["dao"]
        return MyTemplate.get_template_string(self.template_path, template_file_name, self.namespace)

    def get_service_string(self):
        template_file_name = self.templates["service"]
        return MyTemplate.get_template_string(self.template_path, template_file_name, self.namespace)

    def get_handler_string(self):
        template_file_name = self.templates["handler"]
        return MyTemplate.get_template_string(self.template_path, template_file_name, self.namespace)

    def get_route_string(self):
        template_file_name = self.templates["route"]
        return MyTemplate.get_template_string(self.template_path, template_file_name, self.namespace)

    def get_list_page_string(self):
        template_file_name = self.templates["list_page"]
        list_page_str = MyTemplate.get_template_string(self.template_path, template_file_name, self.namespace)
        list_page_str = list_page_str.replace("}&}", "}}")
        return list_page_str

    def get_add_edit_page_string(self):
        template_file_name = self.templates["add_edit_page"]
        add_edit_page_str = MyTemplate.get_template_string(self.template_path, template_file_name, self.namespace)
        add_edit_page_str = add_edit_page_str.replace("}&}", "}}")
        return add_edit_page_str

    def get_detail_page_string(self):
        template_file_name = self.templates["detail_page"]
        detail_page_str = MyTemplate.get_template_string(self.template_path, template_file_name, self.namespace)
        detail_page_str = detail_page_str.replace("}&}", "}}")
        return detail_page_str


if __name__ == "__main__":
    gfs = GenerateFileService(table_name="tests")
    print gfs.get_dao_string()
    # print gfs.get_service_string()
    # print gfs.get_handler_string()
    # print gfs.get_route_string()
    # print gfs.get_list_page_string()
    # print gfs.get_add_edit_page_string()
    # print gfs.get_detail_page_string()


