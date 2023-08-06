class OnAppAttribute(object):
    # Attribute Value
    value = None
    # Attribute type
    vartype = str
    # Required atribute in create cli params
    cli_create_required = False
    # Attribute available in create cli params
    cli_create = False
    # Required atribute in edit cli params
    cli_edit_required = False
    # Attribute available in edit cli params
    cli_edit = False
    # Attribute available in list cli
    cli_list = True
    # Header of list table
    list_title = None
    # Description of attribute
    description = None
    # Help on create/edit cli params
    usage = None
    # List of available choices
    choices = []
    # Default vlaue
    default = None

    def __init__(self, value = None, vartype = str, cli_create_required = False, cli_create = False, cli_edit_required = False, cli_edit = False, cli_list = True, list_title = None, description = None, usage = None, choices = [], default = None):
        self.value = value
        self.vartype = vartype
        self.cli_create_required = cli_create_required
        self.cli_create = cli_create
        self.cli_edit_required = cli_edit_required
        self.cli_edit = cli_edit
        self.cli_list = cli_list
        self.list_title = list_title
        self.description = description
        self.usage = usage
        self.choices = choices
        self.default = default

    def set_value(self, value):
        # TO-DO verify data type
        self.value = value

    def get_value(self): return self.value

    def __str__(self): return '%s' % self.value    
    def __unicode__(self): return u'%s' % self.value
    def __repr__(self): return '<Attribute Value: %s>' % self.value


class OnAppJsonObject(object):
    api = None
    def __init__(self, jsondata = None, name = None, api = None):
        self.api = api
        if jsondata and name:
            if name in jsondata:
                jsondata = jsondata[name]

            for name, value in jsondata.items():
                if hasattr(self, name):
                    attr = getattr(self, name)
                    if type(attr) == OnAppAttribute:
                        attr.set_value(value)
                        setattr(self, name, attr)
                    else:
                        setattr(self, name, value)

    def valid_attr(self, attr_name):
        if attr_name not in [ 'get_methods', 'get_create_params', 'valid_attr', 'api', 'get_columns' ] and attr_name[:2] != '__' and attr_name[:4] != 'url_': return True
        return False

    def get_create_params(self):
        args = []
        for c in dir(self):
            if self.valid_attr(c):
                attr = getattr(self, c)
                if attr.cli_create:
                    arg = { 
                            'args' : '--%s' % c,
                            'options' : {
                                'required' : attr.cli_create_required,
                                'type' : attr.vartype,
                                'dest' : c,
                                'metavar' : attr.description,
                                'help' : attr.usage,
                                'choices' : attr.choices,
                                'default' : attr.default,
                                }
                            }
                    args.append(arg)
        return args


    def get_columns(self):
        columns = {}
        for c in dir(self):
            if self.valid_attr(c):
                attr = getattr(self, c)
                if type(attr) == OnAppAttribute:
                    if attr.list_title:
                        columns[c] = attr.list_title
                    else:
                        columns[c] = c.title().replace('_',' ')
                else:
                    columns[c] = c.title().replace('_',' ')
        return columns

    def get_methods(self):
        methods = []
        for c in dir(self):
            if c not in [ 'get_methods', 'get_columns', 'get_create_params' ] and attr_name[:2] != '__':
                methods.append(c)
        return methods

class Backup(OnAppJsonObject):
    allowed_resize_without_reboot = None
    allowed_hot_migrate = None
    allowed_swap = None
    backup_server_id = None
    backup_size = None
    backup_type = None
    built = None
    built_at = None
    created_at = None
    updated_at = None
    data_store_type = None
    id = None
    identifier = None
    image_type = None
    initiated = None
    locked = None
    marked_for_delete = None
    min_disk_size = None
    operating_system_distro = None
    operating_system = None
    target_id = None
    target_type = None
    template_id = None
    user_id = None
    volume_id = None
    iqn = None

    def __init__(self, jsondata = None, name = 'backup', api = None):
        super(Backup, self).__init__(jsondata, name, api)

