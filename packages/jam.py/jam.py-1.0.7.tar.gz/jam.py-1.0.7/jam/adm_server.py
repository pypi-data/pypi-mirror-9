# -*- coding: utf-8 -*-

import os, os.path
import cPickle
import hashlib
import datetime
import zipfile
import shutil
import traceback

from third_party.jsparser import parse, SyntaxError_

import common
from server_classes import *
import lang.langs as langs

task = AdminServerTask('admin', u'Administrator', 'adm_main.ui', 'adm_edit.ui', common.SQLITE, db_database='admin.sqlite')

def read_setting():
    sql = 'SELECT '
    keys = common.DEFAULT_SETTINGS.keys()
    for key in keys:
        sql += 'F_%s, ' % key
    sql = sql[:-2]
    sql += ' FROM SYS_PARAMS'
    connection, (rec, error) = execute_sql(task.db_type, \
        task.db_database, task.db_user, task.db_password,
        task.db_host, task.db_port, task.db_encoding, None, sql, result_set='ONE')
    common.SETTINGS = {}
    for i, key in enumerate(keys):
        setting_type = type(common.DEFAULT_SETTINGS[key])
        try:
            if rec[i] is None:
                common.SETTINGS[key] = common.DEFAULT_SETTINGS[key]
            else:
                common.SETTINGS[key] = setting_type(rec[i])
        except:
            common.SETTINGS[key] = common.DEFAULT_SETTINGS[key]
    for key in common.SETTINGS.keys():
        common.__dict__[key] = common.SETTINGS[key]


def write_setting():
    sql = 'UPDATE SYS_PARAMS SET '
    params = []
    keys = common.DEFAULT_SETTINGS.keys()
    for key in keys:
        value = common.SETTINGS[key]
        setting_type = type(common.DEFAULT_SETTINGS[key])
        if setting_type == bool:
            if value:
                value = 1
            else:
                value = 0
        if setting_type == str:
            sql += 'F_%s="%s", ' % (key, value)
        else:
            sql += 'F_%s=%s, ' % (key, value)
    sql = sql[:-2]
    connection, (rec, error) = execute_sql(task.db_type, \
        task.db_database, task.db_user, task.db_password,
        task.db_host, task.db_port, task.db_encoding, None, sql)

read_setting()
task.task_con_pool_size = common.SETTINGS['CON_POOL_SIZE']
task.safe_mode = common.SETTINGS['SAFE_MODE']
task.language = common.SETTINGS['LANGUAGE']
task.item_caption = task.lang['admin']

sys_catalogs = ServerGroup(task, 'catalogs', task.lang['catalogs'], 'adm_catalogs_show.ui', 'adm_edit.ui')
sys_tables = ServerGroup(task, 'tables', task.lang['tables'], 'adm_table_show.ui', 'adm_edit.ui', visible=False)

sys_params = sys_catalogs.add_ref('sys_params', u'', 'SYS_PARAMS')

sys_params.add_field(common.SYS, 'id', u'ID', common.INTEGER, visible=False, edit_visible=False)
sys_params.add_field(common.SYS, 'deleted', u'Deleted flag', common.INTEGER, visible=False, edit_visible=False)
sys_params.add_field(common.DATA, 'f_safe_mode', task.lang['safe_mode'], common.BOOLEAN)
sys_params.add_field(common.DATA, 'f_debugging', 'debugging', common.BOOLEAN, edit_visible=False)
sys_params.add_field(common.DATA, 'f_log_file', u'Log file', common.TEXT, size = 30)
sys_params.add_field(common.DATA, 'f_con_pool_size', u'Connection pool size', common.INTEGER, required=True)#, edit_visible=True)
sys_params.add_field(common.DATA, 'f_decimal_point', u'Decimal point', common.TEXT, size = 1)
sys_params.add_field(common.DATA, 'f_mon_decimal_point', u'Monetory decimal point', common.TEXT, size = 1)
sys_params.add_field(common.DATA, 'f_mon_thousands_sep', u'Monetory thousands separator', common.TEXT, size = 3)
sys_params.add_field(common.DATA, 'f_currency_symbol', u'Currency symbol', common.TEXT, size = 10)
sys_params.add_field(common.DATA, 'f_frac_digits', u'Number of fractional digits', common.INTEGER)
sys_params.add_field(common.DATA, 'f_p_cs_precedes', u'Currency symbol precedes the value (positive values)', common.BOOLEAN)
sys_params.add_field(common.DATA, 'f_n_cs_precedes', u'Currency symbol precedes the value (negative values)', common.BOOLEAN)
sys_params.add_field(common.DATA, 'f_p_sep_by_space', u'Currency symbol is separated by a space (positive values)', common.BOOLEAN)
sys_params.add_field(common.DATA, 'f_n_sep_by_space', u'Currency symbol is separated by a space (negative values)', common.BOOLEAN)
sys_params.add_field(common.DATA, 'f_positive_sign', u'Symbol for a positive monetary value', common.TEXT, size = 1)
sys_params.add_field(common.DATA, 'f_negative_sign', u'Symbol for a negative monetary value', common.TEXT, size = 1)
sys_params.add_field(common.DATA, 'f_p_sign_posn', u'The position of the sign (positive values)', common.INTEGER)
sys_params.add_field(common.DATA, 'f_n_sign_posn', u'The position of the sign (negative values)', common.INTEGER)
sys_params.add_field(common.DATA, 'f_d_fmt', u'Date format string', common.TEXT, size = 30)
sys_params.add_field(common.DATA, 'f_d_t_fmt', u'Date and time format string', common.TEXT, size = 30)
sys_params.add_field(common.SYS, 'f_language', task.lang['language'], common.INTEGER, value_list=langs.LANGUAGE, edit_visible=False)
sys_params.add_field(common.SYS, 'f_author', task.lang['author'], common.TEXT, size = 30, edit_visible=False)

sys_items = sys_catalogs.add_ref('sys_items', u'', 'SYS_ITEMS')

sys_items.add_field(common.SYS, 'id', u'ID', common.INTEGER, visible=True, edit_visible=False)
sys_items.add_field(common.SYS, 'deleted', u'Deleted flag', common.INTEGER, visible=False, edit_visible=False)
sys_items.add_field(common.SYS, 'parent', u'Parent id', common.INTEGER, visible=False, edit_visible=False)
sys_items.add_field(common.SYS, 'task_id', u'Task id', common.INTEGER, visible=False, edit_visible=False)
sys_items.add_field(common.SYS, 'type_id', u'Type id', common.INTEGER, visible=False, edit_visible=False)
sys_items.add_field(common.SYS, 'table_id', u'Table id', common.INTEGER, visible=False, edit_visible=False)
sys_items.add_field(common.SYS, 'has_children', u'Has_children', common.BOOLEAN, visible=False, edit_visible=False)
sys_items.add_field(common.SYS, 'f_index', u'Index', common.INTEGER, visible=False, edit_visible=False)
sys_items.add_field(common.DATA, 'f_name', task.lang['caption'], common.TEXT, required=True, expand=True, size = 200)
sys_items.add_field(common.DATA, 'f_item_name', task.lang['name'], common.TEXT, required=True, expand=True, size = 200)
sys_items.add_field(common.DATA, 'f_table_name', task.lang['table_name'], common.TEXT, size = 200)
sys_items.add_field(common.DATA, 'f_view_template', task.lang['view_template'], common.TEXT, size = 200)
sys_items.add_field(common.DATA, 'f_edit_template', task.lang['edit_template'], common.TEXT, size = 200)
sys_items.add_field(common.DATA, 'f_filter_template', task.lang['filter_template'], common.TEXT, size = 200)
sys_items.add_field(common.DATA, 'f_visible', task.lang['visible'], common.BOOLEAN)
sys_items.add_field(common.DATA, 'f_soft_delete', u'Soft delete', common.BOOLEAN)
sys_items.add_field(common.DATA, 'f_client_module', task.lang['client_module'], common.BLOB, visible=False, edit_visible=False)
sys_items.add_field(common.DATA, 'f_web_client_module', task.lang['web_client_module'], common.BLOB, visible=False, edit_visible=False)
sys_items.add_field(common.DATA, 'f_server_module', task.lang['server_module'], common.BLOB, visible=False, edit_visible=False)
sys_items.add_field(common.DATA, 'f_info', u'Info', common.BLOB, visible=False, edit_visible=False)

