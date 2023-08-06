import json, time
import inspect
from prettytable import PrettyTable
import os, shutil, pycurl, sys
from StringIO import StringIO 

# Objects
from resources import VM, Template, DSZone, DS, NetworkZone, Log, Usage, Disk, DiskUsage, User, Role, Permission, BillingPlan, Backup

class OnApp(object):
    username = None
    password = None
    url = None
    tmpdir = '/tmp/onapp'
    recursive = True

    def __init__(self, username, password, url, tmpdir = '/tmp/onapp', recursive = True):
        self.username = username
        self.password = password
        self.url = url
        self.recursive = recursive

    def clear_cache(self):
        shutil.rmtree(self.tmpdir)

    def get_data(self, url):
        data = self.get_cache(url)
        if data: return (True, data)
        else:
            data = self.exec_url(url)
            (status, data) = self.is_valid_out(data)
            if status:
                self.write_cache(url, data)
                return (status, data)
        return False

    def write_cache(self, url, data):
        fullpath = os.path.join(self.tmpdir, url)
        if not os.path.exists(os.path.dirname(fullpath)): os.makedirs(os.path.dirname(fullpath))
        fd = open(fullpath, 'w')
        fd.write(json.dumps(data, indent=3))
        fd.close()

    def get_cache(self, url):
        if os.path.isfile(os.path.join(self.tmpdir, url)):
            ago=time.time()-300
            if os.path.getmtime(os.path.join(self.tmpdir, url))<ago:
                return False
        try:
            fd = open(os.path.join(self.tmpdir, url), 'r')
        except:
            return False
        data = fd.read()
        if data: return json.loads(data)
        else: return False

    def exec_url(self, url, method = 'GET', data = None):
        buffer = StringIO()
        c = pycurl.Curl()
        c.setopt(c.URL, '%s/%s' % (self.url, url))
        c.setopt(c.WRITEDATA, buffer)
        c.setopt(c.USERPWD, '%s:%s' % (self.username, self.password))
        c.setopt(c.CUSTOMREQUEST, method)
        c.setopt(c.HTTPHEADER, ['Accept: application/json', 'Content-type: application/json'])
        if json:
            c.setopt(c.POSTFIELDS, json.dumps(data))
        c.perform()
        status = c.getinfo(c.RESPONSE_CODE)
        c.close()

        body = buffer.getvalue()
        if body: body = json.loads(body)

        return { 'status' : status, 'body' : body }

    def is_valid_out(self, output):
        if int(output['status']) in [ 200, 201, 204 ]:
            if int(output['status']) == 204: return 'OK'
            return (True, output['body'])
        elif int(output['status']) in [ 403, 404, 422, 500 ]: 
            for d in output['body']['errors']: print d
            sys.exit(1)
        else: return (False, output['body']['errors'])

    def log_list(self, columns = None):
        (status, data) = self.get_data('logs.json')
        if status:
            if not columns:
                columns = [ 'id', 'action', 'status', 'target_type', 'target_id' ]
            return self.generic_return_table(data, Log, columns)

    def log_info(self, log_id):
        (status, data) = self.get_data('logs/%s.json' % log_id)
        if status:
            l = Log(data)
            print vars(l)

    def vm_list(self, sortby = 'Hostname', columns = None):
        (status, data) = self.get_data('virtual_machines.json')
        if status:
            if not columns:
                columns = ['hostname', 'id', 'identifier', 'user', 'cpus', 'memory', 'total_disk_size', 'booted']
            return self.generic_return_table(data, VM, columns)

    def vm_info(self, vm_id):
        (status, data) = self.get_data('virtual_machines/%s.json' % vm_id)
        if status:
            vm = VM(data)
            return vm

    def vm_browser(self, vm_id):
        vm = self.vm_info(vm_id)
        os.system('x-www-browser http://%s/virtual_machines/%s' % (self.url, vm.identifier))

    def vm_console(self, vm_id):
        vm = self.vm_info(vm_id)
        os.system('x-www-browser https://%s/virtual_machines/%s/console_popup' % (self.url, vm.identifier))

    def vm_delete(self, vm_id, convert = 0, destroy = 0):
        if convert not in [ 0, 1]: return False
        if destroy not in [ 0, 1]: return False
        data = self.exec_url('virtual_machines/%s.json?convert_last_backup=%s&destroy_all_backups=%s' % ( vm_id, convert, destroy ), 'DELETE')
        (status, data) = self.is_valid_out(data)
        if isinstance(data, list):
            for d in data:
                print d
        else:
            print data

    def vm_start(self, vm_id):
        data = self.exec_url('virtual_machines/%s/startup.json' % vm_id, 'POST')
        (status, data) = self.is_valid_out(data)
        print data
        
    def vm_shutdown(self, vm_id):
        data = self.exec_url('virtual_machines/%s/shutdown.json' % vm_id, 'POST')
        (status, data) = self.is_valid_out(data)
        print data

    def vm_stop(self, vm_id):
        data = self.exec_url('virtual_machines/%s/stop.json' % vm_id, 'POST')
        (status, data) = self.is_valid_out(data)
        print data

    def vm_create(self, **kwargs):
        args = {}
        for (item, value) in kwargs.items():
            args[item] = value
        vs = { 'virtual_machine' : args }

        data = self.exec_url('virtual_machines.json', 'POST', vs)
        (status, data) = self.is_valid_out(data)
        if isinstance(data, list):
            for d in data: print d
        else: return VM(data)

    def generic_get_create_params(self, resource):
        obj = getattr(sys.modules[__name__], resource)()
        return obj.get_create_params()

    def generic_get_columns(self, resource):
        obj = getattr(sys.modules[__name__], resource)()
        return obj.get_columns()

    def generic_return_table(self, data, obj, columns):
        ocol = obj().get_columns()
        tcol = []
        for c in columns:
            if c in ocol:
                tcol.append({ 'column' : c, 'description' : ocol[c]})

        pt = PrettyTable([c['description'] for c  in tcol])
        pt.align = 'l'
        for rd in data:
            o = obj(rd, api = self )
            row = []
            for c in tcol:
                attr = getattr(o, c['column'])
                if callable(attr):
                    row.append(attr())
                else:
                    if hasattr(attr, 'get_value'): row.append(attr.get_value())
                    else: 
                        if type(attr) == list:
                            row.append(', '.join([a.__str__() for a in attr]))
                        else:
                            row.append(attr)

            pt.add_row(row)
        return pt

    def template_list(self, columns = None, types = 'all', user_id = None):
        if types in [ 'all', 'own', 'user', 'inactive' ]:
            (status, data) = self.get_data('templates/%s.json' % types)
        elif types == 'system':
            (status, data) = self.get_data('templates.json')
        elif types == 'userid':
            if not user_id: return False
            (status, data) = self.get_data('templates/user/%s.json' % user_id)

        if not columns:
            columns = [ 'label', 'id', 'version', 'operating_system', 'virtualization' ]

        if status:
            return self.generic_return_table(data, Template, columns)

    def dszone_list(self, columns):
        (status, data) = self.get_data('settings/data_store_zones.json')

        if status:
            if not columns:
                columns = [ 'label', 'id' ]

            return self.generic_return_table(data, DSZone, columns)

    def dszone_info(self, data_store_zone_id):
        (status, data) = self.get_data('settings/data_store_zones/%s.json' % data_store_zone_id)
        if status:
            return DSZone(data)

    def dszone_create(self):
        return 'hola'

    def ds_list(self, columns = None):
        (status, data) = self.get_data('settings/data_stores.json')

        if status:
            if not columns:
                columns = [ 'label', 'id' ]
            return self.generic_return_table(data, DS, columns)

    def netzone_list(self, columns):
        (status, data) = self.get_data('settings/network_zones.json')
        if status:
            if not columns:
                columns = [ 'label', 'id' ]
            return self.generic_return_table(data, NetworkZone, columns)

    def alerts(self):
        (status, data) = self.get_data('alerts.json')
        if status:
            print 'zombie_data_stores: %s ' % data['alerts']['zombie_data_stores']
            print 'zombie_disks: %s ' % data['alerts']['zombie_disks']
            print 'zombie_domains: %s ' % data['alerts']['zombie_domains']
            print 'zombie_transactions: %s ' % data['alerts']['zombie_transactions']

    def onapp_version(self):
        (status, data) = self.get_data('version.json')
        if status: return "OnApp Version: %s" % data['version']

    def usage(self):
        (status, data) = self.get_data('usage_statistics.json')
        if status:
            pt = PrettyTable([ 'User ID', 'VS ID', 'CPU Used', 'Disk reads', 'Disk writes', 'Data read', 'Data written', 'BW Sent', 'BW Received' ])
            pt.align['User ID'] = 'l'
            pt.align['VS ID'] = 'l'
            pt.align['CPU Used'] = 'r'
            pt.align['Disk reads'] = 'r'
            pt.align['Disk writes'] = 'r'
            pt.align['Data read'] = 'r'
            pt.align['Data written'] = 'r'
            pt.align['BW Sent'] = 'r'
            pt.align['BW Received'] = 'r'
            for d in data:
                u = Usage(d, api = self)
                pt.add_row([ u.user if u.user else u.user_id, u.vm if u.vm else u.virtual_machine_id, u.cpu_usage, u.reads_completed, u.writes_completed, u.data_read, u.data_written, u.data_sent, u.data_received ])
            return pt

    def disk_list(self, data = None):
        if not data: (status, data) = self.get_data('settings/disks.json')
        else: (status, data) = data
        if status:
            disks = []
            pt = PrettyTable([ 'ID', 'Label', 'Size', 'Data Store', 'VS', 'FS', 'Type', 'Mounted', 'Built', 'Auto-Backup' ])
            for da in data:
                d = Disk(da, api = self)
                #disks.append(d)
                if d.primary: 
                    disktype = 'Primary'
                    mounted = 'Yes'
                elif d.is_swap: 
                    disktype = 'Swap'
                    mounted = 'Yes'
                elif d.mount_point: 
                    disktype = 'Secondary'
                    mounted = 'Yes'
                else: 
                    disktype = 'Unknown'
                    disktype = 'No'
                pt.add_row( [ d.id, d.label, '%s GB' % d.disk_size, d.data_store_id, d.vm.label if d.vm is not None else d.virtual_machine_id, d.file_system, disktype, mounted, 'Yes' if d.built else 'No', 'Yes' if d.has_autobackups  else 'No' ])

            return pt

    def disk_usage(self, disk_id):
        (status, data) = self.get_data('settings/disks/%s/usage.json' % disk_id)
        if status: 
            pt = PrettyTable(['User ID', 'VS ID', 'Disk ID', 'Data Read', 'Data Written', 'Reads completed', 'Writes completed', 'Stat Time' ])
            for d in data:
                du = DiskUsage(d, api = self)
                pt.add_row( [ u'%s' % du.user if du.user else du.user_id, du.vm if du.vm else du.virtual_machine_id, u'%s' % du.disk if du.disk else du.disk_id, du.data_read, du.data_written, du.reads_completed, du.writes_completed, du.stat_time ] )

            return pt
                
    def disk_list_vs(self, vm_id, out = True, columns = None):
        return self.disk_list(data = self.get_data('virtual_machines/%s/disks.json' % vm_id))

    def disk_create(self, vm_id, data_store_id, label, primary, disk_size, is_swap, mount_point, hot_attach, min_iops, add_to_linux_fstab, add_to_freebsd_fstab, require_format_disk, file_system):
        disk = {
                'primary' : primary,
                'disk_size' : disk_size,
                'file_system' : file_system,
                'data_store_id' : data_store_id,
                'label' : label,
                'require_format_disk' : require_format_disk,
                'mount_point' : mount_point,
                'hot_attach' : hot_attach,
                'min_iops' : min_iops,
                'add_to_linux_fstab' : add_to_linux_fstab,
                'add_to_freebsd_fstab' : add_to_freebsd_fstab
                }
        data = self.exec_url('virtual_machines/%s/disks.json' % vm_id, 'POST', { 'disk' : disk })
        (status, data) = self.is_valid_out(data)
        if status:
            disk = Disk(data)
            print vars(disk)

    def disk_delete(self, vm_id, disk_id):
        (status, data) = self.exec_url('virtual_machines/%s/disks/%s.json' % (vm_id, disk_id), 'DELETE')
        if status: print 'OK'

    def user_list(self, columns = None):
        (status, data) = self.get_data('users.json')
        if status:
            if not columns:
                columns = [ 'id', 'full_name', 'login', 'user_group_id', 'status' ]
            return self.generic_return_table(data, User, columns)

    def user_info(self, user_id):
        (status, data) = self.get_data('users/%s.json' % user_id)
        if status:
            return User(data, api = self)

    def billing_plan_list(self):
        (status, data) = self.get_data('billing_plans.json')
        if status:
            pt = PrettyTable(['ID', 'Label', 'Currency', 'Resources' ])
            pt.align = 'l'
            for d in data:
                bp = BillingPlan( jsondata = d, api = self)
                rs = '\n'.join([value.label for value in bp.base_resources])
                pt.add_row([ bp.id, bp.label, bp.currency_code, rs ])
            return pt

    def recurse_pt(self, obj):
        table = PrettyTable()
        table.header = False
        table.align = 'l'
        length = 0
        for var in vars(obj):
            if var != 'api':
                length = +1
                value = getattr(obj, var)
                if type(value) == list:
                    for child in value:
                        table.add_row([ var, self.recurse_pt( child ) ])
                elif '<class' == str(type(value))[:6]:
                    table.add_row([ var, self.recurse_pt(value) ])
                else:
                    table.add_row([ var, value ])

        if length > 0: return table
        else: return None


    def billing_plan_info(self, billing_plan_id):
        (status, data) = self.get_data('billing_plans/%s.json' % billing_plan_id)
        if status:
            bp = BillingPlan( jsondata = data )
            table = self.recurse_pt( obj = bp )
            return table

    def backup_vs_list(self, vm_id, columns = None):
        (status, data) = self.get_data('virtual_machines/%s/backups.json' % vm_id)
        if status:
            if not columns:
                columns = [ 'id', 'identifier', 'backup_size', 'created_at' ]
            return self.generic_return_table(data, Backup, columns)