class BaseResourcesLimits(OnAppJsonObject):
    limit_rate_free = None
    limit_ip_free = None    
    limit_data_sent_free = None
    limit_data_received_free = None
    limit_rate = None
    limit_ip = None
    limit_free_cpu = None
    limit_free_cpu_share = None
    limit_free_memory = None
    limit_cpu = None
    limit_cpu_share = None
    limit_memory = None
    limit_default_cpu = None
    limit_default_cpu_share = None
    limit_cpu_units = None
    limit_free_cpu_units = None


    def __init__(self, jsondata = None, name = 'limits', api = None):
        super(BaseResourcesLimits, self).__init__(jsondata, name, api)

class BaseResourcesPrices(OnAppJsonObject):
    price_off = None
    price_writes_completed = None
    price_on = None
    price_reads_completed = None
    price_data_written = None
    price_data_read = None
    price_rate_on = None
    price_rate_off = None
    price_ip_on = None
    price_ip_off = None
    price_data_sent = None
    price_data_received = None
    price = None
    price_on_cpu_share = None
    price_on_cpu = None
    price_off_cpu = None
    price_off_cpu_share = None
    price_on_memory = None
    price_off_cpu_units = None
    price_on_cpu_units = None
    price_off_memory = None

    def __init__(self, jsondata = None, name = 'prices', api = None):
        super(BaseResourcesPrices, self).__init__(jsondata, name, api)

class BaseResourcesPreferences(OnAppJsonObject):
    use_default_cpu_share = None
    use_default_cpu = None
    use_cpu_units = None

    def __init__(self, jsondata = None, name = 'preferences', api = None):
        super(BaseResourcesPreferences, self).__init__(jsondata, name, api)

class BaseResource(OnAppJsonObject):
    resource_name = None
    is_bucket = None
    preferences = None
    limits = None
    billing_plan_id = None
    created_at = None
    target_id = None
    in_bucket_zone = None
    limit_type = None
    updated_at = None
    is_template = None
    limits = None
    prices = None
    in_template_zone = None
    label = None
    id = None
    unit = None

    def __init__(self, jsondata = None, name = 'base_resource', api = None):
        super(BaseResource, self).__init__(jsondata, name, api)
        if self.prices != {}: self.prices = BaseResourcesPrices( jsondata = self.prices )
        else: self.prices = None

        if self.limits != {}: self.limits = BaseResourcesLimits( jsondata = self.limits )
        else: self.limits = None

        if self.preferences != {}: self.preferences = BaseResourcesPreferences( jsondata = self.preferences )
        else: self.preferences = None

class BillingPlan(OnAppJsonObject):
    allows_kms = None
    allows_mak = None
    allows_own = None
    created_at = None
    currency_code = None
    id = None
    label = None
    monthly_price = None
    show_price = None
    updated_at = None
    associated_with_users = None
    base_resources = []

    def __init__(self, jsondata = None, name = 'billing_plan', api = None):
        super(BillingPlan, self).__init__(jsondata, name, api)

        base_resources = []
        for resource in self.base_resources:
            base_resources.append( BaseResource( jsondata = resource ) )
        self.base_resources = base_resources

class DiskUsage(OnAppJsonObject):
    disk_id = None
    created_at = None
    updated_at = None
    data_read = None
    data_written = None
    stat_time = None
    writes_completed = None
    reads_completed = None
    user_id = None
    virtual_machine_id = None

    vm = None
    user = None
    disk = None

    def __init__(self, jsondata = None, name = 'disk_hourly_stat', api = None):
        super(DiskUsage, self).__init__(jsondata, name, api)
        if self.data_read: self.data_read = u'%.2f' % float((float(self.data_read) / 1024) / 3600)
        if self.data_written: self.data_written = u'%.2f' % float((float(self.data_written) / 1024) / 3600)

        if self.api:
            if self.virtual_machine_id: self.vm = api.vm_info( self.virtual_machine_id )
            if self.user_id: self.user = api.user_info( user_id = self.user_id )
            if self.disk_id:
                disks = self.api.disk_list_vs( vm_id = self.virtual_machine_id, out = False )
                for disk in disks._rows:
                    if disk[0] == self.disk_id:
                        self.disk = disk[1]

