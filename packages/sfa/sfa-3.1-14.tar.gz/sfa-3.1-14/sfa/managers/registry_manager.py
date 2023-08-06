import types
# for get_key_from_incoming_ip
import tempfile
import os
import commands

from sfa.util.faults import RecordNotFound, AccountNotEnabled, PermissionError, MissingAuthority, \
    UnknownSfaType, ExistingRecord, NonExistingRecord
from sfa.util.sfatime import utcparse, datetime_to_epoch
from sfa.util.prefixTree import prefixTree
from sfa.util.xrn import Xrn, get_authority, hrn_to_urn, urn_to_hrn
from sfa.util.version import version_core
from sfa.util.sfalogging import logger

from sfa.util.printable import printable

from sfa.trust.gid import GID 
from sfa.trust.credential import Credential
from sfa.trust.certificate import Certificate, Keypair, convert_public_key
from sfa.trust.gid import create_uuid

from sfa.storage.model import make_record, RegRecord, RegAuthority, RegUser, RegSlice, RegKey, \
    augment_with_sfa_builtins
### the types that we need to exclude from sqlobjects before being able to dump
# them on the xmlrpc wire
from sqlalchemy.orm.collections import InstrumentedList

### historical note -- april 2014
# the myslice chaps rightfully complained about the following discrepancy
# they found that
# * read operations (resolve) expose stuff like e.g. 
#   'reg-researchers', or 'reg-pis', but that
# * write operations (register, update) need e.g. 
#   'researcher' or 'pi' to be set - reg-* are just ignored
#
# the '_normalize_input' helper functions below aim at ironing this out
# however in order to break as few code as possible we essentially make sure that *both* fields are set
# upon entering the write methods (so again register and update) for legacy, as some driver code
# might depend on the presence of, say, 'researcher'

# normalize an input record to a write method - register or update
# e.g. registry calls this 'reg-researchers'
# while some drivers call this 'researcher'
# we need to make sure that both keys appear and are the same
def _normalize_input (record, reg_key, driver_key):
    # this looks right, use this for both keys
    if reg_key in record:
        # and issue a warning if they were both set and different
        # as we're overwriting some user data here
        if driver_key in record:
            logger.warning ("normalize_input: incoming record has both values, using %s"%reg_key)
        record[driver_key]=record[reg_key]
    # we only have one key set, duplicate for the other one
    elif driver_key in record:
        logger.warning ("normalize_input: you should use '%s' instead of '%s'"%(reg_key,driver_key))
        record[reg_key]=record[driver_key]

def normalize_input_record (record):
    _normalize_input (record, 'reg-researchers','researcher')
    _normalize_input (record, 'reg-pis','pi')
    _normalize_input (record, 'reg-keys','keys')
    # xxx the keys thing could use a little bit more attention:
    # some parts of the code are using 'keys' while they should use 'reg-keys' 
    # but I run out of time for now
    if 'reg-keys' in record: record['keys']=record['reg-keys']
    return record

