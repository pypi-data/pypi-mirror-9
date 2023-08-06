#!/usr/bin/python
# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-
from ConfigParser import RawConfigParser
from onappapi import OnApp
import os, sys, argparse, json
from prettytable import PrettyTable

cmd = None
resource = None
action = None

def get_arg(resource = None, exit = True):
    if len(sys.argv) > 0: return sys.argv.pop(0)
    else: 
        if exit: usage(resource)
        else: return None


def usage(resource = None):
    info = {
            'vm' : { 'actions' : [ 'list [-C|-c col -c coln]', 'info', 'start', 'stop', 'shutdown', 'delete' ], 'example' : [ 'start 45', 'shutdown 45' ] },
            'template' : { 'actions' : [ 'list [-C|-c col -c coln]', 'listall [-C|-c col -c coln]', 'listsystem [-C|-c col -c coln]', 'listown [-C|-c col -c coln]', 'listinactive [-C|-c col -c coln]', 'listuser [-C|-c col -c coln]', 'listuserid [user_id][-C|-c col -c coln]' ] },
            'cache' : { 'actions' : [ 'clear '] },
            'ds' : { 'actions' : [ 'list [-C|-c col -c coln]' ] },
            'dszone' : { 'actions' : [ 'list [-C|-c col -c coln]' ] },
            'log' : { 'actions' : [ 'list [-C|-c col -c coln]', 'info [log_id]' ] },
            'netzone' : { 'actions' : [ 'list [-C|-c col -c coln]' ] },
            'system' : { 'actions' : [ 'alerts', 'version' ] },
            'usage' : { 'actions' : [ 'all' ] },
            'user' : { 'actions' : [ 'list [-C|-c col -c coln]', 'info [user_id]' ] },
            'disk' : { 'actions' : [ 'list', 'list vs [vm_id]', 'usage [disk_id]', 'create [options]', 'delete [options]' ] },
            'billing_plan' : { 'actions': [ 'list', 'info [bp_id]' ] },
            'backup' : { 'actions': [ 'list vm_id [-C|-c col -c coln]'], },
            }
    if resource:
        if resource in info:
            print '%s %s action' % (cmd, resource)
            print 'Available actions: %s' % ', '.join(info[resource]['actions'])
            if 'example' in info[resource]:
                for e in info[resource]['example']:
                    print '\t%s %s %s' % (cmd, resource, e)
    else:
        print '%s resource action' % cmd
        print 'Available resources: %s' % ', '.join(info.keys())
    sys.exit(0)

def show_create_params(obj):
    return cliparser( args = api.generic_get_create_params( resource = obj ) ) 

def show_columns(resource, columns):
    print 'Available columns in %s list' % resource
    pt = PrettyTable(['Column', 'Description'])
    pt.align = 'l'
    for c, d in columns.items():
        pt.add_row([ c, d ])
    print pt
    usage(resource)

def cliparser(args):
    parser = argparse.ArgumentParser(prog='%s %s %s' % (cmd, resource, action))
    for arg in args:
        if 'options' in arg: parser.add_argument(arg['args'], **arg['options'])
        else: parser.add_argument(arg['args'])
    return vars(parser.parse_args([] if len(sys.argv) == 0 else sys.argv))

def list_columns(resource, obj):
    list_args = [
            { 'args' : '-c',    'options' : { 'required' : False, 'type' : str,  'dest' : 'columns',        'action' : 'append' } },
            { 'args' : '-C' ,   'options' : { 'required' : False, 'dest' : 'show_columns',   'action' : 'store_true' } },
            ]
    args = cliparser(list_args)
    if args['show_columns']:
        show_columns(resource, api.generic_get_columns(obj) )
    if args['columns']:
        columns = []
        for c in args['columns']:
            if ',' in c: columns += c.split(',')
            else: columns.append(c)
    else: columns = args['columns']
    return columns

