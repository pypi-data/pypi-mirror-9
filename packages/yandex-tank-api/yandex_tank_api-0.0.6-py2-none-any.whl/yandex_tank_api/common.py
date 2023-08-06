"""
Commands from HTTP Server (from manager_queue):
    Run the test to the next break:
        {
        'session': '1a2b4f3c'
        'cmd':'run',
        'break': --- see break requests for tank
        'test': --- only when creating new session
        'config': --- only when creating new  session
        }
    Stop the test
        {
        'session': '1a2b4f3c'
        'cmd':'stop'
        }


Status reported by tank (from manager_queue):
    {
     'session': '1a2b4f3c'
     'test': 'DEATHSTAR-10-12345'
     'status': 'running'|'success'|'failure'
     'current_stage': --- current stage (from test_stage_order)
     'break': --- stage to make a break before
     'failures': --- [ {'stage': stage-at-which-failed,'reason': reason of failure },
                       {'stage':stage-of-next-failure,'reason':...},
                       ... ]
     }
=====

Break requests (into tank_queue):
    {'break': --- any stage from test_stage_order }

====
Status reported to HTTP Server (into webserver_queue):
    {
    'session': '1a2b4f3c'
    'test': 'DEATHSTAR-10-12345'
    'status': 'running'|'success'|'failed' (from tank or from  manager)
               running: the tank is running
               success: tank has exited and no failures occured
               failed: tank has exited and there were failures

    'stage': --- optional, from tank only. This is the last stage that was executed.
    'break': --- optional, from tank only. The next break.
    'reason' : --- optional (from manager)
    'failures': --- optional, from tank only
    }
"""

test_stage_order = ['lock', 'init', 'configure', 'prepare',
                    'start', 'poll', 'end', 'postprocess', 'unlock', 'finished']


def is_A_earlier_than_B(stage_A, stage_B):
    """Slow but reliable"""
    return test_stage_order.index(stage_A) < test_stage_order.index(stage_B)


def get_valid_breaks():
    return test_stage_order


def is_valid_break(brk):
    return brk in test_stage_order