class RegistryManager:

    def __init__ (self, config): 
        logger.info("Creating RegistryManager[%s]"%id(self))

    # The GENI GetVersion call
    def GetVersion(self, api, options):
        peers = dict ( [ (hrn,interface.get_url()) for (hrn,interface) in api.registries.iteritems() 
                       if hrn != api.hrn])
        xrn=Xrn(api.hrn,type='authority')
        return version_core({'interface':'registry',
                             'sfa': 3,
                             'hrn':xrn.get_hrn(),
                             'urn':xrn.get_urn(),
                             'peers':peers})
    
    def GetCredential(self, api, xrn, input_type, caller_xrn=None):
        # convert xrn to hrn     
        if input_type:
            hrn, _ = urn_to_hrn(xrn)
            type = input_type
        else:
            hrn, type = urn_to_hrn(xrn)

        # Slivers don't have credentials but users should be able to 
        # specify a sliver xrn and receive the slice's credential
        # However if input_type is specified
        if type == 'sliver' or ( not input_type and '-' in Xrn(hrn).leaf):
            slice_xrn = api.driver.sliver_to_slice_xrn(hrn)
            hrn = slice_xrn.hrn 
  
        # Is this a root or sub authority
        auth_hrn = api.auth.get_authority(hrn)
        if not auth_hrn or hrn == api.config.SFA_INTERFACE_HRN:
            auth_hrn = hrn
        auth_info = api.auth.get_auth_info(auth_hrn)

        # get record info
        dbsession = api.dbsession()
        record=dbsession.query(RegRecord).filter_by(type=type,hrn=hrn).first()
        if not record:
            raise RecordNotFound("hrn=%s, type=%s"%(hrn,type))

        # get the callers gid
        # if caller_xrn is not specified assume the caller is the record
        # object itself.
        if not caller_xrn:
            caller_hrn = hrn
            caller_gid = record.get_gid_object()
        else:
            caller_hrn, caller_type = urn_to_hrn(caller_xrn)
            if caller_type:
                caller_record = dbsession.query(RegRecord).filter_by(hrn=caller_hrn,type=caller_type).first()
            else:
                caller_record = dbsession.query(RegRecord).filter_by(hrn=caller_hrn).first()
            if not caller_record:
                raise RecordNotFound("Unable to associated caller (hrn=%s, type=%s) with credential for (hrn: %s, type: %s)"%(caller_hrn, caller_type, hrn, type))
            caller_gid = GID(string=caller_record.gid)
 
        object_hrn = record.get_gid_object().get_hrn()
        # call the builtin authorization/credential generation engine
        rights = api.auth.determine_user_rights(caller_hrn, record)
        # make sure caller has rights to this object
        if rights.is_empty():
            raise PermissionError("%s has no rights to %s (%s)" % \
                                  (caller_hrn, object_hrn, xrn))    
        object_gid = GID(string=record.gid)
        new_cred = Credential(subject = object_gid.get_subject())
        new_cred.set_gid_caller(caller_gid)
        new_cred.set_gid_object(object_gid)
        new_cred.set_issuer_keys(auth_info.get_privkey_filename(), auth_info.get_gid_filename())
        #new_cred.set_pubkey(object_gid.get_pubkey())
        new_cred.set_privileges(rights)
        new_cred.get_privileges().delegate_all_privileges(True)
        if hasattr(record,'expires'):
            date = utcparse(record.expires)
            expires = datetime_to_epoch(date)
            new_cred.set_expiration(int(expires))
        auth_kind = "authority,ma,sa"
        # Parent not necessary, verify with certs
        #new_cred.set_parent(api.auth.hierarchy.get_auth_cred(auth_hrn, kind=auth_kind))
        new_cred.encode()
        new_cred.sign()
    
        return new_cred.save_to_string(save_parents=True)
    
    
    # the default for full, which means 'dig into the testbed as well', should be false
    def Resolve(self, api, xrns, type=None, details=False):
    
        dbsession = api.dbsession()
        if not isinstance(xrns, types.ListType):
            # try to infer type if not set and we get a single input
            if not type:
                type = Xrn(xrns).get_type()
            xrns = [xrns]
        hrns = [urn_to_hrn(xrn)[0] for xrn in xrns] 

        # load all known registry names into a prefix tree and attempt to find
        # the longest matching prefix
        # create a dict where key is a registry hrn and its value is a list
        # of hrns at that registry (determined by the known prefix tree).  
        xrn_dict = {}
        registries = api.registries
        tree = prefixTree()
        registry_hrns = registries.keys()
        tree.load(registry_hrns)
        for xrn in xrns:
            registry_hrn = tree.best_match(urn_to_hrn(xrn)[0])
            if registry_hrn not in xrn_dict:
                xrn_dict[registry_hrn] = []
            xrn_dict[registry_hrn].append(xrn)
            
        records = [] 
        for registry_hrn in xrn_dict:
            # skip the hrn without a registry hrn
            # XX should we let the user know the authority is unknown?       
            if not registry_hrn:
                continue
    
            # if the best match (longest matching hrn) is not the local registry,
            # forward the request
            xrns = xrn_dict[registry_hrn]
            if registry_hrn != api.hrn:
                credential = api.getCredential()
                interface = api.registries[registry_hrn]
                server_proxy = api.server_proxy(interface, credential)
                # should propagate the details flag but that's not supported in the xmlrpc interface yet
                #peer_records = server_proxy.Resolve(xrns, credential,type, details=details)
                peer_records = server_proxy.Resolve(xrns, credential)
                # pass foreign records as-is
                # previous code used to read
                # records.extend([SfaRecord(dict=record).as_dict() for record in peer_records])
                # not sure why the records coming through xmlrpc had to be processed at all
                records.extend(peer_records)
    
        # try resolving the remaining unfound records at the local registry
        local_hrns = list ( set(hrns).difference([record['hrn'] for record in records]) )
        # 
        local_records = dbsession.query(RegRecord).filter(RegRecord.hrn.in_(local_hrns))
        if type:
            local_records = local_records.filter_by(type=type)
        local_records=local_records.all()
        
        for local_record in local_records:
            augment_with_sfa_builtins (local_record)

        logger.info("Resolve, (details=%s,type=%s) local_records=%s "%(details,type,local_records))
        local_dicts = [ record.__dict__ for record in local_records ]
        
        if details:
            # in details mode we get as much info as we can, which involves contacting the 
            # testbed for getting implementation details about the record
            api.driver.augment_records_with_testbed_info(local_dicts)
            # also we fill the 'url' field for known authorities
            # used to be in the driver code, sounds like a poorman thing though
            def solve_neighbour_url (record):
                if not record.type.startswith('authority'): return 
                hrn=record.hrn
                for neighbour_dict in [ api.aggregates, api.registries ]:
                    if hrn in neighbour_dict:
                        record.url=neighbour_dict[hrn].get_url()
                        return 
            for record in local_records: solve_neighbour_url (record)
        
        # convert local record objects to dicts for xmlrpc
        # xxx somehow here calling dict(record) issues a weird error
        # however record.todict() seems to work fine
        # records.extend( [ dict(record) for record in local_records ] )
        records.extend( [ record.todict(exclude_types=[InstrumentedList]) for record in local_records ] )

        if not records:
            raise RecordNotFound(str(hrns))
    
        return records
    
    def List (self, api, xrn, origin_hrn=None, options=None):
        if options is None: options={}
        dbsession=api.dbsession()
        # load all know registry names into a prefix tree and attempt to find
        # the longest matching prefix
        hrn, type = urn_to_hrn(xrn)
        registries = api.registries
        registry_hrns = registries.keys()
        tree = prefixTree()
        tree.load(registry_hrns)
        registry_hrn = tree.best_match(hrn)
       
        #if there was no match then this record belongs to an unknow registry
        if not registry_hrn:
            raise MissingAuthority(xrn)
        # if the best match (longest matching hrn) is not the local registry,
        # forward the request
        record_dicts = []    
        if registry_hrn != api.hrn:
            credential = api.getCredential()
            interface = api.registries[registry_hrn]
            server_proxy = api.server_proxy(interface, credential)
            record_list = server_proxy.List(xrn, credential, options)
            # same as above, no need to process what comes from through xmlrpc
            # pass foreign records as-is
            record_dicts = record_list
        
        # if we still have not found the record yet, try the local registry