class Disk(OnAppJsonObject):
    primary = None
    virtual_machine_id = None
    has_autobackups = None
    id = None
    mount_point = None
    built = None
    label = None
    max_iops = None
    burst_iops = None
    is_swap = None
    add_to_linux_fstab = None
    disk_vm_number = None
    burst_bw = None
    data_store_id = None
    updated_at = None
    max_bw = None
    volume_id = None
    disk_size = None
    min_iops = None
    file_system = None
    locked = None
    created_at = None
    add_to_freebsd_fstab = None
    iqn = None
    identifier = None

    vm = None

    def __init__(self, jsondata = None, name = 'disk', api = None):
        super(Disk, self).__init__(jsondata, name, api)

        if self.api:
            if self.virtual_machine_id:
                self.vm = api.vm_info(self.virtual_machine_id)

    def __unicode__(self):
        return u'%s' % self.label

class Usage(OnAppJsonObject):
    cpu_usage = None
    user_id = None
    writes_completed = None
    data_received = None
    data_sent = None
    data_read = None
    virtual_machine_id = None
    reads_completed = None
    data_written = None

    vm = None

    def __init__(self, jsondata = None, name = 'vm_stat', api = None):
        super(Usage, self).__init__(jsondata, name, api)

        if self.api:
            if self.virtual_machine_id and self.virtual_machine_id > 0: self.vm = self.api.vm_info(self.virtual_machine_id)
            if self.user_id: self.user = api.user_info( user_id = self.user_id )

class Log(OnAppJsonObject):
    status = None
    created_at = None
    target_id = None
    updated_at = None
    target_type = None
    action = None
    id = None
    def __init__(self, jsondata = None, name = 'log_item', api = None):
        super(Log, self).__init__(jsondata, name, api)

class DS(OnAppJsonObject):
    data_store_group_id = None
    data_store_size = None
    created_at = None
    enabled = None
    updated_at = None
    label = None
    zombie_disks_size = None
    hypervisor_group_id = None
    data_store_type = None
    ip = None
    usage = None
    identifier = None
    local_hypervisor_id = None
    id = None
    iscsi_ip = None

    data_store_group = None

    def __init__(self, jsondata = None, name = 'data_store', api = None):
        super(DS, self).__init__(jsondata, name, api)

        if self.api:
            if self.data_store_group_id: self.data_store_group = self.api.dszone_info( data_store_zone_id = self.data_store_group_id )

    def __str__(self):
        return u'%s' % self.label

class DSZone(OnAppJsonObject):
    default_max_iops = OnAppAttribute()
    min_disk_size = OnAppAttribute()
    created_at = OnAppAttribute()
    updated_at = OnAppAttribute()
    default_burst_iops = OnAppAttribute()
    label = OnAppAttribute( cli_create = True, cli_create_required = True, cli_edit = True, cli_edit_required = True, description = 'DataStore Zone Label', usage = 'Name of DataStore Zone', list_title = 'DataStore Zone Label')
    federation_enabled = OnAppAttribute()
    federation_id = OnAppAttribute()
    closed = OnAppAttribute()
    location_group_id = OnAppAttribute( cli_create = True, cli_edit = True, description = 'Location')
    traded = OnAppAttribute()
    id = OnAppAttribute()

    def __init__(self, jsondata = None, name = 'data_store_group', api = None):
        super(DSZone, self).__init__(jsondata, name, api)

    def __str__(self):
        return '%s' % self.label

    def __unicode__(self):
        return u'%s' % self.label


class NetworkZone(OnAppJsonObject):
    created_at = None
    label = None
    closed = None
    location_group_id = None
    updated_at = None
    federation_enabled = None
    federation_id = None
    location_group_id =None 
    traded = None
    id = None

    def __init__(self, jsondata = None, name = 'network_group', api = None):
        print jsondata
        super(NetworkZone, self).__init__(jsondata, name, api)

    def __str__(self):
        return '%s' % self.label

    def __unicode__(self):
        return u'%s' % self.label


class IPAddr(OnAppJsonObject):
    address = None
    broadcast = None
    created_at = None
    customer_network_id = None
    disallowed_primary = False
    free = False
    gateway = None
    hypervisor_id = None
    id = None
    ip_address_pool_id = None
    netmask = None
    network_address = None
    network_id = None
    pxe = None
    updated_at = None
    user_id = None

    def __init__(self, jsondata = None, name = 'ip_address', api = None):
        super(IPAddr, self).__init__(jsondata, name, api)


    def __str__(self): return '%s' % self.address
    def __unicode__(self): return u'%s' % self.address


