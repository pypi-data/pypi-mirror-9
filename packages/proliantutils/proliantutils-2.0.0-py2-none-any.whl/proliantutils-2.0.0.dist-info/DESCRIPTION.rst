devices in HP Proliant Servers.
Home-page: https://github.com/hpproliant/proliantutils
Author: Hewlett Packard
Author-email: proliantutils@gmail.com
License: Apache License, Version 2.0
Description: ==============
        Proliant Utils
        ==============
        
        Proliant Management Tools provides python libraries for interfacing and 
        managing various devices(like iLO) present in HP Proliant Servers.
        
        Currently, this module offers a library to interface to iLO4 using RIBCL.
        
        #!/usr/bin/python
        
            from proliantutils.ilo import ribcl
        
            ilo_client = ribcl.IloClient('1.2.3.4', 'Administrator', 'password')
            print ilo_client.get_host_power_status()
        
        
Platform: UNKNOWN
Classifier: Development Status :: 4 - Beta
Classifier: Environment :: Console
Classifier: Environment :: Web Environment
Classifier: Intended Audience :: Developers
Classifier: Intended Audience :: Information Technology
Classifier: License :: OSI Approved :: Apache Software License
Classifier: Operating System :: OS Independent
Classifier: Programming Language :: Python