sys_items.add_filter('id', u'ID', 'id', common.FILTER_EQ, visible=False)
sys_items.add_filter('not_id', u'ID', 'id', common.FILTER_NE, visible=False)
sys_items.add_filter('parent', u'Parent', 'parent', common.FILTER_EQ, visible=False)
sys_items.add_filter('task_id', u'Task', 'task_id', common.FILTER_EQ, visible=False)
sys_items.add_filter('type_id', u'Type', 'type_id', common.FILTER_IN, visible=False)
sys_items.add_filter('table_id', u'Type', 'table_id', common.FILTER_EQ, visible=False)
sys_items.add_filter('type_id_gt', u'Type', 'type_id', common.FILTER_GT, visible=False)

sys_tasks = sys_catalogs.add_ref('sys_tasks', u'', 'SYS_TASKS')
sys_tasks.add_field(common.SYS, 'id', u'Record ID', common.INTEGER, visible=False, edit_visible=False)
sys_tasks.add_field(common.SYS, 'deleted', u'Deleted flag', common.INTEGER, visible=False, edit_visible=False)
sys_tasks.add_field(common.SYS, 'task_id', u'Task ID', common.INTEGER, visible=False, edit_visible=False)
sys_tasks.add_field(common.SYS, 'f_manual_update', u'DB manual update', common.BOOLEAN, visible=False, edit_visible=False)
sys_tasks.add_field(common.SYS, 'f_db_type', task.lang['db_type'], common.INTEGER, value_list=common.DB_TYPE)
sys_tasks.add_field(common.SYS, 'f_alias', task.lang['alias'], common.TEXT, size = 30)
sys_tasks.add_field(common.SYS, 'f_login', task.lang['login'], common.TEXT, size = 30)
sys_tasks.add_field(common.SYS, 'f_password', task.lang['password'], common.TEXT, size = 30)
sys_tasks.add_field(common.SYS, 'f_host', u'Host', common.TEXT, size = 30)
sys_tasks.add_field(common.SYS, 'f_port', u'Port', common.TEXT, size = 30)
sys_tasks.add_field(common.SYS, 'f_encoding', u'Encoding', common.TEXT, size = 10)

sys_tasks.add_filter('task_id', u'Task ID', 'task_id', common.FILTER_EQ, visible=False)

sys_fields = sys_tables.add_table('sys_fields', task.lang['fields'], 'SYS_FIELDS')

sys_fields.add_field(common.SYS, 'id', u'Record ID', common.INTEGER, visible=False, edit_visible=False)
sys_fields.add_field(common.SYS, 'deleted', u'Deleted flag', common.INTEGER, visible=False, edit_visible=False)
sys_fields.add_field(common.SYS, 'owner_id', u'Owner ID', common.INTEGER, visible=False, edit_visible=False)
sys_fields.add_field(common.SYS, 'owner_rec_id', u'Owner record ID', common.INTEGER, visible=False, edit_visible=False)
sys_fields.add_field(common.SYS, 'task_id', u'Task ID', common.INTEGER, visible=False, edit_visible=False)
sys_fields.add_field(common.DATA, 'f_name',         task.lang['caption'],      common.TEXT, True, expand=True, size = 30)
sys_fields.add_field(common.DATA, 'f_field_name',   task.lang['name'],          common.TEXT, True, expand=True, size = 30)
sys_fields.add_field(common.DATA, 'f_data_type',    task.lang['data_type'],          common.INTEGER, True,  False, value_list=common.FIELD_TYPES)
sys_fields.add_field(common.DATA, 'f_size',         task.lang['size'],      common.INTEGER)
sys_fields.add_field(common.DATA, 'f_object',       task.lang['object'],       common.INTEGER, False, sys_items, 'f_item_name')#, word_wrap=True)
sys_fields.add_field(common.DATA, 'f_object_field',   task.lang['object_field'],  common.INTEGER, False, sys_fields, 'f_field_name')#, word_wrap=True)
sys_fields.add_field(common.DATA, 'f_master_field', task.lang['master_field'],    common.INTEGER, False, sys_fields, 'f_field_name')#, word_wrap=True)
sys_fields.add_field(common.DATA, 'f_required',     task.lang['required'],        common.BOOLEAN)
sys_fields.add_field(common.DATA, 'f_calculated',   task.lang['calculated'],       common.BOOLEAN, visible=False, edit_visible=False)
sys_fields.add_field(common.DATA, 'f_default',      task.lang['default'],         common.BOOLEAN)
sys_fields.add_field(common.DATA, 'f_read_only',    task.lang['read_only'],       common.BOOLEAN)
sys_fields.add_field(common.DATA, 'f_alignment',    task.lang['alignment'],       common.INTEGER, value_list=common.ALIGNMENT)

sys_fields.add_filter('id', u'ID', 'id', common.FILTER_EQ, visible=False)
sys_fields.add_filter('owner_rec_id', u'Owner record ID', 'owner_rec_id', common.FILTER_IN, visible=False)
sys_fields.add_filter('task_id', u'Task', 'task_id', common.FILTER_EQ, visible=False)
sys_fields.add_filter('not_id', u'not ID', 'id', common.FILTER_NE, visible=False)
sys_fields.add_filter('object', u'Object ID', 'f_object', common.FILTER_EQ, visible=False)
sys_fields.add_filter('master_field_is_null', u'Master field', 'f_master_field', common.FILTER_ISNULL, visible=False)
sys_fields.add_filter('master_field', u'Master field', 'f_master_field', common.FILTER_EQ, visible=False)

item_fields = sys_items.add_detail(sys_fields)
item_fields.edit_template = 'adm_edit.ui'

sys_report_params = sys_tables.add_table('sys_report_params', task.lang['report_params'], 'SYS_REPORT_PARAMS', view_template='adm_filters_show.ui')

sys_report_params.add_field(common.SYS, 'id', u'Record ID', common.INTEGER, visible=False, edit_visible=False)
sys_report_params.add_field(common.SYS, 'deleted', u'Deleted flag', common.INTEGER, visible=False, edit_visible=False)
sys_report_params.add_field(common.SYS, 'owner_id', u'Owner ID', common.INTEGER, visible=False, edit_visible=False)
sys_report_params.add_field(common.SYS, 'owner_rec_id', u'Owner record ID', common.INTEGER, visible=False, edit_visible=False)
sys_report_params.add_field(common.SYS, 'task_id', u'Task ID', common.INTEGER, visible=False, edit_visible=False)
sys_report_params.add_field(common.DATA, 'f_index',        task.lang['index'],   common.INTEGER, visible=False, edit_visible=False)
sys_report_params.add_field(common.DATA, 'f_name',         task.lang['caption'],      common.TEXT, True, expand=True, size = 30)
sys_report_params.add_field(common.DATA, 'f_param_name',   task.lang['name'],          common.TEXT, True, expand=True, size = 30)
sys_report_params.add_field(common.DATA, 'f_data_type',    task.lang['data_type'],          common.INTEGER, True,  False, value_list=common.FIELD_TYPES)
sys_report_params.add_field(common.DATA, 'f_size',         task.lang['size'],  common.INTEGER, visible=False, edit_visible=False)
sys_report_params.add_field(common.DATA, 'f_object',       task.lang['object'],       common.INTEGER, False, sys_items, 'f_name')
sys_report_params.add_field(common.DATA, 'f_object_field',   task.lang['field'],  common.INTEGER, False, sys_fields, 'f_field_name')
sys_report_params.add_field(common.DATA, 'f_required',     task.lang['required'],        common.BOOLEAN)
sys_report_params.add_field(common.DATA, 'f_visible',      task.lang['visible'],    common.BOOLEAN)
sys_report_params.add_field(common.DATA, 'f_alignment',    task.lang['alignment'],       common.INTEGER, value_list=common.ALIGNMENT)

sys_report_params.add_filter('owner_rec_id', u'Owner rec ID ', 'owner_rec_id', common.FILTER_EQ, visible=False)
sys_report_params.add_filter('task_id', u'Task ID', 'task_id', common.FILTER_EQ, visible=False)

sys_indices = sys_tables.add_table('sys_indices', task.lang['indices'], 'SYS_INDICES')#, edit_template='adm_fields_editor.ui')

sys_indices.add_field(common.SYS, 'id', u'Record ID', common.INTEGER, visible=False, edit_visible=False)
sys_indices.add_field(common.SYS, 'deleted', u'Deleted flag', common.INTEGER, visible=False, edit_visible=False)
sys_indices.add_field(common.SYS, 'owner_id', u'Owner ID', common.INTEGER, visible=False, edit_visible=False)
sys_indices.add_field(common.SYS, 'owner_rec_id', u'Owner record ID', common.INTEGER, visible=False, edit_visible=False)
sys_indices.add_field(common.SYS, 'task_id', u'Task ID', common.INTEGER, visible=False, edit_visible=False)
sys_indices.add_field(common.DATA, 'f_index_name', task.lang['index_name'], common.TEXT, True, word_wrap=True, expand=True, size = 100)
sys_indices.add_field(common.DATA, 'descending', u'Descending', common.BOOLEAN)
sys_indices.add_field(common.DATA, 'f_foreign_index', u'Foreign Index', common.BOOLEAN, visible=False, edit_visible=False)
sys_indices.add_field(common.DATA, 'f_foreign_field', u'Foreign Field', common.INTEGER, False, item_fields, 'f_field_name', visible=False, edit_visible=False, word_wrap=True, expand=True)
sys_indices.add_field(common.DATA, 'f_fields', task.lang['fields'], common.BLOB, visible=False, edit_visible=False)

