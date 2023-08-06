from sfa.util.sfalogging import logger

class SecurityGroup:

    def __init__(self, driver):
        self.client = driver.shell.nova_manager

        
    def create_security_group(self, name):
        try:
            self.client.security_groups.create(name=name, description=name)
        except Exception, ex:
            logger.log_exc("Failed to add security group")
            raise

    def delete_security_group(self, name):
        try:
            security_group = self.client.security_groups.find(name=name)
            self.client.security_groups.delete(security_group.id)
        except Exception, ex:
            logger.log_exc("Failed to delete security group")


    def _validate_port_range(self, port_range):
        from_port = to_port = None
        if isinstance(port_range, str):
            ports = port_range.split(':')
            if len(ports) > 1:
                from_port = int(ports[0])
                to_port = int(ports[1])
            else:
                from_port = to_port = int(ports[0])
        return (from_port, to_port)

    def _validate_icmp_type_code(self, icmp_type_code):
        from_port = to_port = None
        if isinstance(icmp_type_code, str):
            code_parts = icmp_type_code.split(':')
            if len(code_parts) > 1:
                try:
                    from_port = int(code_parts[0])
                    to_port = int(code_parts[1])
                except ValueError:
                    logger.error('port must be an integer.')
        return (from_port, to_port)


    def add_rule_to_group(self, group_name=None, protocol='tcp', cidr_ip='0.0.0.0/0',
                          port_range=None, icmp_type_code=None,
                          source_group_name=None, source_group_owner_id=None):

        try:
            from_port, to_port = self._validate_port_range(port_range)
            icmp_type = self._validate_icmp_type_code(icmp_type_code)
            if icmp_type and icmp_type[0] and icmp_type[1]:
                from_port, to_port = icmp_type[0], icmp_type[1]

            group = self.client.security_groups.find(name=group_name)
            self.client.security_group_rules.create(group.id, \
                                protocol, from_port, to_port,cidr_ip)
        except Exception, ex:
            logger.log_exc("Failed to add rule to group %s" % group_name)


    def remove_rule_from_group(self, group_name=None, protocol='tcp', cidr_ip='0.0.0.0/0',
                          port_range=None, icmp_type_code=None,
                          source_group_name=None, source_group_owner_id=None):
        try:
            from_port, to_port = self._validate_port_range(port_range)
            icmp_type = self._validate_icmp_type_code(icmp_type_code)
            if icmp_type:
                from_port, to_port = icmp_type[0], icmp_type[1]
            group = self.client.security_groups.find(name=group_name)
            filter = {
                'id': group.id,   
                'from_port': from_port,
                'to_port': to_port,
                'cidr_ip': ip,
                'ip_protocol':protocol,
            }
            rule = self.client.security_group_rules.find(**filter)
            if rule:
                self.client.security_group_rules.delete(rule)
        except Exception, ex:
            logger.log_exc("Failed to remove rule from group %s" % group_name) 
             
