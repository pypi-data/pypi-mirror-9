from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

try:
    from future_builtings import map, zip
except ImportError:
    pass

import errno
import logging
import random
import time

from ...dotdict import dotdict, apidict
from .. import enip, network

log				= logging.getLogger( "cli.test" )

def test_client_api():
    """Performance of executing an operation a number of times on a socket connected
    Logix simulator, within the same Python interpreter (ie. all on a single CPU
    thread).

    """
    # TODO: work in progress; not operational yet (only one clitest Thread)

    svraddr		        = ('localhost', 12399)
    svrkwds			= dotdict({
        'argv': [
            #'-v',
            '--address',	'%s:%d' % svraddr,
            'Tag=INT[1000]'
        ],
        'server': {
            'control':	apidict( enip.timeout, { 
                'done': False
            }),
        },
    })

    def tagtests( total, name="Tag", length=1000, size=2 ):
        """Generate random reads and writes to Tag.  All writes write a value equal to the index, all
        reads should report the correct value (or 0, if the element was never written).  Randomly
        supply an offset (force Read/Write Tag Fragmented).

        Yields the effective (elm,cnt), and the tag.

        """
        for i in range( total ):
            elm			= random.randint( 0, length-1 ) 
            cnt			= random.randint( 1, min( 5, length - elm ))
            off			= None # in elements, not bytes
            val			= None
            if not random.randint( 0, 10 ) and cnt > 1:
                off			= random.randint( 0, cnt - 1 )
            if random.randint( 0, 1 ):
                val		= list( range( elm + ( off or 0 ), elm + cnt ))
            tag			= "%s[%d-%d]" % ( name, elm, elm + cnt - 1 )
            if off is not None:
                tag	       += "+%d" % ( off * size )
            if val is not None:
                tag	       += '=' + ','.join( map( str, val ))

            yield (elm+( off or 0 ),cnt-( off or 0 )),tag

    def clitest( n ):
        times			= 100  # How many I/O per client
        # take apart the sequence of ( ..., ((elm,cnt), "Tag[1-2]=1,2"), ...)
        # into two sequences: (..., (elm,cnt), ...) and (..., "Tag[1-2]=1,2", ...)
        name			= 'Tag'
        regs,tags		= zip( *list( tagtests( total=times, name=name )))
        connection		= None
        while not connection:
            try:
                connection	= enip.client.connector( *svraddr, timeout=5 )
            except OSError as exc:
                if exc.errno != errno.ECONNREFUSED:
                    raise
                time.sleep( .1 )
         
        results			= []
        failures		= 0
        with connection:
            for idx,dsc,req,rpy,sts,val in connection.pipeline( 
                    operations=enip.client.parse_operations( tags ),
                    multiple=500, timeout=5, depth=3 ):
                log.detail( "Client %3d: %s --> %r ", n, dsc, val )
                if not val:
                    log.warning( "Client %d harvested %d/%d results; failed request: %s",
                                 n, len( results ), len( tags ), rpy )
                    failures       += 1
                results.append( (dsc,val) )
        if len( results ) !=  len( tags ):
            log.warning( "Client %d harvested %d/%d results", n, len( results ), len( tags ))
            failures	       += 1
        # Now, ensure that any results that reported values reported the correct values -- each
        # value equals its own index or 0.
        for i,(elm,cnt),tag,(dsc,val) in zip( range( times ), regs, tags, results ):
            log.detail( "Running on test %3d: operation %34s (%34s) on %5s[%3d-%-3d] ==> %s",
                i, tag, dsc, name, elm, elm + cnt - 1, val )
            if not val:
                log.warning( "Failure in test %3d: operation %34s (%34s) on %5s[%3d-%-3d]: %s",
                             i, tag, dsc, name, elm, elm + cnt - 1, val )
                failures       += 1
            if isinstance( val, list ):
                if not all( v in (e,0) for v,e in zip( val, range( elm, elm + cnt ))):
                    log.warning( "Failure in test %3d: operation %34s (%34s) on %5s[%3d-%-3d] didn't equal indexes: %s",
                                 i, tag, dsc, name, elm, elm + cnt - 1, val )
                    failures       += 1

        return 1 if failures else 0

    failed			= network.bench( server_func=enip.main,
                                                 server_kwds=svrkwds,
                                                 client_func=clitest,
                                                 client_count=1,
                                                 client_max=10 )
    assert failed == 0