sys_indices.add_filter('id', u'ID', 'id', common.FILTER_EQ, visible=False)
sys_indices.add_filter('owner_rec_id', u'Owner record ID', 'owner_rec_id', common.FILTER_EQ, visible=False)
sys_indices.add_filter('task_id', u'Task ID', 'task_id', common.FILTER_EQ, visible=False)
sys_indices.add_filter('foreign_index', u'Owner record ID', 'f_foreign_index', common.FILTER_EQ, visible=False)

sys_filters = sys_tables.add_table('sys_filters', task.lang['filters'], 'SYS_FILTERS', view_template='adm_filters_show.ui')

sys_filters.add_field(common.SYS, 'id', u'Record ID', common.INTEGER, visible=False, edit_visible=False)
sys_filters.add_field(common.SYS, 'deleted', u'Deleted flag', common.INTEGER, visible=False, edit_visible=False)
sys_filters.add_field(common.SYS, 'owner_id', u'Owner ID', common.INTEGER, visible=False, edit_visible=False)
sys_filters.add_field(common.SYS, 'owner_rec_id', u'Owner record ID', common.INTEGER, visible=False, edit_visible=False)
sys_filters.add_field(common.SYS, 'task_id', u'Task ID', common.INTEGER, visible=False, edit_visible=False)
sys_filters.add_field(common.DATA, 'f_index',     task.lang['index'],   common.INTEGER, visible=False, edit_visible=False)
sys_filters.add_field(common.DATA, 'f_field',     task.lang['field'],    common.INTEGER, False, sys_fields, 'f_field_name', expand=True)
sys_filters.add_field(common.DATA, 'f_name',      task.lang['caption'], common.TEXT, True, expand=True)
sys_filters.add_field(common.DATA, 'f_filter_name',  task.lang['name'],     common.TEXT, True, expand=True)
sys_filters.add_field(common.DATA, 'f_data_type', task.lang['data_type'], common.INTEGER, False,  visible=False, edit_visible=False, value_list=common.FIELD_TYPES)
sys_filters.add_field(common.DATA, 'f_type',      task.lang['filter_type'], common.INTEGER, False, value_list=common.FILTER_STRING)
sys_filters.add_field(common.DATA, 'f_visible',   task.lang['visible'],    common.BOOLEAN)

sys_filters.add_filter('owner_rec_id', u'Owner rec ID ', 'owner_rec_id', common.FILTER_EQ, visible=False)
sys_filters.add_filter('task_id', u'Task ID', 'task_id', common.FILTER_EQ, visible=False)

sys_users = sys_catalogs.add_ref('sys_users', task.lang['users'], 'SYS_USERS')
sys_roles = sys_catalogs.add_ref('sys_roles', task.lang['roles'], 'SYS_ROLES', view_template = 'adm_roles.ui')

sys_users.add_field(common.SYS, 'id', u'Record ID', common.INTEGER, visible=False, edit_visible=False)
sys_users.add_field(common.SYS, 'deleted', u'Deleted flag', common.INTEGER, visible=False, edit_visible=False)
sys_users.add_field(common.DATA, 'f_active', task.lang['active'], common.BOOLEAN, visible=False, edit_visible=False)
sys_users.add_field(common.DATA, 'f_act_date', task.lang['date'], common.DATETIME, visible=False, edit_visible=False)
sys_users.add_field(common.DATA, 'f_name', task.lang['name'], common.TEXT, required=True, expand=True, size=30)
sys_users.add_field(common.DATA, 'f_login', task.lang['login'], common.TEXT, required=True, expand=True, size=30)
sys_users.add_field(common.DATA, 'f_password', task.lang['password'], common.TEXT, required=True, expand=True, size=30)
sys_users.add_field(common.DATA, 'f_role', task.lang['role'], common.INTEGER, True, sys_roles, 'f_name', expand=True)
sys_users.add_field(common.DATA, 'f_info', task.lang['info'], common.TEXT, size=100)
sys_users.add_field(common.DATA, 'f_admin', u'Admin', common.BOOLEAN)

sys_roles.add_field(common.SYS, 'id', u'ID', common.INTEGER, visible=True, edit_visible=False)
sys_roles.add_field(common.SYS, 'deleted', u'Deleted flag', common.INTEGER, visible=False, edit_visible=False)
sys_roles.add_field(common.DATA, 'f_name', task.lang['roles'], common.TEXT, required=True, expand=True, size=30)

sys_roles.add_filter('id', u'ID', 'id', common.FILTER_EQ, visible=False)

sys_privileges = sys_tables.add_table('sys_privileges', task.lang['privileges'], 'SYS_PRIVILEGES')

sys_privileges.add_field(common.SYS, 'id', u'Record ID', common.INTEGER, visible=False, edit_visible=False)
sys_privileges.add_field(common.SYS, 'deleted', u'Deleted flag', common.INTEGER, visible=False, edit_visible=False)
sys_privileges.add_field(common.SYS, 'owner_id', u'Owner ID', common.INTEGER, visible=False, edit_visible=False)
sys_privileges.add_field(common.SYS, 'owner_rec_id', u'Owner record ID', common.INTEGER, visible=False, edit_visible=False)
sys_privileges.add_field(common.SYS, 'item_id', task.lang['item'], common.INTEGER, False, sys_items, 'f_name', expand=True)
sys_privileges.add_field(common.SYS, 'f_can_view', task.lang['can_view'], common.BOOLEAN, editable=True)
sys_privileges.add_field(common.SYS, 'f_can_create', task.lang['can_create'], common.BOOLEAN, editable=True)
sys_privileges.add_field(common.SYS, 'f_can_edit', task.lang['can_edit'], common.BOOLEAN, editable=True)
sys_privileges.add_field(common.SYS, 'f_can_delete', task.lang['can_delete'], common.BOOLEAN, editable=True)

sys_privileges.add_filter('owner_rec_id', u'Owner record ID', 'owner_rec_id', common.FILTER_EQ, visible=False)

role_privileges = sys_roles.add_detail(sys_privileges)

def init_item(item, id_value, *order_by):
    item.ID = id_value
    item.soft_delete = False
    if hasattr(item, '_fields'):
        cur_field_id = 0
        for field in item._fields:
            field.alignment = common.get_alignment(field.data_type, field.lookup_item, field.value_list)
            field.ID = cur_field_id
            cur_field_id += 1
    if order_by:
        item.change_order(*order_by)

init_item(task, 0)
init_item(sys_users, 1, 'id')
init_item(sys_roles, 2, 'id')
init_item(sys_items, 3, 'type_id', 'f_index')
init_item(sys_fields, 4, 'f_field_name')
init_item(sys_filters, 5, 'f_index')
init_item(item_fields, 6, 'f_field_name')#'id')
init_item(sys_privileges, 7)
init_item(role_privileges, 8)
init_item(sys_tasks, 9)
init_item(sys_indices, 10, 'id')
init_item(sys_params, 11)
init_item(sys_report_params, 12, 'f_index')

def execute(task_id, sql, params=None):

    def db_info():
        tasks = task.sys_tasks.copy()
        tasks.filters.task_id.value = task_id
        tasks.open()
        return tasks.f_db_type.value, str(tasks.f_alias.value), str(tasks.f_login.value), \
            str(tasks.f_password.value), tasks.f_host.value, \
            tasks.f_port.value, tasks.f_encoding.value

    if task_id == 0:
        result_set, error = task.execute(sql, params)
        return error
    else:
        connection = None
        db_type, db_database, db_user, db_password, db_host, db_port, db_encoding = db_info()
        connection, (result_set, error) = execute_sql(db_type, \
            db_database, db_user, db_password, db_host, db_port,
            db_encoding, connection, sql, params)
        if connection:
            connection.rollback()
            connection.close()
        return error

def execute_select(task_id, sql, params=None):
    return task.execute_select(sql)

def get_privileges(role_id):
    result = {}
    privliges = sys_privileges.copy()
    privliges.filters.owner_rec_id.value = role_id
    privliges.open()
    for p in privliges:
        result[p.item_id.value] = \
            {
            'can_view': p.f_can_view.value,
            'can_create': p.f_can_create.value,
            'can_edit': p.f_can_edit.value,
            'can_delete': p.f_can_delete.value
            }
    return result

