#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import inflection
from app.commons.generate.generate_code_service import GenerateFileService

args = sys.argv
if __name__ == "__main__":
    """ 数据库注释格式约定:第一行:名称+特殊字符(空格等)+其他注释信息
                          第二行:约定关键字
    数据库注释关键字
    编辑类型关键字:("input", "text", "radio", "checkbox", "select", "date", "datetime")
    条件查询关键字:("==", "!=", "llike", "rlike", "like", "between")
    条件查询排序关键字:("asc", "desc")
    字段查询关键字:("get_by", "gets_by")
    下拉类型:全大写字符串
    """
    # table_name = "tests"

    table_name = args[1]
    table_name = table_name[table_name.find("=") + 1:]
    gen_file = args[2]
    gen_file = gen_file[gen_file.find("=") + 1:]

    gfs = GenerateFileService(table_name=table_name)
    dao_str = gfs.get_dao_string()
    service_str = gfs.get_service_string()
    handler_str = gfs.get_handler_string()
    list_page_str = gfs.get_list_page_string()
    add_edit_page_str = gfs.get_add_edit_page_string()
    detail_page_str = gfs.get_detail_page_string()
    dao_file_path = os.path.join(os.path.dirname(__file__), u"templates")
    current_path = os.path.dirname(__file__)
    app_path = current_path[:current_path.find("commons/")]
    sing_table_name = inflection.singularize(table_name)
    if gen_file == "dao" or not gen_file or gen_file == "all":
        dao_file_name = sing_table_name + "_dao.py"
        dao_file_path = os.path.join(app_path, u"daos/" + dao_file_name)
        f = open(dao_file_path, 'w')
        f.write(dao_str)
        print dao_file_path

    if gen_file == "service" or not gen_file or gen_file == "all":
        service_file_name = sing_table_name + "_service.py"
        service_file_path = os.path.join(app_path, u"services/" + service_file_name)
        f = open(service_file_path, 'w')
        f.write(service_str)
        print service_file_path

    if gen_file == "handler" or not gen_file or gen_file == "all":
        handler_file_name = sing_table_name + ".py"
        handler_file_path = os.path.join(app_path, u"handlers/" + handler_file_name)
        f = open(handler_file_path, 'w')
        f.write(handler_str)
        print handler_file_path

    if not os.path.exists(os.path.join(app_path, u"views/" + sing_table_name)):
        os.mkdir(os.path.join(app_path, u"views/" + sing_table_name))
    if gen_file == "list" or not gen_file or gen_file == "all":
        list_page_file_name = table_name + ".html"
        list_page_file_path = os.path.join(app_path, u"views/" + sing_table_name + "/" + list_page_file_name)
        f = open(list_page_file_path, 'w')
        f.write(list_page_str)
        print list_page_file_path

    if gen_file == "add" or not gen_file or gen_file == "all":
        add_edit_page_file_name = sing_table_name + ".html"
        add_edit_page_file_path = os.path.join(app_path, u"views/" + sing_table_name + "/" + add_edit_page_file_name)
        f = open(add_edit_page_file_path, 'w')
        f.write(add_edit_page_str)
        print add_edit_page_file_path

    if gen_file == "detail" or not gen_file or gen_file == "all":
        detail_page_file_name = sing_table_name + "_detail.html"
        detail_page_file_path = os.path.join(app_path, u"views/" + sing_table_name + "/" + detail_page_file_name)
        f = open(detail_page_file_path, 'w')
        f.write(detail_page_str)
        print detail_page_file_path
    print gfs.get_route_string()

