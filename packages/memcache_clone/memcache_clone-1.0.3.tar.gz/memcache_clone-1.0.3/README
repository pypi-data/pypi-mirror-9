clone memcache data to other memcache
Usage Example:
    from memcache_clone import memcache
    s = memcache('127.0.0.1',11211)
    s.con()
    #set(key,value,len,flags,express)
    s.set("key","value",5,0,0)
    #get(key) return list : list[value,value_len,flags]
    s.get("key")[0]
    #clone
    s.clone('127.0.0.1',11212)