def main():
    global cmd 
    global resource
    global action
    cmd = os.path.basename(get_arg())

    conf = os.path.join(os.path.expanduser("~"), '.pyonapp.conf')
    config = RawConfigParser()
    
    if not os.path.exists(conf):
        config.add_section('onapp')
        config.set('onapp', 'user', raw_input('Username: '))
        config.set('onapp', 'password', raw_input('Passowrd: '))
        config.set('onapp', 'url', raw_input('Hostname: '))
        with open(conf, 'wb') as openconf: config.write(openconf)
    else: config.read(conf)
    
    user = config.get('onapp', 'user')
    password = config.get('onapp', 'password')
    url = config.get('onapp', 'url')
    
    api = OnApp(user, password, url)
    
    resource = get_arg()
    if resource: action = get_arg(resource)
    
    if resource == 'vm':
        if  action == 'list': print api.vm_list(columns = list_columns(resource, 'VM'))
        elif action == 'info': print api.vm_info( vm_id = get_arg(resource) )
        elif action == 'browser': api.vm_browser( vm_id = get_arg(resource) )
        elif action == 'console': api.vm_console( vm_id = get_arg(resource) )
        elif action == 'start': print api.vm_start( vm_id = get_arg(resource))
        elif action == 'stop': print api.vm_stop( vm_id = get_arg(resource) )
        elif action == 'shutdown': print api.vm_shutdown( vm_id = get_arg(resource))
        elif action == 'delete': print api.vm_delete( vm_id = get_arg(resource) )
        elif action == 'create':
            #parser = argparse.ArgumentParser(prog='onappcli vm create')
            #parser.add_argument('--memory', help='Max Memory', dest='memory', required = True, type = int)
            #parser.add_argument('--cpus', help='Max CPU', dest='cpus', required = True, type = int)
            #parser.add_argument('--cpu_shares', help='CPU Shares', dest='cpu_shares', default = 100, type = int)
            #parser.add_argument('--cpu-sockets', help='CPU Sockets', dest='cpu_sockets', default = 1, type = int)
            #parser.add_argument('--cpu-threads', help='CPU Threads', dest='cpu_threads', default = 1, type = int)
            #parser.add_argument('--hostname', help='Set hostname', dest='hostname', required = True, type = str)
            #parser.add_argument('--label', help='Set label', dest='label', required = True, type = str)
            #parser.add_argument('--data-store-group-primary-id', help='Primary Datastore ID', required = True, type = int)
            #parser.add_argument('--primary-disk-size', help='Set primary disk size', dest='primary_disk_size', default = 5, type = int)
            #parser.add_argument('--primary-disk-min-iops', help='Primary disk IOPS', dest='primary_disk_min_iops', default = 100, type = int)
            #parser.add_argument('--data-store-group-swap-id', help='Swap Datastore ID', default = 1, type = int)
            #parser.add_argument('--swap-disk-size', help='Set swap disk size', dest='swap_disk_size', default = 0, type = int)
            #parser.add_argument('--swap-disk-min-iops', help='Swap disk IOPS', dest='swap_disk_min_iops', default = 100, type = int)
            #parser.add_argument('--primary-network-group-id', help='Network zone', dest='primary_network_group_id', required = True, type = int)
            #parser.add_argument('--primary-network-id', help='Set primary network id', dest='primary_network_id', required = True, type = int)
            #parser.add_argument('--selected-ip-address-id', help='Primary IP address ID', dest='selected_ip_address_id', default = 0, type = int)
            #parser.add_argument('--required-virtual-machine-build', help='Build virtual machine', dest='required_virtual_machine_build', default=1, type = int)
            #parser.add_argument('--required-virtual-machine-startup', help='Start after create', dest='required_virtual_machine_startup', default = 1, type = int)
            #parser.add_argument('--required-ip-address-assignment', help='Auto assing IP', dest='required_ip_address_assignment', default = 1, type = int)
            #parser.add_argument('--required-automatic-backup', help='Auto backups', dest='required_automatic_backup', default = 0, type = int)
            #parser.add_argument('--type-of-format', help='Type of disk format', dest='type_of_format', default = 'ext4', type = str)
            #parser.add_argument('--enable-autoscale', help='Enable autoscale', dest='enable_autoscale', default = 0, type = int)
            #parser.add_argument('--recipe-ids', help='Recipe IDs', dest='recipe_ids', default = [], type = list)
            #parser.add_argument('--custom-recipe-variables', help='Custom recipe variables', default = [], type = list)
            #parser.add_argument('--template-id', help='Template ID', dest='template_id', required = True, type = int)
            #parser.add_argument('--initial-root-password', help='Root password', dest='initial_root_password', required = False, type = str)
            #parser.add_argument('--rate-limit', help='Rate limit', dest='rate_limit', default = 'none', type = str)
            #parser.add_argument('--hypervisor-group-id', help='Hypervisor group id', dest='hypervisor_group_id', type = int)
            #parser.add_argument('--hypervisor-id', help='Hypervisor', dest='hypervisor_id', required = True, type = int)
            #parser.add_argument('--licensing-server-id', help='Licensing server', dest='licensing_server_id', default = 0, type = int)
            #parser.add_argument('--licensing-type', help='License type', dest='licensing_type', default = 'kms', type = str)
            #parser.add_argument('--licensing-key', help='License Key', dest='licensing_key', default = '', type = str)
    
            args = show_create_params('VM')
            #args = vars(parser.parse_args([] if len(sys.argv) == 0 else sys.argv))
            #vm = api.vm_create(**args)
            #if vm and vm.__class__.__name__ == 'VM':
            #    print vm.id
            #    print vm.label
            #    print vm.hostname
    
        else: usage('vm')
    
    elif resource == 'template':
        columns = list_columns(resource, 'Template')
        if action == 'list' or action == 'listall': print api.template_list(columns = columns, types = 'all')
        elif action == 'listsystem': print api.template_list(columns = columns, types = 'system')
        elif action == 'listown': print api.template_list(columns = columns, types = 'own')
        elif action == 'listuser': print api.template_list(columns = columns, types = 'user')
        elif action == 'listinactive': print api.template_list(columns = columns, types = 'inactive')
        elif action == 'listuserid': print api.template_list(columns = columns, types = 'user', user_id = get_arg('template'))
        else: usage('template')
    elif resource == 'cache':
        if action == 'clear': api.clear_cache()
        else: usage('cache')
    elif resource == 'dszone':
        if action == 'list': print api.dszone_list(columns = list_columns(resource, 'DSZone'))
        elif action == 'create': 
            args = show_create_params('DSZone') 
            api.dszone_create(**args)
        else: usage('dszone')
    elif resource == 'ds':
        if action == 'list': print api.ds_list(columns = list_columns(resource, 'DS'))
        else: usage('ds')
    elif resource == 'netzone':
        if action == 'list': print api.netzone_list(columns = list_columns(resource, 'NetworkZone'))
        else: usage('netzone')
    elif resource == 'log':
        if action == 'list': print api.log_list( columns = list_columns(resource, 'Log') )
        elif action == 'info': print api.log_info( log_id = get_arg('log') )
        else: usage('log')
    elif resource == 'system':
        if action == 'alerts': api.alerts()
        elif action == 'version': print api.onapp_version()
        else: usage('system')
    elif resource == 'usage':
        if action == 'all': print api.usage()
        else: usage('usage')
    elif resource == 'disk':
        if action == 'list': 
            subaction = get_arg('disk', False)
            if not subaction: print api.disk_list()
            elif subaction == 'vs': print api.disk_list_vs( vm_id = get_arg('disk'))
            else: usage('disk')
        elif action == 'usage': print api.disk_usage( disk_id = get_arg('disk'))
        elif action == 'create':
            list_args = [
                    { 'args' : '--vs-id',                   'options' : { 'required' : True, 'type' : int,   'dest' : 'vm_id' } },
                    { 'args' : '--data-store-id',           'options' : { 'required' : True, 'type' : int,   'dest' : 'data_store_id' } }, 
                    { 'args' : '--label',                   'options' : { 'required' : True, 'type' : str, } },
                    { 'args' : '--primary',                 'options' : { 'required' : True, 'type' : str,   'default' : 'false', 'choices' : [ 'true', 'false' ] } },
                    { 'args' : '--disk_size',               'options' : { 'required' : True, 'type' : int,   'dest' : 'disk_size' }},
                    { 'args' : '--is-swap',                 'options' : { 'required' : True, 'type' : str,   'dest' : 'is_swap', 'choices' : [ 'true', 'false' ] } },
                    { 'args' : '--mount-point',             'options' : { 'required' : False,'type' : str,   'dest' : 'mount_point' } },
                    { 'args' : '--hot-attach',              'options' : { 'default' : True,  'type' : bool,  'dest' : 'hot_attach'  } },
                    { 'args' : '--min-iops',                'options' : { 'default' : 100,   'type' : int,   'dest' : 'min_iops' } },
                    { 'args' : '--add-to-linux-fstab',      'options' : { 'default' : False, 'type' : bool,  'dest' : 'add_to_linux_fstab' } },
                    { 'args' : '--add-to-freebsd-fstab',    'options' : { 'default' : False, 'type' : bool,  'dest' : 'add_to_freebsd_fstab' } },
                    { 'args' : '--require-format-disk',     'options' : { 'default' : False, 'type' : str,   'dest' : 'require_format_disk', 'choices' : [ 'true', 'false' ] } },
                    { 'args' : '--file-system',             'options' : { 'required' : True, 'type' : str,   'dest' : 'file_system', 'choices' : [ 'ext3', 'ext4' ] } },
                    ]
            args = cliparser(list_args)
            api.disk_create(**args)
        elif action == 'delete': 
            list_args = [
                    { 'args' : '--vs-id',   'options' : { 'required' : True, 'type' : int,   'dest' : 'vm_id' } },
                    { 'args' : '--disk-id', 'options' : { 'required' : True, 'type' : int,   'dest' : 'disk_id' } },
                    ]
            args = cliparser(list_args)
            print api.disk_delete(**args)
        else: usage('disk')
    elif resource == 'user':
        if action == 'list': print api.user_list( columns = list_columns(resource, 'User') )
        elif action == 'info': print api.user_info( user_id = get_arg('user') )
        else: usage('user')
    elif resource == 'billing_plan':
        if action == 'list': print api.billing_plan_list()
        elif action == 'info': print api.billing_plan_info( billing_plan_id = get_arg('billing_plan') )
        else: usage('billing_plan')
    elif resource == 'backup':
        if action == 'list': print api.backup_vs_list( vm_id = get_arg('backup'), columns = list_columns(resource, 'Backup') )
    else: usage()
