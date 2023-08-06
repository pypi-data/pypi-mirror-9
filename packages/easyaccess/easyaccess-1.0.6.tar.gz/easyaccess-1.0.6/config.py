#Config file
import ConfigParser
import getpass
import time
import sys
import cx_Oracle
import os

configcomment="""#
# Easyaccess default parameters
# 
# database  : Default is dessci, change to desoper, destest and others
#             Make sure the db-"database" section is in the .desservices.ini
# editor    : Deafault editor to open from inside easyaccess if $EDITOR is not set
# prefetch  : Prefetch number of rows to get from oracle (not the number of total rows)
#           : This determine the number of trips to the DB to get all results from query
# histcache : The number of line in the history cache (when possible)
# timeout   : The time in seconds before closing a connection for a query to print on screen
#             If the results are redirected to a file there is not a timeout
"""

descomment="""#
# DES services configuration
# Please modify the passwords accordingly
#
"""

def get_config(configfile):
    """
    Loads config file or create one if not
    Returns a configParser object
    """
    config = ConfigParser.ConfigParser()
    configwrite = False
    check=config.read(configfile)
    if check == []:
        configwrite= True
        print '\nCreating a configuration file... at %s\n' %configfile

    if not config.has_section('easyaccess'):
        configwrite = True
        config.add_section('easyaccess')
    if not config.has_option('easyaccess','database'): configwrite = True ;config.set('easyaccess','database','dessci')
    if not config.has_option('easyaccess','editor'): configwrite = True ;config.set('easyaccess','editor','nano')
    if not config.has_option('easyaccess','prefetch'): configwrite = True ;config.set('easyaccess','prefetch',10000)
    if not config.has_option('easyaccess','histcache'): configwrite = True ;config.set('easyaccess','histcache',5000)
    if not config.has_option('easyaccess','timeout'): configwrite = True ;config.set('easyaccess','timeout',900)
    
    if not config.has_section('display'):
        configwrite=True
        config.add_section('display')
    if not config.has_option('display','color_terminal'): configwrite = True ;config.set('display','color_terminal','yes')
    if not config.has_option('display','loading_bar'): configwrite = True ;config.set('display','loading_bar','yes')
    if not config.has_option('display','max_rows'): configwrite = True ;config.set('display','max_rows',1500)
    if not config.has_option('display','width'): configwrite = True ;config.set('display','width',1000)
    if not config.has_option('display','max_columns'): configwrite = True ;config.set('display','max_columns',50)
    
    check = True
    if configwrite == True:
        check=write_config(configfile, config)
        config.read(configfile)
    if check:
        return config


def write_config(configfile, config_ob):
    """
    Writes configuration file
    """
    try:
        F=open(configfile,'w')
        F.write(configcomment+'\n')
        config_ob.write(F)
        F.flush()
        F.close()
        return True
    except:
        print "Problems writing the configuration  file %s" % configfile
        return False


def get_desconfig(desfile,db):
    """
    Loads des config file or create one if not

    """
    server_n='leovip148.ncsa.uiuc.edu'
    port_n='1521'

    if not db[:3] == 'db-': db='db-'+db
    config = ConfigParser.ConfigParser()
    configwrite = False
    check=config.read(desfile)
    if check == []:
        configwrite= True
        print '\nError in DES_SERVICES config file, creating a new one...'
        print 'File might not exists or is not configured'
        print 

    databases = ['db-desoper','db-dessci','db-destest'] #most used ones anyways

    if db not in databases and not config.has_section(db):
        check_db=raw_input('\nDB entered not dessci, desoper or destest or in DES_SERVICE file, continue anyway [y]/n\n')
        if check_db in ('n','N','no','No','NO'): sys.exit(0)

    if not config.has_section(db):
        print '\nAdding section %s to des_service file\n' % db 
        configwrite = True
        kwargs = {'host': server_n, 'port': port_n, 'service_name': db[3:]}
        dsn = cx_Oracle.makedsn(**kwargs)
        good=False
        for i in range(3):
            try:
                user=raw_input('Enter username : ')
                pw1=getpass.getpass(prompt='Enter password : ')
                ctemp=cx_Oracle.connect(user,pw1,dsn=dsn)
                good = True
                break
            except:
                (type, value, traceback) = sys.exc_info()
                print value
                if value.message.code == 1017: pass    
                else: sys.exit(0)
        if good: 
            ctemp.close()
        else:
            print '\n Check your credentials and/or database access\n'
            sys.exit(0)
        config.add_section(db)
        
    if not config.has_option(db,'user'): configwrite = True ;config.set(db,'user',user)
    if not config.has_option(db,'passwd'): configwrite = True ;config.set(db,'passwd',pw1)
    if not config.has_option(db,'name'): configwrite = True ;config.set(db,'name',db[3:])
    if not config.has_option(db,'server'): configwrite = True ;config.set(db,'server',server_n)
    if not config.has_option(db,'port'): configwrite = True ;config.set(db,'port',port_n)

    
    check = True
    if configwrite == True:
        check=write_desconfig(desfile, config)
        config.read(desfile)
    if check:
        return config
    

def write_desconfig(configfile, config_ob):
    """
    Writes configuration file
    """
    try:
        F=open(configfile,'w')
        F.write(descomment+'\n')
        config_ob.write(F)
        F.flush()
        F.close()
        os.chmod(configfile,2**8+2**7) #rw-------  
        return True
    except:
        print "Problems writing the configuration  file %s" % configfile
        return False