def get_roles():
    result = {}
    roles = sys_roles.copy()
    roles.open()
    for r in roles:
        result[r.id.value] = get_privileges(r.id.value)
    return result

def find_user(admin, login, password_hash=None):
    user_id = None
    user_info = {}
    users = sys_users.copy()
    users.open()
    for u in users:
        if u.f_login.value.strip() == login.strip():
            if password_hash is None or hashlib.md5(u.f_password.value).hexdigest() == psw_hash:
                if not admin or u.f_admin.value == admin:
                    user_id = u.id.value
                    user_info = {
                        'user_id': u.id.value,
                        'role_id': u.f_role.value,
                        'role_name': u.f_role.display_text,
                        'user_name': u.f_name.value
                    }
    return user_id, user_info
task.find_user = find_user

def login(log, psw_hash, admin):
    user_id = None
    user_info = {}
    users = sys_users.copy()
    users.open()
    if task.safe_mode:
        privileges = {}
        for u in users:
            if u.f_login.value.strip() == log.strip():
                if hashlib.md5(u.f_password.value).hexdigest() == psw_hash:
                    if not admin or u.f_admin.value == admin:
                        user_id = u.id.value
                        user_info = {
                            'user_id': u.id.value,
                            'role_id': u.f_role.value,
                            'role_name': u.f_role.display_text,
                            'user_name': u.f_name.value
                        }
    return user_id, user_info
task.login = login

def logout(user_id):
    users = sys_users.copy()
    users.open()
    for u in users:
        if u.id.value == user_id:
            u.edit()
            u.f_active.value = False
            u.f_act_date.value = None
            u.post()
            u.apply()

def get_tasks(id=None):
    copy = sys_items.copy()
    copy.filters.type_id.value = [common.TASK_TYPE]
    copy.open()
    result = []
    for rec in copy:
        result.append({'id': copy.id.value, 'caption': copy.f_name.value})
    return result

def create_task(server):
    it = sys_items.copy()
    it.filters.type_id.value = [common.TASK_TYPE]
    it.open()
    it_task = sys_tasks.copy()
    it_task.filters.task_id.value = it.id.value
    it_task.open()
    result = ServerTask(it.f_item_name.value, it.f_name.value, it.f_view_template.value,
        it.f_edit_template.value, it_task.f_db_type.value, it_task.f_alias.value,
        it_task.f_login.value, it_task.f_password.value, it_task.f_host.value,
        it_task.f_port.value, it_task.f_encoding.value, task.task_con_pool_size)
    result.ID = it.id.value
    load_task(result, server)
    return result

###############################################################################
#                                   load task                                 #
###############################################################################

def reload_task():
    if common.SETTINGS['DEBUGGING']:
        if task.server.task:
            load_task(task.server.task, task.server)

def load_task(target, server):

    def create_fields(item, parent_id):
        for rec in sys_fields:
            if sys_fields.owner_rec_id.value == parent_id:
                view_index = -1
                visible = False
                word_wrap = False
                expand = False
                editable = False
                for i, rec in enumerate(sys_items._view_list):
                    if sys_fields.id.value == rec[0]:
                        view_index = i
                        visible = True
                        word_wrap = rec[1]
                        expand = rec[2]
                        editable = rec[3]
                        break
                edit_visible = False
                edit_index = -1
                for i, rec in enumerate(sys_items._edit_list):
                    if sys_fields.id.value == rec[0]:
                        edit_index = i
                        edit_visible = True
                        break
                field = item.add_field(common.DATA,
                    sys_fields.f_field_name.value,
                    sys_fields.f_name.value,
                    sys_fields.f_data_type.value,
                    sys_fields.f_required.value,
                    sys_fields.f_object.value,
                    sys_fields.f_object_field.value,
                    visible,
                    view_index,
                    edit_visible,
                    edit_index,
                    sys_fields.f_read_only.value,
                    expand,
                    word_wrap,
                    sys_fields.f_size.value,
                    sys_fields.f_default.value,
                    sys_fields.f_calculated.value,
                    editable,
                    sys_fields.f_master_field.value)

                field.alignment = sys_fields.f_alignment.value
                field.ID = sys_fields.field_by_name('id').value
                field._view_index = view_index

    def create_filters(item, parent_id):
        for rec in sys_filters:
            if sys_filters.owner_rec_id.value == parent_id:
                item.add_filter(
                    sys_filters.f_filter_name.value,
                    sys_filters.f_name.value,
                    sys_filters.f_field.value,
                    sys_filters.f_type.value,
                    sys_filters.f_data_type.value,
                    sys_filters.f_visible.value)

    def create_params(item, parent_id):
        for params in sys_params:
            if sys_params.owner_rec_id.value == parent_id:
                item.add_param(params.f_name.value,
                        params.f_param_name.value,
                        params.f_data_type.value,
                        params.f_object.value,
                        params.f_object_field.value,
                        params.f_required.value,
                        params.f_visible.value,
                        params.f_alignment.value)

    def create_items(group, group_id, group_type_id):
        for rec in sys_items:
            if rec.parent.value == group_id:
                item = None
                add_item = None
                if group_type_id == common.CATALOGS_TYPE:
                    add_item = group.add_ref
                elif group_type_id == common.JOURNALS_TYPE:
                    add_item = group.add_journal
                elif group_type_id == common.TABLES_TYPE:
                    add_item = group.add_table
                elif group_type_id == common.REPORTS_TYPE:
                    add_item = group.add_report
                if add_item:
                    item = add_item(rec.f_item_name.value,
                        rec.f_name.value,
                        rec.f_table_name.value,
                        rec.f_visible.value,
                        rec.f_view_template.value,
                        rec.f_edit_template.value,
                        rec.f_filter_template.value,
                        rec.f_soft_delete.value)
                    if item:
                        item.ID = rec.id.value
                        item.client_code = rec.f_client_module.value
                        item.web_client_code = rec.f_web_client_module.value
                        item.server_code = rec.f_server_module.value
                        if group_type_id != common.REPORTS_TYPE:
                            common.load_interface(sys_items)
                            create_fields(item, group_id)
                            create_fields(item, rec.id.value)
                            item._order_by = sys_items._order_list
                            item.rep_ids = sys_items._reports_list
                            create_filters(item, group_id)
                            create_filters(item, rec.id.value)
                        else:
                            create_params(item, rec.id.value)
                            item.rep_ids = []

    def create_groups(parent):
        groups = []
        for rec in sys_items:
            if rec.id.value == parent:
                target.table_name = rec.f_table_name.value
                target.template = rec.f_view_template.value
                target.edit_template = rec.f_edit_template.value
                common.load_interface(sys_items)
                target.client_code = rec.f_client_module.value
                target.web_client_code = rec.f_web_client_module.value
                target.server_code = rec.f_server_module.value
            if rec.parent.value == parent:
                group = ServerGroup(target, rec.f_item_name.value, rec.f_name.value, rec.f_view_template.value,
                    rec.f_edit_template.value, rec.f_filter_template.value, rec.f_visible.value, rec.type_id.value)
                group.ID = rec.id.value
                group.client_code = rec.f_client_module.value
                group.web_client_code = rec.f_web_client_module.value
                group.server_code = rec.f_server_module.value
                groups.append((group, rec.id.value, rec.type_id.value))
        for group in groups:
             create_items(*group)

    def create_details():
        for it in sys_items:
            if it.table_id.value:
                item = target.item_by_ID(it.parent.value)
                table = target.item_by_ID(it.table_id.value)
                if item and table:
                    detail = item.add_detail(table)
                    detail.ID = it.id.value
                    detail.visible = it.f_visible.value
                    detail.view_template = it.f_view_template.value
                    detail.edit_template = it.f_edit_template.value
                    detail.filter_template = it.f_filter_template.value
                    detail.client_code = it.f_client_module.value
                    detail.web_client_code = it.f_web_client_module.value
                    detail.server_code = it.f_server_module.value
                    detail.item_type = common.ITEM_TYPES[detail.item_type_id - 1]
                    common.load_interface(sys_items)
                    detail._order_by = sys_items._order_list
                    for field in detail._fields:
                        field.view_index = -1
                        field.view_visible = False
                        field.word_wrap = False
                        field.expand = False
                        field.editable = False
                        for i, rec in enumerate(sys_items._view_list):
                            if field.ID == rec[0]:
                                field.view_index = i
                                field.view_visible = True
                                field.word_wrap = rec[1]
                                field.expand = rec[2]
                                field.editable = rec[3]
                                break
                        field.edit_visible = False
                        field.edit_index = -1
                        for i, rec in enumerate(sys_items._edit_list):
                            if field.ID == rec[0]:
                                field.edit_index = i
                                field.edit_visible = True
                                break

    def process_reports():

        def add_reports(item):
            item.reports = []
            for rep_id in item.rep_ids:
                report = target.item_by_ID(rep_id[0])
                if report:
                    item.reports.append(report)

        for group in target.items:
            for item in group.items:
                add_reports(item)

    target.items = []
    sys_fields = task.sys_fields
    sys_fields.open()
    sys_filters = task.sys_filters
    sys_filters.open()
    sys_params = task.sys_report_params
    sys_params.open()
    sys_items = task.sys_items
    sys_items.details_active = False
    sys_items.open()
    create_groups(target.ID)
    create_details()
    process_reports()
    target.bind_items()
    target.compile_all()
    target.language = task.language

    target.server = server
    target.admin = server.admin
    target.admin.task = target

    if target.on_created:
        target.on_created(target)

