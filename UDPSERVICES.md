## Storm.pm services

Available on storm.pm:410 (IPv4 and IPv6) UDP

First byte is the operation:

0x01: Update tunnel endpoint with automatic IP
    This is only available over IPv4.
    
    data[1:17] is the block UUID in big endian.

    Reply: [0]   is 0x01
           [1]   is 0 for success, >0 for fail
           
    
0x02: Update tunnel endpoint with manual IP
    This is available over IPv4 and IPv6
    
    data[1:17] is the block UUID in big endian.
    data[17:21] is the IPv4 endpoint address in network byte order.
    
    Reply: [0]   is 0x02
           [1]   is 0 for success, >0 for fail
           
0x03: Add/Update DNS AAAA record
    This is available over IPv4 and IPv6
    
    data[1:17]  is the block UUID. The IP suffix is in this block.
    data[17:25] is the IPv6 suffix (the last 64 bits after the block)
    data[25]    is the length of the DNS prefix (the part before .m.storm.pm)
    data[26:]  is the prefix (eg "border.mymesh") It does not end in '.'
    
    Reply: [0] is 0x03
           [1] is 0 for success, >0 for fail
          
0x04: Add/Update DNS AAAA record with auto address
    This is only available over IPv6. It is used for a node to name itself.
    It gets the IPv6 address from the packet.
    
    data[1:17] is the block UUID.
    data[17]    is the length of the DNS prefix (the part before .m.storm.pm)
    data[18:]  is the prefix (eg "border.mymesh") It does not end in '.'
    
    Reply[: [0] is 0x04
            [1] is 0 for success, >0 for fail
                


