import time
import datetime

from sfa.util.faults import MissingSfaInfo, UnknownSfaType, \
    RecordNotFound, SfaNotImplemented, SfaInvalidArgument, UnsupportedOperation

from sfa.util.sfalogging import logger
from sfa.util.defaultdict import defaultdict
from sfa.util.sfatime import utcparse, datetime_to_string, datetime_to_epoch
from sfa.util.xrn import Xrn, hrn_to_urn, get_leaf 
from sfa.openstack.osxrn import OSXrn, hrn_to_os_slicename, hrn_to_os_tenant_name
from sfa.util.cache import Cache
from sfa.trust.credential import Credential
# used to be used in get_ticket
#from sfa.trust.sfaticket import SfaTicket
from sfa.rspecs.version_manager import VersionManager
from sfa.rspecs.rspec import RSpec
from sfa.storage.model import RegRecord, SliverAllocation

# the driver interface, mostly provides default behaviours
from sfa.managers.driver import Driver
from sfa.openstack.shell import Shell
from sfa.openstack.osaggregate import OSAggregate
from sfa.planetlab.plslices import PlSlices

def list_to_dict(recs, key):
    """
    convert a list of dictionaries into a dictionary keyed on the 
    specified dictionary key 
    """
    return dict ( [ (rec[key],rec) for rec in recs ] )