#
###############################################################################
#                                 task                                        #
###############################################################################

def server_check_connection(task, db_type, database, user,
    password, host, port, encoding):
    result = False
    error = 'Fill in DB type entry.'
    if not host:
        host = 'localhost'
    if db_type:
        result = True
        error = ''
        try:
            if db_type == common.POSTGRESQL:
                import psycopg2
                connection = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
            if db_type == common.MYSQL:
                import MySQLdb
                connection = MySQLdb.connect(db=database, user=user, passwd=password, host=host)
            elif db_type == common.FIREBIRD:
                import fdb
                connection = fdb.connect(host=host, database=database, user=user, password=password, charset=encoding)
            elif db_type == common.SQLITE:
                if database == '':
                    database = None
                import sqlite3
                connection = sqlite3.connect(database)
            if connection:
                connection.close()
        except Exception, e:
            print e
            result = False
            error = e.message
    return result, error
task.register(server_check_connection)

def server_create_task(task, caption, name, db_type, database, user,
    password, host, port, encoding):

    def update_buttons_text(file_name):
        with open(file_name, 'r') as f:
            data = f.read()
        start = data.find('__$_')
        label_list = []
        while start > -1:
            end = data.find('_$__', start)
            if end != -1:
                search = data[start:end+4]
                replace = data[start +4:end]
                label_list.append((search, replace))
            start = data.find('__$_', end)
        for search, replace in label_list:
            try:
                data = data.replace(search, task.lang[replace])
            except:
                pass
        with open(file_name, 'w') as f:
            f.write(data)

    task.init_locale()
    write_setting()
    read_setting()
    check_result = server_check_connection(task, db_type, database,
        user, password, host, port, encoding)
    if not check_result[0]:
        return False, task.lang['can_not_connect'] % check_result[1]
    items = task.sys_items.copy()
    items.open()
    for it in items:
        it.edit()
        try:
            it.f_name.value = task.lang[it.f_item_name.value]
        except:
            pass
        it.post()
    it.apply()
    update_buttons_text('index.html')
    ui_dir = 'ui'
    for file_name in os.listdir(ui_dir):
        update_buttons_text(os.path.join(ui_dir, file_name))
    return True, ''
task.register(server_create_task)

def server_update_has_children(task):
    has_children = {}
    items = task.sys_items.copy(handlers=False)
    items.open()
    for it in items:
        has_children[it.parent.value] = True
        if it.type_id.value in (common.ROOT_TYPE, common.USERS_TYPE, common.ROLES_TYPE,
            common.TASKS_TYPE, common.CATALOGS_TYPE,
            common.JOURNALS_TYPE, common.TABLES_TYPE, common.REPORTS_TYPE):
            has_children[it.id.value] = True
    for it in items:
        if not has_children.get(it.id.value):
            has_children[it.id.value] = False
        if it.has_children.value != has_children.get(it.id.value):
            it.edit()
            it.has_children.value = has_children.get(it.id.value)
            it.post()
    items.apply()
task.register(server_update_has_children)

def server_export_task(task, task_id):

    def add_item(item):
        table = item.copy(handlers=False)
        table.open()
        result[item.item_name] = table.records

    result = {}
    add_item(sys_items)
    add_item(sys_fields)
    add_item(sys_indices)
    add_item(sys_filters)
    add_item(sys_report_params)
    add_item(sys_roles)
    add_item(sys_params)
    add_item(sys_privileges)

    task_file = 'task.dat'
    file_name = 'task.zip'
    zip_file_name = os.path.join(task.work_dir, file_name)
    try:
        with open(task_file, 'w') as f:
            cPickle.dump(result, f)
        zip_file = zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED)
        zip_file.write(task_file)
        zip_file.write('index.html')
        zip_file.write('server.py')
        zip_file.write('admin.py')
        zip_file.write('client.py')
        zip_file.write('main.py')
        common.zip_dir('jam', zip_file, exclude_ext=['.pyc'])
        common.zip_dir('js', zip_file)
        common.zip_dir('css', zip_file)
        common.zip_dir('img', zip_file)
        common.zip_dir('ui', zip_file)
        common.zip_dir('reports', zip_file)
        if os.path.exists('utils'):
            common.zip_dir('utils', zip_file, exclude_ext=['.pyc'])
        zip_file.close()
        with open(file_name, 'r') as f:
            result = f.read()
    finally:
        if os.path.exists(file_name):
            os.remove(file_name)
        if os.path.exists(task_file):
            os.remove(task_file)
    return result
task.register(server_export_task)

