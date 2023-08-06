#!/usr/bin/env python
#coding=utf-8
from DBUtils.PooledDB import PooledDB
from beaker.cache import CacheManager
import functools
import settings
import datetime
try:
    import MySQLdb
except:
    pass

__cache_timeout__ = 600

cache = CacheManager(cache_regions={
      'short_term':{ 'type': 'memory', 'expire': __cache_timeout__ }
      }) 

###############################################################################
# Basic Define                                                            ####
###############################################################################

ticket_fds = [
    'account_number','acct_fee','acct_input_gigawords','acct_input_octets',
    'acct_input_packets','acct_output_gigawords','acct_output_octets',
    'acct_output_packets','acct_session_id','acct_session_time',
    'acct_start_time','acct_stop_time','acct_terminate_cause',
    'calling_station_id','fee_receivables','frame_netmask',
    'framed_ipaddr','is_deduct','nas_class','nas_addr',
    'nas_port','nas_port_id','nas_port_type','service_type',
    'session_timeout','start_source','stop_source',"mac_addr"
]

class Connect:
    def __init__(self, dbpool):
        self.conn = dbpool.connect()

    def __enter__(self):
        return self.conn   

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.conn.close()

class Cursor:
    def __init__(self, dbpool):
        self.conn = dbpool.connect()
        self.cursor = dbpool.cursor(self.conn)

    def __enter__(self):
        return self.cursor 

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.conn.close()

class MySQLPool():
    
    def __init__(self,config):
        conf_str = functools.partial(config.get,"database")
        conf_int = functools.partial(config.getint,"database")
        self.dbpool = PooledDB(
            creator=MySQLdb,
            db=conf_str("db"),
            host=conf_str("host"),
            port=conf_int("port"),
            user=conf_str("user"),
            passwd=conf_str("passwd"),
            charset=conf_str("charset"),
            maxusage=conf_int("maxusage")
        )

    def cursor(self,conn):
        return conn.cursor(MySQLdb.cursors.DictCursor)

    def connect(self):
        return self.dbpool.connection()
        

pool_clss = {'mysql':MySQLPool}

###############################################################################
# Database Store                                                          ####
###############################################################################        

