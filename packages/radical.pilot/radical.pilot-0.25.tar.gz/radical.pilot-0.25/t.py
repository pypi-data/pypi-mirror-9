
import radical.pilot as rp
import radical.utils as ru
import sys

dh=ru.DebugHelper()

s=rp.Session()
pd=rp.ComputePilotDescription()
pd.resource='local.localhost'
pd.cores=1
pd.runtime=1
pd.cleanup=True
pd.queue='does_not_exist'
pm=rp.PilotManager(s)
p=pm.submit_pilots(pd)
print p.wait()
print p.state
print p.stdout
print p.stderr

s.close(cleanup=True, terminate=True)

sys.exit ()