#        logger.debug("before trying local records, %d foreign records"% len(record_dicts))
        if not record_dicts:
            recursive = False
            if ('recursive' in options and options['recursive']):
                recursive = True
            elif hrn.endswith('*'):
                hrn = hrn[:-1]
                recursive = True

            if not api.auth.hierarchy.auth_exists(hrn):
                raise MissingAuthority(hrn)
            if recursive:
                records = dbsession.query(RegRecord).filter(RegRecord.hrn.startswith(hrn)).all()
#                logger.debug("recursive mode, found %d local records"%(len(records)))
            else:
                records = dbsession.query(RegRecord).filter_by(authority=hrn).all()
#                logger.debug("non recursive mode, found %d local records"%(len(records)))
            # so that sfi list can show more than plain names...
            for record in records: augment_with_sfa_builtins (record)
            record_dicts=[ record.todict(exclude_types=[InstrumentedList]) for record in records ]
    
        return record_dicts
    
    def CreateGid(self, api, xrn, cert):
        # get the authority
        authority = Xrn(xrn=xrn).get_authority_hrn()
        auth_info = api.auth.get_auth_info(authority)
        if not cert:
            pkey = Keypair(create=True)
        else:
            certificate = Certificate(string=cert)
            pkey = certificate.get_pubkey()    

        # Add the email of the user to SubjectAltName in the GID
        email = None
        hrn = Xrn(xrn).get_hrn()
        dbsession=api.dbsession()
        record=dbsession.query(RegUser).filter_by(hrn=hrn).first()
        if record:
            email=getattr(record,'email',None)
        gid = api.auth.hierarchy.create_gid(xrn, create_uuid(), pkey, email = email)
        return gid.save_to_string(save_parents=True)
    
    ####################
    # utility for handling relationships among the SFA objects 
    
    # subject_record describes the subject of the relationships
    # ref_record contains the target values for the various relationships we need to manage
    # (to begin with, this is just the slice x person (researcher) and authority x person (pi) relationships)
    def update_driver_relations (self, api, subject_obj, ref_obj):
        type=subject_obj.type
        #for (k,v) in subject_obj.__dict__.items(): print k,'=',v
        if type=='slice' and hasattr(ref_obj,'researcher'):
            self.update_driver_relation(api, subject_obj, ref_obj.researcher, 'user', 'researcher')
        elif type=='authority' and hasattr(ref_obj,'pi'):
            self.update_driver_relation(api, subject_obj,ref_obj.pi, 'user', 'pi')
        
    # field_key is the name of one field in the record, typically 'researcher' for a 'slice' record
    # hrns is the list of hrns that should be linked to the subject from now on
    # target_type would be e.g. 'user' in the 'slice' x 'researcher' example
    def update_driver_relation (self, api, record_obj, hrns, target_type, relation_name):
        dbsession=api.dbsession()
        # locate the linked objects in our db
        subject_type=record_obj.type
        subject_id=record_obj.pointer
        # get the 'pointer' field of all matching records
        link_id_tuples = dbsession.query(RegRecord.pointer).filter_by(type=target_type).filter(RegRecord.hrn.in_(hrns)).all()
        # sqlalchemy returns named tuples for columns
        link_ids = [ tuple.pointer for tuple in link_id_tuples ]
        api.driver.update_relation (subject_type, target_type, relation_name, subject_id, link_ids)

    def Register(self, api, record_dict):
    
        logger.debug("Register: entering with record_dict=%s"%printable(record_dict))
        normalize_input_record (record_dict)
        logger.debug("Register: normalized record_dict=%s"%printable(record_dict))

        dbsession=api.dbsession()
        hrn, type = record_dict['hrn'], record_dict['type']
        urn = hrn_to_urn(hrn,type)
        # validate the type
        if type not in ['authority', 'slice', 'node', 'user']:
            raise UnknownSfaType(type) 
        
        # check if record_dict already exists
        existing_records = dbsession.query(RegRecord).filter_by(type=type,hrn=hrn).all()
        if existing_records:
            raise ExistingRecord(hrn)
           
        assert ('type' in record_dict)
        # returns the right type of RegRecord according to type in record
        record = make_record(dict=record_dict)
        record.just_created()
        record.authority = get_authority(record.hrn)
        auth_info = api.auth.get_auth_info(record.authority)
        pub_key = None
        # make sure record has a gid
        if not record.gid:
            uuid = create_uuid()
            pkey = Keypair(create=True)
            pub_key=getattr(record,'reg-keys',None)
            if pub_key is not None:
                # use only first key in record
                if pub_key and isinstance(pub_key, types.ListType): pub_key = pub_key[0]
                pkey = convert_public_key(pub_key)
    
            email=getattr(record,'email',None)
            gid_object = api.auth.hierarchy.create_gid(urn, uuid, pkey, email = email)
            gid = gid_object.save_to_string(save_parents=True)
            record.gid = gid
    
        if isinstance (record, RegAuthority):
            # update the tree
            if not api.auth.hierarchy.auth_exists(hrn):
                api.auth.hierarchy.create_auth(hrn_to_urn(hrn,'authority'))
    
            # get the GID from the newly created authority
            auth_info = api.auth.get_auth_info(hrn)
            gid = auth_info.get_gid_object()
            record.gid=gid.save_to_string(save_parents=True)

            # locate objects for relationships
            pi_hrns = getattr(record,'reg-pis',None)
            if pi_hrns is not None: record.update_pis (pi_hrns, dbsession)

        elif isinstance (record, RegSlice):
            researcher_hrns = getattr(record,'reg-researchers',None)
            if researcher_hrns is not None: record.update_researchers (researcher_hrns, dbsession)
        
        elif isinstance (record, RegUser):
            # create RegKey objects for incoming keys
            if hasattr(record,'reg-keys'):
                keys=getattr(record,'reg-keys')
                # some people send the key as a string instead of a list of strings
                if isinstance(keys,types.StringTypes): keys=[keys]
                logger.debug ("creating %d keys for user %s"%(len(keys),record.hrn))
                record.reg_keys = [ RegKey (key) for key in keys ]
            
        # update testbed-specific data if needed
        pointer = api.driver.register (record.__dict__, hrn, pub_key)

        record.pointer=pointer
        dbsession.add(record)
        dbsession.commit()
    
        # update membership for researchers, pis, owners, operators
        self.update_driver_relations (api, record, record)
        
        return record.get_gid_object().save_to_string(save_parents=True)
    
    def Update(self, api, record_dict):

        logger.debug("Update: entering with record_dict=%s"%printable(record_dict))
        normalize_input_record (record_dict)
        logger.debug("Update: normalized record_dict=%s"%printable(record_dict))

        dbsession=api.dbsession()
        assert ('type' in record_dict)
        new_record=make_record(dict=record_dict)
        (type,hrn) = (new_record.type, new_record.hrn)
        
        # make sure the record exists
        record = dbsession.query(RegRecord).filter_by(type=type,hrn=hrn).first()
        if not record:
            raise RecordNotFound("hrn=%s, type=%s"%(hrn,type))
        record.just_updated()
    
        # Use the pointer from the existing record, not the one that the user
        # gave us. This prevents the user from inserting a forged pointer
        pointer = record.pointer

        # is there a change in keys ?
        new_key=None
        if type=='user':
            if getattr(new_record,'keys',None):
                new_key=new_record.keys
                if isinstance (new_key,types.ListType):
                    new_key=new_key[0]

        # take new_key into account
        if new_key:
            # update the openssl key and gid
            pkey = convert_public_key(new_key)
            uuid = create_uuid()
            urn = hrn_to_urn(hrn,type)

            email=getattr(new_record,'email',None)
            if email is None:
                email=getattr(record,'email',None)
            gid_object = api.auth.hierarchy.create_gid(urn, uuid, pkey, email = email)
            gid = gid_object.save_to_string(save_parents=True)
        
        # xxx should do side effects from new_record to record
        # not too sure how to do that
        # not too big a deal with planetlab as the driver is authoritative, but...

        # update native relations
        if isinstance (record, RegSlice):
            researcher_hrns = getattr(new_record,'reg-researchers',None)
            if researcher_hrns is not None: record.update_researchers (researcher_hrns, dbsession)

        elif isinstance (record, RegAuthority):
            pi_hrns = getattr(new_record,'reg-pis',None)
            if pi_hrns is not None: record.update_pis (pi_hrns, dbsession)
        
        # update the PLC information that was specified with the record
        # xxx oddly enough, without this useless statement, 
        # record.__dict__ as received by the driver seems to be off
        # anyway the driver should receive an object 
        # (and then extract __dict__ itself if needed)
        print "DO NOT REMOVE ME before driver.update, record=%s"%record
        new_key_pointer = -1
        try:
           (pointer, new_key_pointer) = api.driver.update (record.__dict__, new_record.__dict__, hrn, new_key)
        except:
           pass
        if new_key and new_key_pointer:
            record.reg_keys=[ RegKey (new_key, new_key_pointer)]
            record.gid = gid

        dbsession.commit()
        # update membership for researchers, pis, owners, operators
        self.update_driver_relations (api, record, new_record)
        
        return 1 
    
    # expecting an Xrn instance
    def Remove(self, api, xrn, origin_hrn=None):
        dbsession=api.dbsession()
        hrn=xrn.get_hrn()
        type=xrn.get_type()
        request=dbsession.query(RegRecord).filter_by(hrn=hrn)
        if type and type not in ['all', '*']:
            request=request.filter_by(type=type)
    
        record = request.first()
        if not record:
            msg="Could not find hrn %s"%hrn
            if type: msg += " type=%s"%type
            raise RecordNotFound(msg)

        type = record.type
        if type not in ['slice', 'user', 'node', 'authority'] :
            raise UnknownSfaType(type)

        credential = api.getCredential()
        registries = api.registries
    
        # Try to remove the object from the PLCDB of federated agg.
        # This is attempted before removing the object from the local agg's PLCDB and sfa table
        if hrn.startswith(api.hrn) and type in ['user', 'slice', 'authority']:
            for registry in registries:
                if registry not in [api.hrn]:
                    try:
                        result=registries[registry].remove_peer_object(credential, record, origin_hrn)
                    except:
                        pass

        # call testbed callback first
        # IIUC this is done on the local testbed TOO because of the refreshpeer link
        if not api.driver.remove(record.__dict__):
            logger.warning("driver.remove failed")

        # delete from sfa db
        dbsession.delete(record)
        dbsession.commit()
    
        return 1

    # This is a PLC-specific thing, won't work with other platforms
    def get_key_from_incoming_ip (self, api):
        dbsession=api.dbsession()
        # verify that the callers's ip address exist in the db and is an interface
        # for a node in the db
        (ip, port) = api.remote_addr
        interfaces = api.driver.shell.GetInterfaces({'ip': ip}, ['node_id'])
        if not interfaces:
            raise NonExistingRecord("no such ip %(ip)s" % locals())
        nodes = api.driver.shell.GetNodes([interfaces[0]['node_id']], ['node_id', 'hostname'])
        if not nodes:
            raise NonExistingRecord("no such node using ip %(ip)s" % locals())
        node = nodes[0]
       
        # look up the sfa record
        record=dbsession.query(RegRecord).filter_by(type='node',pointer=node['node_id']).first()
        if not record:
            raise RecordNotFound("node with pointer %s"%node['node_id'])
        
        # generate a new keypair and gid
        uuid = create_uuid()
        pkey = Keypair(create=True)
        urn = hrn_to_urn(record.hrn, record.type)

        email=getattr(record,'email',None)
        gid_object = api.auth.hierarchy.create_gid(urn, uuid, pkey, email)
        gid = gid_object.save_to_string(save_parents=True)
        record.gid = gid

        # update the record
        dbsession.commit()
  
        # attempt the scp the key
        # and gid onto the node
        # this will only work for planetlab based components
        (kfd, key_filename) = tempfile.mkstemp() 
        (gfd, gid_filename) = tempfile.mkstemp() 
        pkey.save_to_file(key_filename)
        gid_object.save_to_file(gid_filename, save_parents=True)
        host = node['hostname']
        key_dest="/etc/sfa/node.key"
        gid_dest="/etc/sfa/node.gid" 
        scp = "/usr/bin/scp" 
        #identity = "/etc/planetlab/root_ssh_key.rsa"
        identity = "/etc/sfa/root_ssh_key"
        scp_options=" -i %(identity)s " % locals()
        scp_options+="-o StrictHostKeyChecking=no " % locals()
        scp_key_command="%(scp)s %(scp_options)s %(key_filename)s root@%(host)s:%(key_dest)s" %\
                         locals()
        scp_gid_command="%(scp)s %(scp_options)s %(gid_filename)s root@%(host)s:%(gid_dest)s" %\
                         locals()    

        all_commands = [scp_key_command, scp_gid_command]
        
        for command in all_commands:
            (status, output) = commands.getstatusoutput(command)
            if status:
                raise Exception, output

        for filename in [key_filename, gid_filename]:
            os.unlink(filename)

        return 1 