def server_import_task(task, task_id, data):

    def copy_tmp_files(data):
        dir = os.path.join(os.getcwd(), 'tmp-' + datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S"))
        if os.path.exists(dir):
            shutil.rmtree(dir)
        os.makedirs(dir)
        zip_file_name = os.path.join(dir, 'task.zip')
        with open(zip_file_name, 'w' ) as f:
            f.write(data)
        try:
            common.unzip_dir(dir, zip_file_name)
        finally:
            if os.path.exists(zip_file_name):
                os.remove(zip_file_name)
        return dir

    def delete_tmp_files(dir):
        if os.path.exists(dir):
            shutil.rmtree(dir)

    def copy_files(dir):
        from distutils import dir_util
        dir_util.copy_tree(dir, os.getcwd())

    def refresh_old_item(item):
        item = item.copy()
        item.open()
        old_dict[item.item_name] = item


    def get_items(dir):
        file_name = os.path.join(dir, 'task.dat')
        with open(file_name, 'r' ) as f:
            data = f.read()
        data_lists = cPickle.loads(data)
        new_items = {}
        old_items = {}
        items = [sys_items, sys_fields, sys_indices, sys_filters, sys_report_params, sys_roles, sys_params, sys_privileges]
        for item in items:
            task.execute('DELETE FROM "%s" WHERE "DELETED" = 1' % item.table_name)
            old_item = item.copy(handlers=False)
            old_item.soft_delete = False
            old_item.open()
            new_item = item.copy(handlers=False)
            new_item.open()
            new_item._records = data_lists[item.item_name]
            new_items[item.item_name] = new_item
            old_items[item.item_name] = old_item
        os.remove(file_name)
        return new_items, old_items

    def copy_record(old, new):
        for i, field in enumerate(old.fields):
            try:
                old.fields[i].value = new.fields[i].raw_value
            except Exception, e:
                print 'server_import_task copy_record error:', new.item_name, new.id.value, new.fields[i].field_name, new.fields[i].raw_value
                raise


    def compare_items(old, new, owner_id=None):
        result = {}
        for it in old:
            result[it.id.value] = [True, False]
        for it in new:
            if not owner_id or owner_id == it.owner_rec_id.value:
                info = result.get(it.id.value)
                if info:
                    info[1] = True
                else:
                    result[it.id.value] = [False, True]
        return result

    def update_item(item_name, detail_name=None, options=['update', 'insert', 'delete'], owner=None):
        new = new_dict[item_name]
        if owner:
            old = owner.detail_by_name(item_name)
            old.open()
        else:
            old = old_dict[item_name]
        owner_id = None
        if owner:
            owner_id = owner.id.value
        compare = compare_items(old, new, owner_id)
        if 'delete' in options:
            old.first()
            while not old.eof():
                if not owner_id or owner_id == old.owner_rec_id.value:
                    o, n = compare[old.id.value]
                    if o and not n:
                        old.delete()
                    else:
                        old.next()
                else:
                    old.next()
        if 'update' in options:
            for it in old:
                if not owner_id or owner_id == it.owner_rec_id.value:
                    o, n = compare[old.id.value]
                    if o and n and new.locate('id', old.id.value):
                        old.edit()
                        copy_record(old, new)
                        if detail_name:
                            update_item(detail_name, owner=old)
                        old.post()
        if 'insert' in options:
            for it in new:
                if not owner_id or owner_id == it.owner_rec_id.value:
                    o, n = compare[new.id.value]
                    if not o and n:
                        old.append()
                        copy_record(old, new)
                        if detail_name:
                            update_item(detail_name, owner=old)
                        old.post()
        return old

    def get_delta(item_name, detail_name=None, options=['update', 'insert', 'delete']):
        item = update_item(item_name, detail_name, options)
        return item.delta()

    def get_new_fields(item_id):
        result = []
        new_items = new_dict['sys_items']
        if new_items.locate('id', item_id):
            parent_id = new_items.parent.value
        new_fields = new_dict['sys_fields']
        for field in new_fields:
            if field.owner_rec_id.value in [item_id, parent_id]:
                if not (field.f_calculated.value or field.f_master_field.value):
                    dic = {}
                    dic['id'] = field.id.value
                    dic['field_name'] = field.f_field_name.value
                    dic['data_type'] = field.f_data_type.value
                    dic['size'] = field.f_size.value
                    result.append(dic)
        return result

    def get_table_name(item_id):
        new_items = new_dict['sys_items']
        if new_items.locate('id', item_id):
            return new_items.f_table_name.value


    error = ''

    db_type = get_db_type(task_id)
    if db_type == common.SQLITE:
        return 'Import operation is not allowed for SQLITE database'

    dir = copy_tmp_files(data)
    try:
        try:
            new_dict, old_dict = get_items(dir)

            db_sql = []
            adm_sql = []
            deltas = {}

            delta = get_delta('sys_indices', options=['delete'])
            for d in delta:
                db_sql.append(indices_delete_sql(task.sys_indices, d))
            adm_sql.append(delta.apply_sql())

            delta = get_delta('sys_items', 'sys_fields')
            for d in delta:
                if d.rec_inserted():
                    db_sql.append(items_insert_sql(task.sys_items, d))
                elif d.rec_modified():
                    db_sql.append(items_update_sql(task.sys_items, d))
                elif d.rec_deleted():
                    db_sql.append(items_delete_sql(task.sys_items, d))

            refresh_old_item(old_dict['sys_items'])
            delta = get_delta('sys_items')
            adm_sql.append(delta.apply_sql())

            refresh_old_item(old_dict['sys_fields'])
            delta = get_delta('sys_fields')
            adm_sql.append(delta.apply_sql())

            refresh_old_item(old_dict['sys_indices'])
            delta = get_delta('sys_indices', options=['update', 'insert'])
            for d in delta:
                table_name = get_table_name(d.owner_rec_id.value)
                if d.rec_inserted():
                    db_sql.append(indices_insert_sql(task.sys_indices, d, table_name, get_new_fields(d.owner_rec_id.value)))
                elif d.rec_modified():
                    db_sql.append(indices_update_sql(task.sys_indices, d, table_name, get_new_fields(d.owner_rec_id.value)))
                elif d.rec_deleted():
                    db_sql.append(indices_delete_sql(task.sys_indices, d))
            adm_sql.append(delta.apply_sql())

            delta = get_delta('sys_filters')
            adm_sql.append(delta.apply_sql())

            delta = get_delta('sys_report_params')
            adm_sql.append(delta.apply_sql())

            delta = get_delta('sys_roles')
            adm_sql.append(delta.apply_sql())

            delta = get_delta('sys_params')
            adm_sql.append(delta.apply_sql())

            delta = get_delta('sys_privileges')
            adm_sql.append(delta.apply_sql())
        except Exception, e:
            error = '%s: %s' % (e.message, traceback.format_exc())

        if not error:
            task.server.under_maintenance = True
            try:
                task.server.release_connections()
                if len(db_sql):
                    error = execute(task_id, db_sql)
                if not error:
                    result, error = task.execute(adm_sql)
                    copy_files(dir)
            except Exception, e:
                error = '%s: %s' % (e.message, traceback.format_exc())
            finally:
                task.server.under_maintenance = False
    finally:
        delete_tmp_files(dir)
    return error

task.register(server_import_task)

def get_item_module_name(item_id, module_type=None):
    it = sys_items.copy()
    it.filters.id.value = item_id
    it.open()
    if it.task_id.value == it.id.value:
        if module_type == common.SERVER_MODULE:
            return it.f_item_name.value + '_server'
        elif module_type == common.CLIENT_MODULE:
            return it.f_item_name.value + '_client'
        else:
            return it.f_item_name.value
    else:
        return get_item_module_name(it.parent.value, module_type) + '.' + it.f_item_name.value
    return

def server_get_module_name(task, item_id, module_type):
    return get_item_module_name(item_id, module_type)
task.register(server_get_module_name)

def server_find_in_task(task, task_id, search_text, case_sencitive, whole_words):

    def is_whole_word(line, pos, search_text):
        if pos > 0:
            ch = line[pos - 1]
            if ch.isalpha() or ch == '_':
                return False
        if pos + len(search_text) < len(line):
            ch = line[pos + len(search_text)]
            if ch.isalpha() or ch == '_':
                return False
        return True

    def find_in_text(text, search_text, module_name):
        result = []
        if text:
            if not case_sencitive:
                search_text = search_text.upper()
            lines = text.splitlines()
            for i, l in enumerate(lines):
                line = l
                if not case_sencitive:
                    line = l.upper()
                pos = line.find(search_text)
                if pos > -1:
                    if whole_words and not is_whole_word(line, pos, search_text):
                        continue
                    result.append((module_name, i + 1, l.strip()))
        return result

    def find_in_type(header, module_type):
        search = ''
        result = []
        for it in items:
            if module_type == common.CLIENT_MODULE:
                text = it.f_client_module.value
            elif module_type == common.WEB_CLIENT_MODULE:
                text = it.f_web_client_module.value
            elif module_type == common.SERVER_MODULE:
                text = it.f_server_module.value
            result += find_in_text(text, search_text, get_item_module_name(it.id.value, module_type))
        for line in result:
            search += '%s:%s: %s\n' % line
        search = header + '\n' + search
        return search + '\n'

    items = task.sys_items.copy(handlers=False)
    items.filters.task_id.value = task_id
    items.open(fields=['id', 'f_client_module', 'f_web_client_module', 'f_server_module'])
    return find_in_type('Search result in client:', common.CLIENT_MODULE) + \
        find_in_type('Search result in webclient:', common.WEB_CLIENT_MODULE) + \
        find_in_type('Search result in server:', common.SERVER_MODULE)
task.register(server_find_in_task)

def server_print_code(task, task_id, url):

    def sep_line(ch='-'):
        return ''.join([ch] * 80)

    def print_code(it):
        for i in range(3):
            if i == common.CLIENT_MODULE:
                field = 'f_client_module'
            elif i == common.WEB_CLIENT_MODULE:
                field = 'f_web_client_module'
            else:
                field = 'f_server_module'
            code = it.field_by_name(field).value
            if code and len(code):
                name = get_item_module_name(it.id.value, i)
                result[i] = result[i] + sep_line() +  '\nMODULE: ' + name + \
                     '\n' + sep_line() + '\n\n' + code + '\n\n'


    def print_children_code(parent_value):
        for it in items:
            if it.parent.value == parent_value:
                print_code(it)
                rec_no = it.rec_no
                print_children_code(it.id.value)
                it.rec_no = rec_no

    result = {}
    for i in range(3):
        if i == common.CLIENT_MODULE:
            text = 'CLIENT CODE'
        elif i == common.WEB_CLIENT_MODULE:
            text = 'WEB CLIENT CODE'
        else:
            text = 'SERVER CODE'
        text = '\n' + sep_line('*') + '\n' + text + '\n' + sep_line('*') + '\n\n'
        result[i] = text

    items = task.sys_items.copy()
    items.filters.task_id.value = task_id
    items.open()
    items.locate('id', task_id)

    code = 'TASK: ' + items.f_item_name.value + '\n\n'

    print_code(items)
    print_children_code(task_id)


    for i in range(3):
        code += result[i]

    path = os.path.join(os.getcwd(), 'static', 'reports')
    if not os.path.exists(path):
        os.makedirs(path)
    file_name = 'code.txt'
    code_file_name = os.path.join(path, file_name)
    with open(code_file_name, "w") as f:
        f.write(code)
    if url:
        code_file_name = 'http://%s/static/reports/%s' % (url, file_name)
    return code_file_name
task.register(server_print_code)

def server_load_report_module(task, module_name):
    file_name = os.path.join(task.work_dir, 'reports', module_name)
    with open(file_name) as f:
        result = f.read()
    return result
task.register(server_load_report_module)

def server_store_report_module(task, text, module_name):
    file_name = os.path.join(task.work_dir, 'reports', module_name)
    with open(file_name, 'wb') as f:
        f.write(text)
task.register(server_store_report_module)

def server_remove_events_code(task):
    file_name = os.path.join(os.getcwd().decode('utf-8'), 'js','events.js')
    try:
        os.remove(os.path.join(os.getcwd().decode('utf-8'), 'js','events.js'));
    except:
        pass
    if os.path.exists(file_name):
        return False
    return True
task.register(server_remove_events_code)

def server_update_events_code(task=None, task_id=None):

    def find_events(code):
        result = []
        code = code.replace('.delete(', '["delete"](')
        n = parse(code)
        for key in n:
            if key.type == 'FUNCTION':
                result.append(key.name)
        return result

    def process_events(code, ID, script):
        if code:
            script += '\nfunction Events%s() { // %s \n\n' % (ID, get_item_module_name(ID))
            code = '\t' + code.replace('\n', '\n\t')
            code = code.replace('    ', '\t')
            script += code
            events = find_events(code)
            if len(events):
                script += '\n'
                for event in events:
                    script += '\tthis.%s = %s;\n' % (event, event)
            script += '}\n\n'
            script += 'window.task_events.events%s = new Events%s();\n' % (ID, ID)
        return script

    print 11111111
    it = sys_items.copy(handlers=False)
    if task_id is None:
        it.set_where(type_id=common.TASK_TYPE)
        it.open()
        task_id = it.task_id.value
    it.filters.task_id.value = task_id
    it.open(fields=['id', 'f_name', 'f_web_client_module'])
    print 22222222
    script = '(function(window, undefined) {\n"use strict";\nvar $ = window.$;\n\nfunction TaskEvents() {};\n\nwindow.task_events = new TaskEvents();\n'
    for it in it:
        code = it.f_web_client_module.value
        if code:
            code = code.strip()
            if code:
                script = process_events(code, it.id.value, script)
    script += '\n})( window )'
    print 3333333
    with open(os.path.join(os.getcwd().decode('utf-8'), 'js','events.js'), 'w') as f:
        f.write(script)
task.register(server_update_events_code)

def server_get_info(task, item_id):
    items = sys_items.copy()
    items.filters.id.value = item_id
    items.open()
    type_id = items.type_id.value
    parent = items.parent.value
    task_id = items.task_id.value
    table_id = items.table_id.value
    name = items.f_name.value

    if type_id == common.TASK_TYPE:
        item = task
        task_id = item_id
    elif group_type(type_id):
        item = ServerGroup('', '', '')
    else:
        item = sys_items

    result = {}

    fields_dict = {}
    if type_id in [common.CATALOG_TYPE, common.JOURNAL_TYPE, common.TABLE_TYPE, common.DETAIL_TYPE]:
        fields = task.sys_fields.copy()
        if table_id:
            fields.filters.owner_rec_id.value = [table_id, task.sys_items.field_by_id(table_id, 'parent')]
        else:
            fields.filters.owner_rec_id.value = [item_id, parent]
        fields.open()
        for f in fields:
            if f.f_field_name.value.lower() != 'deleted':
                fields_dict[f.f_field_name.value] = None
    result[common.editor_tabs[common.TAB_FIELDS]] = fields_dict

    root_tree = {}

    def get_children(id_value, type_id, dict, key, parent_id=None):
        it = sys_items.copy()
        it.filters.parent.value = id_value
        it.details_active = False
        it.open()
        if it.record_count() > 0 and type_id in (common.TASK_TYPE, common.CATALOGS_TYPE, common.JOURNALS_TYPE, common.TABLES_TYPE, common.REPORTS_TYPE):
            childs = {}
            for rec in it:
                get_children(it.id.value, it.type_id.value, childs, it.f_item_name.value, it.parent.value)
            dict[key] = childs
        else:
            childs = {}
            fields = sys_fields.copy()
            fields.filters.owner_rec_id.value = [id_value, parent_id]
            fields.open()
            for f in fields:
                if f.f_field_name.value.lower() != 'deleted':
                    childs[f.f_field_name.value] = None
            dict[key] = childs
    get_children(task_id, common.TASK_TYPE, root_tree, u'root_tree')
    result[common.editor_tabs[common.TAB_TASK]] = root_tree[u'root_tree']
    return result
task.register(server_get_info)


###############################################################################
#                                  sys_items                                  #
###############################################################################

def group_type(type_id):
    if type_id in (common.CATALOGS_TYPE, common.JOURNALS_TYPE, common.TABLES_TYPE):
        return True

def get_db_type(task_id):
    task = sys_tasks.copy()
    task.filters.task_id.value = task_id
    task.open()
    return task.f_db_type.value

def manual_update(task_id):
    task = sys_tasks.copy()
    task.filters.task_id.value = task_id
    task.open()
    return task.f_manual_update.value

def get_table_fields(fields, delta_fields=None):

    def field_dict(field):
        if not (field.f_calculated.value or field.f_master_field.value):
            dic = {}
            dic['id'] = field.id.value
            dic['field_name'] = field.f_field_name.value
            dic['data_type'] = field.f_data_type.value
            dic['size'] = field.f_size.value
            return dic

    def field_info(fields):
        result = []
        for field in fields:
            if not (field.f_calculated.value or field.f_master_field.value):
                dic = field_dict(field)
                if dic:
                    result.append(dic)
        return result

    def find_field(fields_info, field_id):
        for field in fields_info:
            if field['id'] == field_id:
                return field

    result = []
    parent_fields = sys_fields.copy()
    parent_fields.filters.owner_rec_id.value = [fields.owner.parent.value]
    parent_fields.open()
    result = field_info(parent_fields) + field_info(fields)
    if delta_fields:
        for field in delta_fields:
            if not (field.f_calculated.value or field.f_master_field.value):
                if field.record_status == common.RECORD_INSERTED:
                    dic = field_dict(field)
                    if dic:
                        result.append(dic)
                if field.record_status == common.RECORD_DELETED:
                    field_info = find_field(result, field.id.value)
                    if field_info:
                        result.remove(field_info)
                elif field.record_status == common.RECORD_MODIFIED:
                    field_info = find_field(result, field.id.value)
                    if field_info:
                        field_info['id'] = field.id.value
                        field_info['field_name'] = field.f_field_name.value
                        field_info['data_type'] = field.f_data_type.value
                        field_info['size'] = field.f_size.value
                    else:
                        dic = field_dict(field)
                        if dic:
                            result.append(dic)
    return result

def item_children(item_id):
    items = sys_items.copy()
    items.filters.parent.value = item_id
    items.open()
    return items

def update_interface(delta, type_id, item_id):

    def delete_id_from_list(id_list, id_value):
        return [id_it for id_it in id_list if id_it[0] != id_value]

    if type_id in (common.CATALOGS_TYPE, common.JOURNALS_TYPE, common.TABLES_TYPE, common.CATALOG_TYPE, common.JOURNAL_TYPE, common.TABLE_TYPE) and \
        delta.details.sys_fields.record_count():
        if type_id in (common.CATALOGS_TYPE, common.JOURNALS_TYPE, common.TABLES_TYPE):
            for it in item_children(item_id):
                update_interface(delta, it.type_id.value, it.id.value)
        else:
            item = sys_items.copy()
            item.filters.id.value = item_id
            item.open()
            fields = sys_fields.copy()
            fields.filters.owner_rec_id.value = [item_id, item.parent.value]
            fields.open()
            common.load_interface(item)
            if delta.record_status == common.RECORD_INSERTED:
                for field in fields:
                    if field.owner_rec_id.value == item.parent.value:
                        if not field.f_field_name.value in common.SYSTEM_FIELDS:
                            item._view_list.append([field.id.value, False, False, False])
                            item._edit_list.append([field.id.value])

            for d in delta.details.sys_fields:
                if d.record_status in [common.RECORD_INSERTED, common.RECORD_DELETED]:
                    field_name = d.f_field_name.value
                    if fields.locate('f_field_name', field_name):
                        if d.record_status == common.RECORD_INSERTED:
                            if not field_name in common.SYSTEM_FIELDS:
                                item._view_list.append([fields.id.value, False, False, False])
                                item._edit_list.append([fields.id.value])
                        elif d.record_status == common.RECORD_DELETED:
                            item._view_list = delete_id_from_list(item._view_list, fields.id.value)
                            item._edit_list = delete_id_from_list(item._edit_list, fields.id.value)
                            item._order_list = delete_id_from_list(item._order_list, fields.id.value)
            common.store_interface(item)

def change_item_sql(item, old_fields, new_fields):
    db_type = get_db_type(item.task_id.value)
    if item.type_id.value in (common.CATALOGS_TYPE, common.JOURNALS_TYPE, common.TABLES_TYPE):
        result = []
        for it in item_children(item.id.value):
            result.append(it.change_table_sql(db_type, old_fields, new_fields))
        return result
    elif item.type_id.value in (common.CATALOG_TYPE, common.JOURNAL_TYPE, common.TABLE_TYPE):
        return item.change_table_sql(db_type, old_fields, new_fields)

def items_insert_sql(item, delta):
    if delta.type_id.value in (common.CATALOG_TYPE, common.JOURNAL_TYPE, common.TABLE_TYPE):
        db_type = get_db_type(delta.task_id.value)
        sql = delta.create_table_sql(db_type, delta.f_table_name.value, get_table_fields(delta.details.sys_fields))
        return sql

def items_execute_insert(item, delta):
    if not manual_update(delta.task_id.value):
        sql = items_insert_sql(item, delta)
        if sql:
            error = execute(delta.task_id.value, sql)
            if error:
                raise Exception, u'Error while creating table %s: %s' % (table_name.upper(), error)
    sql = delta.apply_sql()
    result = item.task.execute(sql)
    exec_result = result[0]
    result_id = exec_result['changes'][0]['rec_id']
    update_interface(delta, delta.type_id.value, result_id)
    return result

def items_update_sql(item, delta):
    if delta.type_id.value in (common.CATALOGS_TYPE, common.JOURNALS_TYPE, common.TABLES_TYPE, common.CATALOG_TYPE, common.JOURNAL_TYPE, common.TABLE_TYPE) and \
        delta.details.sys_fields.record_count():
        it = item.copy()
        it.filters.id.value = delta.id.value
        it.open()
        it_fields = it.details.sys_fields
        it_fields.open()
        old_fields = get_table_fields(it_fields)
        new_fields = get_table_fields(it_fields, delta.details.sys_fields)
        sql = change_item_sql(delta, old_fields, new_fields)
        return sql

def items_execute_update(item, delta):
    if not manual_update(delta.task_id.value):
        sql = items_update_sql(item, delta)
        if sql:
            error = execute(delta.task_id.value, sql)
            if error:
                raise Exception, u'Error while modifying table: %s' % error
    sql = delta.apply_sql()
    result = item.task.execute(sql)
    update_interface(delta, delta.type_id.value, delta.id.value)
    return result

def items_delete_sql(item, delta):
    if delta.type_id.value in (common.CATALOG_TYPE, common.JOURNAL_TYPE, common.TABLE_TYPE):
        db_type = get_db_type(delta.task_id.value)
        sql = delta.delete_table_sql(db_type)
        return sql

def items_execute_delete(item, delta):
    if not manual_update(delta.task_id.value):
        sql = items_delete_sql(item, delta)
        if sql:
            error = execute(delta.task_id.value, sql)
            if error:
                raise Exception, u'Error while deleting table %s: %s' % (delta.table_name.upper(), error)
    commands = []
    sql = delta.apply_sql()
    commands.append(sql)
    for it in (sys_filters, sys_indices, sys_report_params):
        commands.append('UPDATE %s SET DELETED = 1 WHERE OWNER_REC_ID = %s' % (it.table_name.upper(), delta.id.value))
    result = item.task.execute(commands)
    return result

def items_apply_changes(item, delta, params, priv, user_info, env):
    if delta.rec_inserted():
        result = items_execute_insert(item, delta)
    elif delta.rec_modified():
        result = items_execute_update(item, delta)
    elif delta.rec_deleted():
        result = items_execute_delete(item, delta)
    reload_task();
    return result
sys_items.on_apply = items_apply_changes

def do_on_apply_changes(item, delta, params, priv, user_info, env):
    sql = delta.apply_sql()
    result = item.task.execute(sql)
    reload_task();
    return result

sys_filters.on_apply = do_on_apply_changes
sys_report_params.on_apply = do_on_apply_changes

###############################################################################
#                                 sys_indices                                 #
###############################################################################

def change_foreign_index(delta):
    items = sys_items.copy()
    items.filters.id.value = delta.owner_rec_id.value
    items.open()
    it_fields = items.details.sys_fields
    it_fields.open()
    fields = get_table_fields(it_fields)
    new_fields = list(fields)
    return items.recreate_table_sql(common.SQLITE, fields, new_fields, delta)

def indices_insert_sql(item, delta, table_name=None, new_fields=None):
    if not table_name:
        table_name = sys_items.field_by_id(delta.owner_rec_id.value, 'f_table_name')
    db_type = get_db_type(delta.task_id.value)
    if db_type == common.SQLITE and delta.f_foreign_index.value:
        return change_foreign_index(delta)
    else:
        return delta.create_index_sql(db_type, table_name, new_fields=new_fields)

def indices_execute_insert(item, delta, params):
    if not manual_update(delta.task_id.value):
        sql = indices_insert_sql(item, delta)
        error = execute(delta.task_id.value, sql)
        if error:
            raise Exception, u'Error while creating index %s: %s' % (delta.f_index_name.value.upper(), error)
    sql = delta.apply_sql()
    return item.task.execute(sql)

def indices_update_sql(item, delta, table_name=None, new_fields=None):
    sql = []
    db_type = get_db_type(delta.task_id.value)
    ind = sys_indices.copy()
    ind.filters.id.value = delta.id.value
    ind.open()
    if not table_name:
        table_name = sys_items.field_by_id(delta.owner_rec_id.value, 'f_table_name')
    if db_type == common.SQLITE and delta.f_foreign_index.value:
        sql = change_foreign_index(delta)
    else:
        sql.append(ind.delete_index_sql(db_type))
        sql.append(delta.create_index_sql(db_type, table_name, new_fields=new_fields))
    return sql

def indices_execute_update(item, delta, params):
    if not manual_update(delta.task_id.value):
        sql = indices_update_sql(item, delta)
        error = execute(delta.task_id.value, sql)
        if error:
            raise Exception, u'Error while modifying index %s: %s' % (delta.f_index_name.value.upper(), error)
    sql = delta.apply_sql()
    return item.task.execute(sql)

def indices_delete_sql(item, delta):
    db_type = get_db_type(delta.task_id.value)
    if db_type == common.SQLITE and delta.f_foreign_index.value:
        return change_foreign_index(delta)
    else:
        return delta.delete_index_sql(db_type)

def indices_execute_delete(item, delta, params):
    if not manual_update(delta.task_id.value):
        sql = indices_delete_sql(item, delta)
        error = execute(delta.task_id.value, sql)
        if error:
            raise Exception, u'Error while deleting index %s' % error
    sql = delta.apply_sql()
    return item.task.execute(sql)

def indices_apply_changes(item, delta, params, priv, user_info, env):
    if delta.rec_inserted():
        result = indices_execute_insert(item, delta, params)
    elif delta.rec_modified():
        result = indices_execute_update(item, delta, params)
    elif delta.rec_deleted():
        result = indices_execute_delete(item, delta, params)
    return result
sys_indices.on_apply = indices_apply_changes

###############################################################################
#                                  sys_roles                                  #
###############################################################################

def privileges_table_get_select(item, query, user_info, enviroment):
    owner_id = query['__owner_id']
    owner_rec_id = query['__owner_rec_id']
    result_sql =  \
        """
        SELECT "SYS_PRIVILEGES"."ID", "SYS_PRIVILEGES"."DELETED", "SYS_PRIVILEGES"."OWNER_ID",
        "SYS_PRIVILEGES"."OWNER_REC_ID",
        "SYS_ITEMS"."ID",
        "SYS_PRIVILEGES"."F_CAN_VIEW",
        "SYS_PRIVILEGES"."F_CAN_CREATE",
        "SYS_PRIVILEGES"."F_CAN_EDIT",
        "SYS_PRIVILEGES"."F_CAN_DELETE",
        "SYS_ITEMS"."F_NAME" AS "ITEM_ID_LOOKUP"
        FROM (SYS_ITEMS LEFT JOIN  "SYS_PRIVILEGES" ON "SYS_PRIVILEGES"."ITEM_ID" = "SYS_ITEMS"."ID" AND
            "SYS_PRIVILEGES"."DELETED" = 0 and SYS_PRIVILEGES.OWNER_ID = %s AND SYS_PRIVILEGES.OWNER_REC_ID = %s)
        WHERE "SYS_ITEMS"."DELETED" = 0 AND "SYS_ITEMS"."TYPE_ID" IN (10, 11, 12, 13) AND "SYS_ITEMS"."TABLE_ID" = 0
        ORDER BY "SYS_ITEMS"."TYPE_ID", "ITEM_ID_LOOKUP"
        """
    result_sql = result_sql % (owner_id, owner_rec_id)

    error_mes = ''
    try:
        rows = task.execute_select(result_sql)
    except Exception, e:
        error_mes = e.message
    return rows, error_mes
role_privileges.on_select = privileges_table_get_select
