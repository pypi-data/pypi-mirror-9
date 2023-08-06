import os
import sys
import time
import radical.pilot as rp
import radical.utils as ru

dh      = ru.DebugHelper ()

CNT     =     0
RUNTIME =    60
SLEEP   =   900
CORES   =  1024 
UNITS   =  1024
SCHED   = rp.SCHED_DIRECT_SUBMISSION

# RESOURCE = 'local.localhost'
# PROJECT  = None

RESOURCE = 'xsede.trestles'
PROJECT  = 'TG-MCB090174' 

# RESOURCE = 'futuregrid.india'
# PROJECT  = None

#------------------------------------------------------------------------------
#
def pilot_state_cb (pilot, state) :
    """ this callback is invoked on all pilot state changes """

    if not pilot:
        return

    print "[Callback]: ComputePilot '%s' state: %s." % (pilot.uid, state)

    if  state == rp.FAILED :
        sys.exit (1)


#------------------------------------------------------------------------------
#
def unit_state_cb (unit, state) :
    """ this callback is invoked on all unit state changes """

    if not unit:
        return

    global CNT

    print "[Callback]: unit %s on %s : %s." % (unit.uid, unit.pilot_id, state)

    if state in [rp.FAILED, rp.DONE, rp.CANCELED] :
        CNT += 1
        print "[Callback]: # %6d" % CNT


    if  state == rp.FAILED :
        print "stderr: %s" % unit.stderr


#------------------------------------------------------------------------------
#
def wait_queue_size_cb(umgr, wait_queue_size):
    """ 
    this callback is called when the size of the unit managers wait_queue
    changes.
    """
    print "[Callback]: UnitManager  '%s' wait_queue_size changed to %s." \
        % (umgr.uid, wait_queue_size)

    pilots = umgr.get_pilots ()
    for pilot in pilots :
        print "pilot %s: %s" % (pilot.uid, pilot.state)

    if  wait_queue_size == 0 :
        for pilot in pilots :
            if  pilot.state in [rp.PENDING_LAUNCH,
                                rp.LAUNCHING     ,
                                rp.PENDING_ACTIVE] :
                print "cancel pilot %s" % pilot.uid
                umgr.remove_pilot (pilot.uid)
                pilot.cancel ()


#------------------------------------------------------------------------------
#
if __name__ == "__main__":

    session      = None
    session_name = None

    if len(sys.argv) > 1 :
        session_name = sys.argv[1]

    try :

        # prepare some input files for the compute units
        os.system ('hostname > file1.dat')
        os.system ('date     > file2.dat')

        # Create a new session. A session is the 'root' object for all other
        # RADICAL-Pilot objects. It encapsulates the MongoDB connection(s) as
        # well as security credentials.
        session = rp.Session()
        sid     = session.uid
        print "session id: %s (%s)" % (sid, session_name)

        # Add a Pilot Manager. Pilot managers manage one or more ComputePilots.
        pmgr = rp.PilotManager(session=session)

        # Register our callback with the PilotManager. This callback will get
        # called every time any of the pilots managed by the PilotManager
        # change their state.
        pmgr.register_callback(pilot_state_cb)

        # Define a 4-core local pilot that runs for 10 minutes and cleans up
        # after itself.
        pdesc = rp.ComputePilotDescription()
        pdesc.resource = RESOURCE
        pdesc.cores    = CORES
        pdesc.project  = PROJECT
        pdesc.runtime  = RUNTIME  # minutes
        pdesc.cleanup  = False

      # pdesc.resource = "xsede.stampede"
      # pdesc.project  = 'TG-MCB090174'
      # pdesc.cores    = CORES
      # pdesc.cores    = 128

        # Launch the pilot.
        pilot = pmgr.submit_pilots(pdesc)

        # Combine the ComputePilot, the ComputeUnits and a scheduler via
        # a UnitManager object.
        umgr = rp.UnitManager(
            session=session,
            scheduler=SCHED)

        # Register our callback with the UnitManager. This callback will get
        # called every time any of the units managed by the UnitManager
        # change their state.
        umgr.register_callback(unit_state_cb, rp.UNIT_STATE)

        # Register also a callback which tells us when all units have been
        # assigned to pilots
        umgr.register_callback(wait_queue_size_cb, rp.WAIT_QUEUE_SIZE)


        # Add the previously created ComputePilot to the UnitManager.
        umgr.add_pilots(pilot)

        # Create a workload of ComputeUnits (tasks). Each compute unit
        # uses /bin/cat to concatenate two input files, file1.dat and
        # file2.dat. The output is written to STDOUT. cu.environment is
        # used to demonstrate how to set environment variables within a
        # ComputeUnit - it's not strictly necessary for this example. As
        # a shell script, the ComputeUnits would look something like this:
        #
        #    export INPUT1=file1.dat
        #    export INPUT2=file2.dat
        #    /bin/cat $INPUT1 $INPUT2
        #
        cuds = []
        for unit_count in range(0, UNITS):
            cud = rp.ComputeUnitDescription()
            cud.executable    = "/bin/sh"
            cud.arguments     = ['-c', "'echo \"hello world\"; /bin/sleep %s" % SLEEP]
          # cud.arguments     = []
            cud.cores         = 1

            cuds.append(cud)

        # Submit the previously created ComputeUnit descriptions to the
        # PilotManager. This will trigger the selected scheduler to start
        # assigning ComputeUnits to the ComputePilots.
        units = umgr.submit_units(cuds)

        # Wait for all compute units to reach a terminal state (DONE or FAILED).
        umgr.wait_units()

        print 'units all done'
        print '----------------------------------------------------------------------'

        for unit in units :
            unit.wait ()

        for unit in units:
            print "* Task %s (executed @ %s) state %s, exit code: %s, started: %s, finished: %s, stdout: %s" \
                % (unit.uid, unit.execution_locations, unit.state, unit.exit_code, unit.start_time, unit.stop_time, unit.stdout)

        # delete the test data files
        os.system ('rm file1.dat')
        os.system ('rm file2.dat')

        session.close (cleanup=False, delete=False, terminate=True)
        session = None

        os.system ("radicalpilot-stats -m stat,plot -s %s > %s.stat" % (sid, session_name))

    except Exception as e :
        print "exception: %s" % e

    finally :
        if  session :
            session.close (cleanup=False, delete=False, terminate=True)