class Template(OnAppJsonObject):
    file_name = None
    cdn = None
    updated_at = None
    template_size = None
    virtualization = None
    operating_system_arch = None
    id = None
    ext4 = None
    disk_target_device = None
    operating_system_edition = None
    remote_id = None
    allow_resize_without_reboot = None
    label = None
    parent_template_id = None
    state = None
    version = None
    manager_id = None
    baremetal_server = None
    initial_password = None
    operating_system_tail = None
    smart_server = None
    min_memory_size = None
    operating_system_distro = None
    min_disk_size = None
    operating_system = None
    user_id = None
    backup_server_id = None
    checksum = None
    created_at = None
    resize_without_reboot_policy = None
    allowed_hot_migrate = None
    allowed_swap = None
    initial_username = None

    def __init__(self, jsondata = None, name = 'image_template', api = None):
        super(Template, self).__init__(jsondata, name, api)

class VM(OnAppJsonObject):
    # Object Parameters
    id = OnAppAttribute()
    memory = OnAppAttribute( list_title = 'Memory (MB)')
    cpus = OnAppAttribute()
    cpu_shares = OnAppAttribute()
    cpu_sockets = OnAppAttribute()
    cpu_threads = OnAppAttribute()
    hostname = OnAppAttribute()
    label = OnAppAttribute()
    preferred_hvs = OnAppAttribute()
    remote_access_password = OnAppAttribute()
    recovery_mode = OnAppAttribute()
    suspended = OnAppAttribute()
    cpu_priority = OnAppAttribute()
    updated_at = OnAppAttribute()
    ip_addresses = OnAppAttribute()
    add_to_marketplace = OnAppAttribute()
    vip = OnAppAttribute()
    initial_root_password_encrypted = OnAppAttribute()
    local_remote_access_ip_address = OnAppAttribute()
    total_disk_size = OnAppAttribute( list_title = 'Total Disk (GB)' )
    deleted_at = OnAppAttribute()
    support_incremental_backups = OnAppAttribute()
    template_label = OnAppAttribute()
    operating_system_distro = OnAppAttribute()
    built = OnAppAttribute()
    price_per_hour_powered_off = OnAppAttribute()
    allow_resize_without_reboot = OnAppAttribute()
    note = OnAppAttribute()
    state = OnAppAttribute()
    local_remote_access_port = OnAppAttribute()
    monthly_bandwidth_used = OnAppAttribute()
    price_per_hour = OnAppAttribute()
    initial_root_password = OnAppAttribute()
    storage_server_type = OnAppAttribute()
    admin_note = OnAppAttribute()
    enable_monitis = OnAppAttribute()
    strict_virtual_machine_id = OnAppAttribute()
    user_id = OnAppAttribute()
    edge_server_type = OnAppAttribute()
    min_disk_size = OnAppAttribute()
    customer_network_id = OnAppAttribute()
    operating_system = OnAppAttribute()
    locked = OnAppAttribute()
    service_password = OnAppAttribute()
    created_at = OnAppAttribute()
    firewall_notrack = OnAppAttribute()
    allowed_hot_migrate = OnAppAttribute()
    allowed_swap = OnAppAttribute()
    xen_id = OnAppAttribute()
    booted = OnAppAttribute()
    cpu_units = OnAppAttribute()
    identifier = OnAppAttribute()
    
    # Create
    enable_autoscale = OnAppAttribute( cli_create = True )
    template_id = OnAppAttribute( cli_create = True )
    hypervisor_id = OnAppAttribute( cli_create = True )

    # Create parameters
    data_store_group_primary_id = OnAppAttribute( cli_list = False, cli_create = True )
    primary_disk_size = OnAppAttribute( cli_list = False, cli_create = True )
    primary_disk_min_iops = OnAppAttribute( cli_list = False, cli_create = True )
    data_store_group_swap_id = OnAppAttribute( cli_list = False, cli_create = True )
    swap_disk_size = OnAppAttribute( cli_list = False, cli_create = True )
    swap_disk_min_iops = OnAppAttribute( cli_list = False, cli_create = True )
    primary_network_group_id = OnAppAttribute( cli_list = False, cli_create = True )
    primary_network_id = OnAppAttribute( cli_list = False, cli_create = True )
    selected_ip_address_id = OnAppAttribute( cli_list = False, cli_create = True )
    required_virtual_machine_build = OnAppAttribute( cli_list = False, cli_create = True )
    required_virtual_machine_startup = OnAppAttribute( cli_list = False, cli_create = True )
    required_ip_address_assignment = OnAppAttribute( cli_list = False, cli_create = True )
    required_automatic_backup = OnAppAttribute( cli_list = False, cli_create = True )
    type_of_format = OnAppAttribute( cli_list = False, cli_create = True )
    recipe_ids = OnAppAttribute( cli_list = False, cli_create = True )
    custom_recipe_variables = OnAppAttribute( cli_list = False, cli_create = True )
    initial_root_password = OnAppAttribute( cli_list = False, cli_create = True )
    rate_limit = OnAppAttribute( cli_list = False, cli_create = True )
    hypervisor_group_id = OnAppAttribute( cli_list = False, cli_create = True )
    licensing_server_id = OnAppAttribute( cli_list = False, cli_create = True )
    licensing_type = OnAppAttribute( cli_list = False, cli_create = True )
    licensing_key = OnAppAttribute( cli_list = False, cli_create = True )

    # Optional resources
    user = OnAppAttribute()

    def __init__(self, jsondata = None, name = 'virtual_machine', api = None):
        super(VM, self).__init__(jsondata, name, api)
        if jsondata:
            if 'virtual_machine' in jsondata:
                jsondata = jsondata['virtual_machine']

            ip_obj = []
            for ip in jsondata['ip_addresses']:
                ip_obj.append(IPAddr(ip))
            self.ip_addresses = ip_obj

        if self.api and self.user_id:
            self.user = self.api.user_info( user_id = self.user_id )

    def __str__(self):
        return u'%s' % self.label

