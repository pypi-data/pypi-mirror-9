Sfor
====

Simple failover resolver for Python

this is experimental version.
yet, you should not use in large-scale service.



Install
===

    pip install sfor

Example
===


    from sfor.sfor_simple import SforSimple, SforNodeInfo
    import time
    import logging
    
    node_list = [
        SforNodeInfo("hoge1", 80, "/status.html"),
        SforNodeInfo("hoge2", 80, "/status.html"),
    ]
    
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    
    sfor = SforSimple(node_list)
    
    for n in range(60):
         logging.info(sfor.resolv())
         time.sleep(1)