#
# PlShell is just an xmlrpc serverproxy where methods
# can be sent as-is; it takes care of authentication
# from the global config
# 
class NovaDriver(Driver):

    # the cache instance is a class member so it survives across incoming requests
    cache = None

    def __init__ (self, api):
        Driver.__init__(self, api)
        config = api.config
        self.shell = Shell(config=config)
        self.cache=None
        if config.SFA_AGGREGATE_CACHING:
            if NovaDriver.cache is None:
                NovaDriver.cache = Cache()
            self.cache = NovaDriver.cache

    def sliver_to_slice_xrn(self, xrn):
        sliver_id_parts = Xrn(xrn).get_sliver_id_parts()
        slice = self.shell.auth_manager.tenants.find(id=sliver_id_parts[0])
        if not slice:
            raise Forbidden("Unable to locate slice record for sliver:  %s" % xrn)
        slice_xrn = OSXrn(name=slice.name, type='slice')
        return slice_xrn

    def check_sliver_credentials(self, creds, urns):
        # build list of cred object hrns
        slice_cred_names = []
        for cred in creds:
            slice_cred_hrn = Credential(cred=cred).get_gid_object().get_hrn()
            slice_cred_names.append(OSXrn(xrn=slice_cred_hrn).get_slicename())

        # look up slice name of slivers listed in urns arg
        slice_ids = []
        for urn in urns:
            sliver_id_parts = Xrn(xrn=urn).get_sliver_id_parts()
            slice_ids.append(sliver_id_parts[0])

        if not slice_ids:
             raise Forbidden("sliver urn not provided")

        sliver_names = []
        for slice_id in slice_ids:
            slice = self.shell.auth_manager.tenants.find(slice_id) 
            sliver_names.append(slice['name'])

        # make sure we have a credential for every specified sliver ierd
        for sliver_name in sliver_names:
            if sliver_name not in slice_cred_names:
                msg = "Valid credential not found for target: %s" % sliver_name
                raise Forbidden(msg)
 
    ########################################
    ########## registry oriented
    ########################################

    ########## disabled users 
    def is_enabled (self, record):
        # all records are enabled
        return True

    def augment_records_with_testbed_info (self, sfa_records):
        return self.fill_record_info (sfa_records)

    ########## 
    def register (self, sfa_record, hrn, pub_key):
        
        if sfa_record['type'] == 'slice':
            record = self.register_slice(sfa_record, hrn)         
        elif sfa_record['type'] == 'user':
            record = self.register_user(sfa_record, hrn, pub_key)
        elif sfa_record['type'].startswith('authority'): 
            record = self.register_authority(sfa_record, hrn)
        # We should be returning the records id as a pointer but
        # this is a string and the records table expects this to be an 
        # int.
        #return record.id
        return -1

    def register_slice(self, sfa_record, hrn):
        # add slice description, name, researchers, PI
        name = hrn_to_os_tenant_name(hrn)
        description = sfa_record.get('description', None)
        self.shell.auth_manager.tenants.create(name, description)
        tenant = self.shell.auth_manager.tenants.find(name=name)
        auth_hrn = OSXrn(xrn=hrn, type='slice').get_authority_hrn()
        parent_tenant_name = OSXrn(xrn=auth_hrn, type='slice').get_tenant_name()
        parent_tenant = self.shell.auth_manager.tenants.find(name=parent_tenant_name)
        researchers = sfa_record.get('researchers', [])
        for researcher in researchers:
            name = Xrn(researcher).get_leaf()
            user = self.shell.auth_manager.users.find(name=name)
            self.shell.auth_manager.roles.add_user_role(user, 'Member', tenant)
            self.shell.auth_manager.roles.add_user_role(user, 'user', tenant)
            

        pis = sfa_record.get('pis', [])
        for pi in pis:
            name = Xrn(pi).get_leaf()
            user = self.shell.auth_manager.users.find(name=name)
            self.shell.auth_manager.roles.add_user_role(user, 'pi', tenant)
            self.shell.auth_manager.roles.add_user_role(user, 'pi', parent_tenant)

        return tenant
       
    def register_user(self, sfa_record, hrn, pub_key):
        # add person roles, projects and keys
        email = sfa_record.get('email', None)
        xrn = Xrn(hrn)
        name = xrn.get_leaf()
        auth_hrn = xrn.get_authority_hrn()
        tenant_name = OSXrn(xrn=auth_hrn, type='authority').get_tenant_name()  
        tenant = self.shell.auth_manager.tenants.find(name=tenant_name)  
        self.shell.auth_manager.users.create(name, email=email, tenant_id=tenant.id)
        user = self.shell.auth_manager.users.find(name=name)
        slices = sfa_records.get('slices', [])
        for slice in projects:
            slice_tenant_name = OSXrn(xrn=slice, type='slice').get_tenant_name()
            slice_tenant = self.shell.auth_manager.tenants.find(name=slice_tenant_name)
            self.shell.auth_manager.roles.add_user_role(user, slice_tenant, 'user')
        keys = sfa_records.get('keys', [])
        for key in keys:
            keyname = OSXrn(xrn=hrn, type='user').get_slicename()
            self.shell.nova_client.keypairs.create(keyname, key)
        return user

    def register_authority(self, sfa_record, hrn):
        name = OSXrn(xrn=hrn, type='authority').get_tenant_name()
        self.shell.auth_manager.tenants.create(name, sfa_record.get('description', ''))
        tenant = self.shell.auth_manager.tenants.find(name=name)
        return tenant
        
        
    ##########
    # xxx actually old_sfa_record comes filled with plc stuff as well in the original code
    def update (self, old_sfa_record, new_sfa_record, hrn, new_key):
        type = new_sfa_record['type'] 
        
        # new_key implemented for users only
        if new_key and type not in [ 'user' ]:
            raise UnknownSfaType(type)

        elif type == "slice":
            # can update project manager and description
            name = hrn_to_os_slicename(hrn)
            researchers = sfa_record.get('researchers', [])
            pis = sfa_record.get('pis', [])
            project_manager = None
            description = sfa_record.get('description', None)
            if pis:
                project_manager = Xrn(pis[0], 'user').get_leaf()
            elif researchers:
                project_manager = Xrn(researchers[0], 'user').get_leaf()
            self.shell.auth_manager.modify_project(name, project_manager, description)

        elif type == "user":
            # can techinally update access_key and secret_key,
            # but that is not in our scope, so we do nothing.  
            pass
        return True
        

    ##########
    def remove (self, sfa_record):
        type=sfa_record['type']
        if type == 'user':
            name = Xrn(sfa_record['hrn']).get_leaf()     
            if self.shell.auth_manager.get_user(name):
                self.shell.auth_manager.delete_user(name)
        elif type == 'slice':
            name = hrn_to_os_slicename(sfa_record['hrn'])     
            if self.shell.auth_manager.get_project(name):
                self.shell.auth_manager.delete_project(name)
        return True


    ####################
    def fill_record_info(self, records):
        """
        Given a (list of) SFA record, fill in the PLC specific 
        and SFA specific fields in the record. 
        """
        if not isinstance(records, list):
            records = [records]

        for record in records:
            if record['type'] == 'user':
                record = self.fill_user_record_info(record)
            elif record['type'] == 'slice':
                record = self.fill_slice_record_info(record)
            elif record['type'].startswith('authority'):
                record = self.fill_auth_record_info(record)
            else:
                continue
            record['geni_urn'] = hrn_to_urn(record['hrn'], record['type'])
            record['geni_certificate'] = record['gid'] 
            #if os_record.created_at is not None:    
            #    record['date_created'] = datetime_to_string(utcparse(os_record.created_at))
            #if os_record.updated_at is not None:
            #    record['last_updated'] = datetime_to_string(utcparse(os_record.updated_at))
 
        return records

    def fill_user_record_info(self, record):
        xrn = Xrn(record['hrn'])
        name = xrn.get_leaf()
        record['name'] = name
        user = self.shell.auth_manager.users.find(name=name)
        record['email'] = user.email
        tenant = self.shell.auth_manager.tenants.find(id=user.tenantId)
        slices = []
        all_tenants = self.shell.auth_manager.tenants.list()
        for tmp_tenant in all_tenants:
            if tmp_tenant.name.startswith(tenant.name +"."):
                for tmp_user in tmp_tenant.list_users():
                    if tmp_user.name == user.name:
                        slice_hrn = ".".join([self.hrn, tmp_tenant.name]) 
                        slices.append(slice_hrn)   
        record['slices'] = slices
        roles = self.shell.auth_manager.roles.roles_for_user(user, tenant)
        record['roles'] = [role.name for role in roles] 
        keys = self.shell.nova_manager.keypairs.findall(name=record['hrn'])
        record['keys'] = [key.public_key for key in keys]
        return record

    def fill_slice_record_info(self, record):
        tenant_name = hrn_to_os_tenant_name(record['hrn'])
        tenant = self.shell.auth_manager.tenants.find(name=tenant_name)
        parent_tenant_name = OSXrn(xrn=tenant_name).get_authority_hrn()
        parent_tenant = self.shell.auth_manager.tenants.find(name=parent_tenant_name)
        researchers = []
        pis = []

        # look for users and pis in slice tenant
        for user in tenant.list_users():
            for role in self.shell.auth_manager.roles.roles_for_user(user, tenant):
                if role.name.lower() == 'pi':
                    user_tenant = self.shell.auth_manager.tenants.find(id=user.tenantId)
                    hrn = ".".join([self.hrn, user_tenant.name, user.name])
                    pis.append(hrn)
                elif role.name.lower() in ['user', 'member']:
                    user_tenant = self.shell.auth_manager.tenants.find(id=user.tenantId)
                    hrn = ".".join([self.hrn, user_tenant.name, user.name])
                    researchers.append(hrn)

        # look for pis in the slice's parent (site/organization) tenant
        for user in parent_tenant.list_users():
            for role in self.shell.auth_manager.roles.roles_for_user(user, parent_tenant):
                if role.name.lower() == 'pi':
                    user_tenant = self.shell.auth_manager.tenants.find(id=user.tenantId)
                    hrn = ".".join([self.hrn, user_tenant.name, user.name])
                    pis.append(hrn)
        record['name'] = tenant_name
        record['description'] = tenant.description
        record['PI'] = pis
        if pis:
            record['geni_creator'] = pis[0]
        else:
            record['geni_creator'] = None
        record['researcher'] = researchers
        return record

    def fill_auth_record_info(self, record):
        tenant_name = hrn_to_os_tenant_name(record['hrn'])
        tenant = self.shell.auth_manager.tenants.find(name=tenant_name)
        researchers = []
        pis = []

        # look for users and pis in slice tenant
        for user in tenant.list_users():
            for role in self.shell.auth_manager.roles.roles_for_user(user, tenant):
                hrn = ".".join([self.hrn, tenant.name, user.name])
                if role.name.lower() == 'pi':
                    pis.append(hrn)
                elif role.name.lower() in ['user', 'member']:
                    researchers.append(hrn)

        # look for slices
        slices = []
        all_tenants = self.shell.auth_manager.tenants.list() 
        for tmp_tenant in all_tenants:
            if tmp_tenant.name.startswith(tenant.name+"."):
                slices.append(".".join([self.hrn, tmp_tenant.name])) 

        record['name'] = tenant_name
        record['description'] = tenant.description
        record['PI'] = pis
        record['enabled'] = tenant.enabled
        record['researchers'] = researchers
        record['slices'] = slices
        return record

    ####################
    # plcapi works by changes, compute what needs to be added/deleted
    def update_relation (self, subject_type, target_type, subject_id, target_ids):
        # hard-wire the code for slice/user for now, could be smarter if needed
        if subject_type =='slice' and target_type == 'user':
            subject=self.shell.project_get(subject_id)[0]
            current_target_ids = [user.name for user in subject.members]
            add_target_ids = list ( set (target_ids).difference(current_target_ids))
            del_target_ids = list ( set (current_target_ids).difference(target_ids))
            logger.debug ("subject_id = %s (type=%s)"%(subject_id,type(subject_id)))
            for target_id in add_target_ids:
                self.shell.project_add_member(target_id,subject_id)
                logger.debug ("add_target_id = %s (type=%s)"%(target_id,type(target_id)))
            for target_id in del_target_ids:
                logger.debug ("del_target_id = %s (type=%s)"%(target_id,type(target_id)))
                self.shell.project_remove_member(target_id, subject_id)
        else:
            logger.info('unexpected relation to maintain, %s -> %s'%(subject_type,target_type))

        
    ########################################
    ########## aggregate oriented
    ########################################

    def testbed_name (self): return "openstack"

    def aggregate_version (self):
        return {}

    # first 2 args are None in case of resource discovery
    def list_resources (self, version=None, options=None):
        if options is None: options={}
        aggregate = OSAggregate(self)
        rspec =  aggregate.list_resources(version=version, options=options)
        return rspec

    def describe(self, urns, version=None, options=None):
        if options is None: options={}
        aggregate = OSAggregate(self)
        return aggregate.describe(urns, version=version, options=options)
    
    def status (self, urns, options=None):
        if options is None: options={}
        aggregate = OSAggregate(self)
        desc =  aggregate.describe(urns)
        status = {'geni_urn': desc['geni_urn'],
                  'geni_slivers': desc['geni_slivers']}
        return status

    def allocate (self, urn, rspec_string, expiration, options=None):
        if options is None: options={}
        xrn = Xrn(urn) 
        aggregate = OSAggregate(self)

        # assume first user is the caller and use their context
        # for the ec2/euca api connection. Also, use the first users
        # key as the project key.
        key_name = None
        if len(users) > 1:
            key_name = aggregate.create_instance_key(xrn.get_hrn(), users[0])

        # collect public keys
        users = options.get('geni_users', [])
        pubkeys = []
        for user in users:
            pubkeys.extend(user['keys'])
           
        rspec = RSpec(rspec_string)
        instance_name = hrn_to_os_slicename(slice_hrn)
        tenant_name = OSXrn(xrn=slice_hrn, type='slice').get_tenant_name()
        slivers = aggregate.run_instances(instance_name, tenant_name, \
                                          rspec_string, key_name, pubkeys)
        
        # update all sliver allocation states setting then to geni_allocated    
        sliver_ids = [sliver.id for sliver in slivers]
        dbsession=self.api.dbsession()
        SliverAllocation.set_allocations(sliver_ids, 'geni_provisioned',dbsession)
   
        return aggregate.describe(urns=[urn], version=rspec.version)

    def provision(self, urns, options=None):
        if options is None: options={}
        # update sliver allocation states and set them to geni_provisioned
        aggregate = OSAggregate(self)
        instances = aggregate.get_instances(urns)
        sliver_ids = []
        for instance in instances:
            sliver_hrn = "%s.%s" % (self.driver.hrn, instance.id)
            sliver_ids.append(Xrn(sliver_hrn, type='sliver').urn)
        dbsession=self.api.dbsession()
        SliverAllocation.set_allocations(sliver_ids, 'geni_provisioned',dbsession) 
        version_manager = VersionManager()
        rspec_version = version_manager.get_version(options['geni_rspec_version'])
        return self.describe(urns, rspec_version, options=options) 

    def delete (self, urns, options=None):
        if options is None: options={}
        # collect sliver ids so we can update sliver allocation states after
        # we remove the slivers.
        aggregate = OSAggregate(self)
        instances = aggregate.get_instances(urns)
        sliver_ids = []
        for instance in instances:
            sliver_hrn = "%s.%s" % (self.driver.hrn, instance.id)
            sliver_ids.append(Xrn(sliver_hrn, type='sliver').urn)
            
            # delete the instance
            aggregate.delete_instance(instance)
            
        # delete sliver allocation states
        dbsession=self.api.dbsession()
        SliverAllocation.delete_allocations(sliver_ids, dbsession)

        # return geni_slivers
        geni_slivers = []
        for sliver_id in sliver_ids:
            geni_slivers.append(
                {'geni_sliver_urn': sliver['sliver_id'],
                 'geni_allocation_status': 'geni_unallocated',
                 'geni_expires': None})        
        return geni_slivers

    def renew (self, urns, expiration_time, options=None):
        if options is None: options={}
        description = self.describe(urns, None, options)
        return description['geni_slivers']

    def perform_operational_action  (self, urns, action, options=None):
        if options is None: options={}
        aggregate = OSAggregate(self)
        action = action.lower() 
        if action == 'geni_start':
            action_method = aggregate.start_instances
        elif action == 'geni_stop':
            action_method = aggregate.stop_instances
        elif action == 'geni_restart':
            action_method = aggreate.restart_instances
        else:
            raise UnsupportedOperation(action)

         # fault if sliver is not full allocated (operational status is geni_pending_allocation)
        description = self.describe(urns, None, options)
        for sliver in description['geni_slivers']:
            if sliver['geni_operational_status'] == 'geni_pending_allocation':
                raise UnsupportedOperation(action, "Sliver must be fully allocated (operational status is not geni_pending_allocation)")
        #
        # Perform Operational Action Here
        #

        instances = aggregate.get_instances(urns) 
        for instance in instances:
            tenant_name = self.driver.shell.auth_manager.client.tenant_name
            action_method(tenant_name, instance.name, instance.id)
        description = self.describe(urns)
        geni_slivers = self.describe(urns, None, options)['geni_slivers']
        return geni_slivers

    def shutdown(self, xrn, options=None):
        if options is None: options={}
        xrn = OSXrn(xrn=xrn, type='slice')
        tenant_name = xrn.get_tenant_name()
        name = xrn.get_slicename()
        self.driver.shell.nova_manager.connect(tenant=tenant_name)
        instances = self.driver.shell.nova_manager.servers.findall(name=name)
        for instance in instances:
            self.driver.shell.nova_manager.servers.shutdown(instance)
        return True
