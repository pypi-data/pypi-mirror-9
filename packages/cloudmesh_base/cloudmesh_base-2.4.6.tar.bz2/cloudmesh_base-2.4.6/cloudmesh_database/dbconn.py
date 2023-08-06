from __future__ import print_function
import traceback

from cloudmesh_base.locations import config_file
from cloudmesh_base.ConfigDict import ConfigDict
from cloudmesh_base.logger import LOGGER

from pymongo import MongoClient
from mongoengine import connect

# Changes of import in existing cloudmesh code:
#
## FROM:
# from cloudmesh.config.cm_config import get_mongo_db, get_mongo_dbname_from_collection, DBConnFactory
## TO:
# from cloudmesh_database.dbconn import get_mongo_db, get_mongo_dbname_from_collection, DBConnFactory
##
log = LOGGER(__file__)

MONGOCLIENT = 0
MONGOENGINE = 1

class DBConnFactory(object):
    connectors = {}
    DBCONFIG = None
    TYPE_MONGOCLIENT = MONGOCLIENT
    TYPE_MONGOENGINE = MONGOENGINE

    @classmethod
    def getconn(cls, dbname, clientType=MONGOCLIENT):

        conn = None
        if dbname:
            dbkey = "%s_%s" % (dbname, clientType)
            if dbkey in cls.connectors:
                # print "RETURNING AN EXISTING DB CONNECTOR FROM FACTORY"
                conn = cls.connectors[dbkey]
            else:
                if cls.DBCONFIG is None:
                    cls.DBCONFIG = {}
                    config = dbconf().get("cloudmesh.server.mongo")
                    cls.DBCONFIG["host"] = config["host"]
                    cls.DBCONFIG["port"] = int(config["port"])
                    cls.DBCONFIG["username"] = config["username"]
                    cls.DBCONFIG["password"] = config["password"]

                if clientType == MONGOCLIENT:
                    if cls.DBCONFIG["username"] and cls.DBCONFIG["password"]:
                        uri = "mongodb://{0}:{1}@{2}:{3}/{4}".format(cls.DBCONFIG["username"],
                                                                     cls.DBCONFIG[
                                                                         "password"],
                                                                     cls.DBCONFIG[
                                                                         "host"],
                                                                     cls.DBCONFIG[
                                                                         "port"],
                                                                     dbname)
                    else:
                        uri = "mongodb://{2}:{3}/{4}".format(cls.DBCONFIG["username"],
                                                             cls.DBCONFIG[
                                                                 "password"],
                                                             cls.DBCONFIG["host"],
                                                             cls.DBCONFIG["port"],
                                                             dbname)
                    try:
                        conn = MongoClient(uri)[dbname]
                    except:
                        msg = "Failed to connect to Mongoclient DB:\n\t%s" % uri
                        print(msg)
                        log.error(msg)

                elif clientType == MONGOENGINE:
                    try:
                        conn = connect(db=dbname,
                                       alias=dbname,
                                       host=cls.DBCONFIG["host"],
                                       port=cls.DBCONFIG["port"],
                                       username=cls.DBCONFIG["username"],
                                       password=cls.DBCONFIG["password"])
                    except:
                        msg = "Failed to connect to MongoEngine DB:\n\t%s" % dbname
                        print(msg)
                        log.error(msg)
                        log.error(traceback.format_exc())
                # put the newly created connection object into factory
                cls.connectors[dbkey] = conn
        return conn

def get_mongo_db(mongo_collection, clientType=MONGOCLIENT):
    """
    Read in the mongo db information from the cloudmesh_server.yaml
    """
    # DEBUG
    # try:
    #    import sys
    #    _args = locals()
    #    del(_args['self'])
    #    log.debug("[{0}()] called with [{1}]".format(sys._getframe().f_code.co_name,
    #                                    str(_args)))
    #except:
    #    pass

    db_name = get_mongo_dbname_from_collection(mongo_collection)

    conn = None

    db = DBConnFactory.getconn(db_name, clientType)

    if db:
        conn = db[mongo_collection]
    else:
        try:
            log.debug("connection failed to {0}".format(db_name))
        except:
            pass

    return conn

def get_mongo_dbname_from_collection(mongo_collection):
    config = dbconf().get("cloudmesh.server.mongo")
    db_name = None
    try:
        db_name = config["collections"][mongo_collection]['db']
    except:
        pass
    return db_name
    
class dbconf(ConfigDict):

    """
    reads db config info from cloudmesh_database.yaml
    """
    filename = config_file("/cloudmesh_database.yaml")

    def __init__(self, filename=None):
        if filename is None:
            filename = self.filename
        ConfigDict.__init__(self, filename=filename)

# ----------------------------------------------------------------------
# MAIN METHOD FOR TESTING and example to use
# See also examples in the examples directory
# ----------------------------------------------------------------------
def main():
    from cloudmesh_database.dbconn import get_mongo_db, get_mongo_dbname_from_collection, DBConnFactory
    # this returns a mongoengine connection to the db of the 'experiment' collection (from yaml config)
    conn1 = get_mongo_db("experiment", DBConnFactory.TYPE_MONGOENGINE)
    print (conn1)
    # this returns a pymongo collection for 'pbs'
    conn2 = get_mongo_db("pbs")
    print (conn2)
	
if __name__ == "__main__":
	main()
