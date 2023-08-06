Getting Started
===============

Getting a connection to your Violin Memory appliance is as simple as this::

    import vmemclient
    con = vmemclient.open(hostname, username, password)

The **open()** function automatically determines what kind of Violin
Memory appliance it sees, and returns a version specific object that you
can use to query and manage your array.  It makes this connection over
*https* preferably, but it can also fallback to *http* for the session
authentication if *https* isn't working.

When finished interacting with the Violin Memory array, close the
connection like so::

    con.close()

There are a few different object types that the *open()* function can
return.  Please refer to the *open()* documentation for more info on the
specifics of using each object type, and the various functions available
for your product / version.


Examples
========

Below are a few examples of how to use the core VXG python library:


Example 1:  Get the system uptime
----------------------------------

This example works on all MGs running 6.x and lower, and all ACMs.::

    # Get the connection object
    con = vmemclient.open(hostname, username, password)
    if con is not None:
        node = '/system/uptime'
        answer = con.basic.get_node_values(node)
        uptime = datetime.timedelta(int(milliseconds=answer[node]))
        print '{0} uptime: {1}'.format(hostname, uptime)
        con.close()


Example 2:  List all LUNs
-------------------------

This example works on all MGs running 6.x and lower.::

    con = vmemclient.open(hostname, username, password)
    if con is not None:
        base_node = '/vshare/state/local/container/*'
        containers = con.basic.get_node_values(base_node)
        for container in containers.values():
            print '[LUNs in container: {0}]'.format(container)
            luns_node = base_node[:-1] + container + '/lun/*'
            luns = con.basic.get_node_values(luns_node)
            for lun in luns.values():
                print ' - {0}'.format(lun)
            print
        con.close()


Example 3:  Create a LUN
------------------------

Each object returned from *vmemclient.open()* has a number of namespaces,
and each namespace will have a collection of functions.  This example
will demonstrate how to do LUN creation on a MG running 6.x.  Pairing
these functions with the version specific REST API documentation will
tell what types of input are expected, and any acceptible values.::

    # Create the object connection like normal
    con = vmemclient.open(hostname, username, password)
    if con is not None:
        answer = con.basic.get_node_values('/vshare/state/local/container/*')
        if not answer:
            print 'No container present'
        else:
            # Use the first container on this MG
            container = answer.values()[0]

            # Create a single, read-only, thick LUN of size 10G
            result = con.lun.create_lun(container, 'MyNewLun', size='10',
                                        quantity=1, nozero='nozero',
                                        thin='0', readonly='r',
                                        startnum=1)

            # Actions return a dict with two keys: 'code' and 'message'
            if result['code'] == 0:
                print 'Created LUN OK: {0}'.format(result['message'])
            else:
                print 'Failed ({code}): {message}'.format(**result)

        # Done
        con.close()