class Permission(OnAppJsonObject):
    label = None
    created_at = None
    identifier = None
    updated_at = None
    id = None

    def __init__(self, jsondata = None, name = 'permission', api = None):
        super(Permission, self).__init__(jsondata, name, api)

class Role(OnAppJsonObject):
    created_at = None
    updated_at = None
    label = None
    identifier = None
    id = None
    permissions = []
    def __init__(self, jsondata = None, name = 'role', api = None):
        super(Role, self).__init__(jsondata, name, api)

        if self.api and self.permissions:
            old_permissions = self.permissions
            new_permissions = []
            for p in old_permissions:
                new_permissions.append(Permission(p))
            self.permissions = new_permissions



class User(OnAppJsonObject):
    last_name = None
    billing_plan_id = None
    password_changed_at = None
    updated_at = None
    time_zone = None
    used_cpus = None
    deleted_at = None
    id = None
    cdn_status = None
    additional_fields = None
    first_name = None
    used_memory = None
    used_cpu_shares = None
    supplied = None
    locale = None
    payment_amount = None
    use_gravatar = None
    email = None
    status = None
    used_disk_size = None
    activated_at = None
    outstanding_amount = None
    disk_space_available = None
#    infoboxes": {  "hidden_infoboxes": [],  "display_infoboxes": true }, 
    image_template_group_id = None
    total_amount = None
    roles = []
    created_at = None
    memory_available = None
    used_ip_addresses = None
    firewall_id = None
    avatar = None
    suspend_at = None
    cdn_account_status = None
    login = None
    user_group_id = None
    group_id = None

    def __init__(self, jsondata = None, name = 'user', api = None):
        super(User, self).__init__(jsondata, name, api)

        if self.roles and self.api:
            old_roles = self.roles
            new_roles = []
            for r in old_roles:
                new_roles.append(Role(r, api = self.api))

            self.roles = new_roles

    def __str__(self):
        return '%s %s' % ( self.first_name, self.last_name )

    def __unicode__(self):
        return u'%s %s' % ( self.first_name, self.last_name )

    def full_name(self):
        return '%s %s' % ( self.first_name, self.last_name )