class Store():

    def setup(self,config):
        self.dbpool = pool_clss[config.get("database",'dbtype')](config)
        global __cache_timeout__
        __cache_timeout__ = config.get("radiusd",'cache_timeout')

    @cache.cache('get_param',expire=__cache_timeout__)   
    def get_param(self,param_name):
        with Cursor(self.dbpool) as cur:
            cur.execute("select param_value from  slc_param where param_name = %s",(param_name,))
            param = cur.fetchone()
            return param and param['param_value'] or None

    def update_param_cache(self):
        with Cursor(self.dbpool) as cur:
            cur.execute("select param_name from  slc_param ")
            for param in cur:
                cache.invalidate(self.get_param,'get_param', str(param['param_name']))
                cache.invalidate(self.get_param,'get_param', unicode(param['param_name']))

    ###############################################################################
    # bas method                                                              ####
    ############################################################################### 

    def list_bas(self):
        with Cursor(self.dbpool) as cur:
            cur.execute("select * from  slc_rad_bas")
            return [bas for bas in cur] 

    @cache.cache('get_bas',expire=__cache_timeout__)   
    def get_bas(self,ipaddr):
        with Cursor(self.dbpool) as cur:
            cur.execute("select * from slc_rad_bas where ip_addr = %s",(ipaddr,))
            bas = cur.fetchone()
            return bas

    def update_bas_cache(self,ipaddr):
        cache.invalidate(self.get_bas,'get_bas',str(ipaddr))
        cache.invalidate(self.get_bas,'get_bas',unicode(ipaddr))

    ###############################################################################
    # user method                                                              ####
    ###############################################################################  

    @cache.cache('get_user',expire=__cache_timeout__)   
    def get_user(self,username):
        with Cursor(self.dbpool) as cur:
            cur.execute("select a.*,p.product_policy from slc_rad_account a,slc_rad_product p "
                "where a.product_id = p.id and a.account_number = %s ",(username,))
            user =  cur.fetchone()
            return user

    @cache.cache('get_user_attrs',expire=__cache_timeout__)   
    def get_user_attrs(self,username):
        with Cursor(self.dbpool) as cur:
            cur.execute("select * from slc_rad_account_attr where account_number = %s ",(username,))
            return cur.fetchall()  

    def get_user_balance(self,username):
        with Cursor(self.dbpool) as cur:
            cur.execute("select balance from slc_rad_account where account_number = %s ",(username,))
            b = cur.fetchone()  
            return b and b['balance'] or 0    
    
    def get_user_time_length(self,username):
        with Cursor(self.dbpool) as cur:
            cur.execute("select time_length from slc_rad_account where account_number = %s ",(username,))
            b = cur.fetchone()  
            return b and b['time_length'] or 0
    
    def get_user_flow_length(self,username):
        with Cursor(self.dbpool) as cur:
            cur.execute("select flow_length from slc_rad_account where account_number = %s ",(username,))
            b = cur.fetchone()  
            return b and b['flow_length'] or 0

    def update_user_cache(self,username):
        cache.invalidate(self.get_user,'get_user', str(username))
        cache.invalidate(self.get_user,'get_user', unicode(username))
        cache.invalidate(self.get_user_attrs,'get_user_attrs', str(username))
        cache.invalidate(self.get_user_attrs,'get_user_attrs', unicode(username))

    def update_user_balance(self,username,balance):
        with Connect(self.dbpool) as conn:
            cur = conn.cursor()
            sql = "update slc_rad_account set balance = %s where account_number = %s"
            cur.execute(sql,(balance,username))
            conn.commit()
            self.update_user_cache(username)
            
    def update_user_time_length(self,username,time_length):
        with Connect(self.dbpool) as conn:
            cur = conn.cursor()
            sql = "update slc_rad_account set time_length = %s where account_number = %s"
            cur.execute(sql,(time_length,username))
            conn.commit()
            self.update_user_cache(username)
    
    def update_user_flow_length(self,username,flow_length):
        with Connect(self.dbpool) as conn:
            cur = conn.cursor()
            sql = "update slc_rad_account set flow_length = %s where account_number = %s"
            cur.execute(sql,(flow_length,username))
            conn.commit()
            self.update_user_cache(username)

    def update_user_mac(self,username,mac_addr):
        with Connect(self.dbpool) as conn:
            cur = conn.cursor()
            sql = "update slc_rad_account set mac_addr = %s where account_number = %s"
            cur.execute(sql,(mac_addr,username))
            conn.commit()
            self.update_user_cache(username)

    def update_user_vlan_id(self,username,vlan_id):
        with Connect(self.dbpool) as conn:
            cur = conn.cursor()
            sql = "update slc_rad_account set vlan_id = %s where account_number = %s"
            cur.execute(sql,(vlan_id,username))
            conn.commit()
            self.update_user_cache(username)

    def update_user_vlan_id2(self,username,vlan_id2):
        with Connect(self.dbpool) as conn:
            cur = conn.cursor()
            sql = "update slc_rad_account set vlan_id2 = %s where account_number = %s"
            cur.execute(sql,(vlan_id2,username))    
            conn.commit() 
            self.update_user_cache(username)     

    ###############################################################################
    # roster method                                                              ####
    ############################################################################### 

    @cache.cache('get_roster',expire=__cache_timeout__)   
    def get_roster(self,mac_addr):
        if mac_addr:
            mac_addr = mac_addr.upper()
        roster = None
        with Cursor(self.dbpool) as cur:
            cur.execute("select * from slc_rad_roster where mac_addr = %s ",(mac_addr,))
            roster =  cur.fetchone()
        print roster
        if  roster:
            now = create_time = datetime.datetime.now()
            roster_start = datetime.datetime.strptime(roster['begin_time'],"%Y-%m-%d")
            roster_end = datetime.datetime.strptime(roster['end_time'],"%Y-%m-%d")
            if now < roster_start or now > roster_end:
                return None
            return roster
            
    def is_black_roster(self,mac_addr):
        roster = self.get_roster(mac_addr)
        return roster and roster['roster_type'] == 1 or False
        
    def is_white_roster(self,mac_addr):
        roster = self.get_roster(mac_addr)
        return roster and roster['roster_type'] == 0 or False
    
    def update_roster_cache(self,mac_addr):
        cache.invalidate(self.get_roster,'get_roster', str(mac_addr))
        cache.invalidate(self.get_roster,'get_roster', unicode(mac_addr))

    ###############################################################################
    # product method                                                         ####
    ############################################################################### 

    @cache.cache('get_product',expire=__cache_timeout__)   
    def get_product(self,product_id):
        with Cursor(self.dbpool) as cur:
            cur.execute("select * from slc_rad_product where id = %s ",(product_id,))
            return cur.fetchone()  

    @cache.cache('get_product_attrs',expire=__cache_timeout__)  
    def get_product_attrs(self,product_id):
        with Cursor(self.dbpool) as cur:
            cur.execute("select * from slc_rad_product_attr where product_id = %s ",(product_id,))
            return cur.fetchall()  

    def update_product_cache(self,product_id):
        cache.invalidate(self.get_product,'get_product',product_id)
        cache.invalidate(self.get_product_attrs,'get_product_attrs',product_id)
        
    ###############################################################################
    # cache method                                                            ####
    ###############################################################################
    
    def update_all_cache(self):
        from beaker.cache import cache_managers
        for _cache in cache_managers.values():
            _cache.clear()


    ###############################################################################
    # online method                                                            ####
    ############################################################################### 
          
    def is_online(self,nas_addr,acct_session_id):
        with Cursor(self.dbpool) as cur: 
            sql = 'select count(id) as online from slc_rad_online where  nas_addr = %s and acct_session_id = %s'
            cur.execute(sql,(nas_addr,acct_session_id)) 
            return cur.fetchone()['online'] > 0

    def count_online(self,account_number):
        with Cursor(self.dbpool) as cur: 
            sql = 'select count(id) as online from slc_rad_online where  account_number = %s'
            cur.execute(sql,(account_number,)) 
            return cur.fetchone()['online']

    def get_online(self,nas_addr,acct_session_id):
        with Cursor(self.dbpool) as cur: 
            sql = 'select * from slc_rad_online where  nas_addr = %s and acct_session_id = %s'
            cur.execute(sql,(nas_addr,acct_session_id)) 
            return cur.fetchone()     

    def get_nas_onlines(self,nas_addr):
        with Cursor(self.dbpool) as cur: 
            sql = 'select * from slc_rad_online where nas_addr = %s'
            cur.execute(sql,(nas_addr,)) 
            return cur.fetchall()        

    def add_online(self,online):
        with Connect(self.dbpool) as conn:
            cur = conn.cursor()
            keys = ','.join(online.keys())
            vals = ",".join(["'%s'"% c for c in online.values()])
            sql = 'insert into slc_rad_online (%s) values(%s)'%(keys,vals)
            cur.execute(sql)
            conn.commit()
            
    def update_online(self,online):
        with Connect(self.dbpool) as conn:
            cur = conn.cursor()
            online_sql = """update slc_rad_online set 
                billing_times = %s,
                input_total = %s,
                output_total = %s
                where nas_addr = %s and acct_session_id = %s
            """
            cur.execute(online_sql,(
                online['billing_times'],
                online['input_total'],
                online['output_total'],
                online['nas_addr'],
                online['acct_session_id']
            ))
            conn.commit()

    def update_billing(self,billing,time_length=0,flow_length=0):
        with Connect(self.dbpool) as conn:
            cur = conn.cursor()
            # update account
            balan_sql = """update slc_rad_account set 
                balance = %s,
                time_length=%s,
                flow_length=%s
                where account_number = %s
            """
            cur.execute(balan_sql,(
                billing.balance,
                time_length,
                flow_length,
                billing.account_number
            ))
            
            # update online
            online_sql = """update slc_rad_online set 
                billing_times = %s,
                input_total = %s,
                output_total = %s
                where nas_addr = %s and acct_session_id = %s
            """
            cur.execute(online_sql,(
                billing.acct_session_time,
                billing.input_total,
                billing.output_total,
                billing.nas_addr,
                billing.acct_session_id
            ))
            
            # update billing
            keys = ','.join(billing.keys())
            vals = ",".join(["'%s'"% c for c in billing.values()])
            billing_sql = 'insert into slc_rad_billing (%s) values(%s)'%(keys,vals)
            cur.execute(billing_sql)
            conn.commit()
            
        self.update_user_cache(billing.account_number) 
    
    def del_online(self,nas_addr,acct_session_id):
        with Connect(self.dbpool) as conn:
            cur = conn.cursor()
            sql = 'delete from slc_rad_online where nas_addr = %s and acct_session_id = %s'
            cur.execute(sql,(nas_addr,acct_session_id))
            conn.commit()

    def add_ticket(self,ticket):
        _ticket = ticket.copy()
        for _key in _ticket:
            if _key not in ticket_fds:
                del ticket[_key]
        with Connect(self.dbpool) as conn:
            cur = conn.cursor()
            keys = ','.join(ticket.keys())
            vals = ",".join(["'%s'"% c for c in ticket.values()])
            sql = 'insert into slc_rad_ticket (%s) values(%s)'%(keys,vals)
            cur.execute(sql)
            conn.commit()

    def unlock_online(self,nas_addr,acct_session_id,stop_source):
        bsql = ''' insert into slc_rad_ticket (
        account_number,acct_session_id,acct_start_time,nas_addr,framed_ipaddr,start_source,
        acct_session_time,acct_stop_time,stop_source) values(
         %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''' 
        def _ticket(online):
            ticket = []
            ticket.append(online['account_number'])
            ticket.append(online['acct_session_id'])
            ticket.append(online['acct_start_time'])
            ticket.append(online['nas_addr'])
            ticket.append(online['framed_ipaddr'])
            ticket.append(online['start_source'])
            _datetime = datetime.datetime.now()
            _starttime = datetime.datetime.strptime(online['acct_start_time'],"%Y-%m-%d %H:%M:%S")
            session_time = (_datetime - _starttime).seconds
            stop_time = _datetime.strftime( "%Y-%m-%d %H:%M:%S")
            ticket.append(session_time)
            ticket.append(stop_time)
            ticket.append(stop_source)
            return ticket

        def _unlock_one():
            ticket = None
            with Connect(self.dbpool) as conn:
                cur = self.dbpool.cursor(conn)
                sql = 'select * from slc_rad_online where  nas_addr = %s and acct_session_id = %s'
                cur.execute(sql,(nas_addr,acct_session_id)) 
                online = cur.fetchone()
                if online:
                    ticket = _ticket(online) 
                    dsql = 'delete from slc_rad_online where nas_addr = %s and acct_session_id = %s'
                    cur.execute(dsql,(nas_addr,acct_session_id))
                    cur.execute(bsql,ticket)
                    conn.commit()  

        def _unlock_many():
            tickets = []
            with Connect(self.dbpool) as conn:
                cur = self.dbpool.cursor(conn)
                cur.execute('select * from slc_rad_online where nas_addr = %s',(nas_addr,)) 
                for online in cur:
                    tickets.append(_ticket(online))
                if tickets:     
                    cur.executemany(bsql,tickets)
                    cur.execute('delete from slc_rad_online where nas_addr = %s',(nas_addr,))
                    conn.commit()                  

        if acct_session_id:_unlock_one()
        else:_unlock_many()

    
store = Store()






