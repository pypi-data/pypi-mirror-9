
import radical.pilot as rp
import pprint

RESOURCE = 'epsrc.archer'

# get a pre-installed resource configuration
session = rp.Session()
cfg = session.get_resource_config(RESOURCE)
pprint.pprint (cfg)

# create a new config based on the old one, and set a different launch method
new_cfg = rp.ResourceConfig(RESOURCE, cfg)
new_cfg.task_launch_method = 'ORTE'

# now add the entry back.  As we did not change the config name, this will
# replace the original configuration.  A completely new configuration would
# need a unique label.
session.add_resource_config(new_cfg)
pprint.pprint (session.get_resource_config(RESOURCE))
