from sfa.util.xrn import urn_to_hrn
from sfa.util.method import Method
from sfa.storage.parameter import Parameter, Mixed
from sfa.trust.auth import Auth
from sfa.trust.credential import Credential

class Delete(Method):
    """
    Remove the slice or slivers and free the allocated resources        

    @param xrns human readable name of slice to instantiate (hrn or urn)
    @param creds credential string specifying the rights of the caller
    @return 1 is successful, faults otherwise  
    """

    interfaces = ['aggregate', 'slicemgr', 'component']
    
    accepts = [
        Parameter(type([str]), "Human readable name of slice to delete (hrn or urn)"),
        Parameter(type([dict]), "Credentials"),
        Parameter(dict, "options"),
        ]

    returns = Parameter(int, "1 if successful")
    
    def call(self, xrns, creds, options):
        valid_creds = self.api.auth.checkCredentialsSpeaksFor(creds, 'deletesliver', xrns,
                                                              check_sliver_callback = self.api.driver.check_sliver_credentials,
                                                              options=options)

        #log the call
        origin_hrn = Credential(cred=valid_creds[0]).get_gid_caller().get_hrn()
        self.api.logger.info("interface: %s\tcaller-hrn: %s\ttarget-hrn: %s\tmethod-name: %s"%(self.api.interface, origin_hrn, xrns, self.name))

        return self.api.manager.Delete(self.api, xrns, creds, options)
