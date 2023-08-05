# -*- coding: utf-8 -*-
#
#  Copyright (C) 2014 Cornelius Kölbel
#  License:  AGPLv3
#  contact:  cornelius@privacyidea.org
#
# This code is free software; you can redistribute it and/or
# modify it under the terms of the GNU AFFERO GENERAL PUBLIC LICENSE
# License as published by the Free Software Foundation; either
# version 3 of the License, or any later version.
#
# This code is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU AFFERO GENERAL PUBLIC LICENSE for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import logging
import yaml

from UserIdResolver import UserIdResolver
from UserIdResolver import getResolverClass

from sqlalchemy import and_
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from privacyidea.lib.phppass import PasswordHash
import traceback
import hashlib
from base64 import (b64decode,
                    b64encode)
import binascii

log = logging.getLogger(__name__)
ENCODING = "utf-8"

SQLSOUP_LOADED = False
try:
    from sqlsoup import SQLSoup
    SQLSOUP_LOADED = True
except:
    pass  # pragma: no cover

if SQLSOUP_LOADED is False:  # pragma: no cover
    try:
        from sqlalchemy.ext.sqlsoup import SQLSoup
        SQLSOUP_LOADED = True
    except:
        log.error("SQLSoup could not be loaded!")
        pass

       
class IdResolver (UserIdResolver):

    searchFields = {"username": "text",
                    "userid": "numeric",
                    "phone": "text",
                    "mobile": "text",
                    "surname": "text",
                    "givenname": "text",
                    "email": "text"
                    }

    @classmethod
    def setup(cls, config=None, cache_dir=None):
        '''
        this setup hook is triggered, when the server
        starts to serve the first request

        :param config: the privacyidea config
        :type  config: the privacyidea config dict
        '''
        log.info("Setting up the SQLResolver")
        return
    
    def __init__(self):
        self.resolverId = ""
        self.server = ""
        self.driver = ""
        self.database = ""
        self.port = 0
        self.limit = 100
        self.user = ""
        self.password = ""
        self.table = ""
        self.map = {}
        self.reverse_map = {}
        self.where = ""
        self.encoding = ""
        self.conParams = ""
        self.connect_string = ""
        self.session = None
        return

    def getSearchFields(self):
        return self.searchFields

    def checkPass(self, uid, password):
        """
        This function checks the password for a given uid.
        - returns true in case of success
        -         false if password does not match
        
        """
        def _check_ssha(pw_hash, password, hashfunc, length):
            pw_hash_bin = b64decode(pw_hash.split("}")[1])
            digest = pw_hash_bin[:length]
            salt = pw_hash_bin[length:]
            hr = hashfunc(password)
            hr.update(salt)
            return digest == hr.digest()
        
        def _check_sha(pw_hash, password):
            b64_db_password = pw_hash[5:]
            hr = hashlib.sha1(password).digest()
            b64_password = b64encode(hr)
            return b64_password == b64_db_password
        
        def _otrs_sha256(pw_hash, password):
            hr = hashlib.sha256(password)
            digest = binascii.hexlify(hr.digest())
            return pw_hash == digest
       
        res = False
        userinfo = self.getUserInfo(uid)
        
        database_pw = userinfo.get("password", "XXXXXXX")
        if database_pw[:2] == "$P":
            # We have a phpass (wordpress) password
            PH = PasswordHash()
            res = PH.check_password(password, userinfo.get("password"))
        # check salted hashed passwords
        elif database_pw[:6].upper() == "{SSHA}":
            res = _check_ssha(database_pw, password, hashlib.sha1, 20)
        elif database_pw[:9].upper() == "{SSHA256}":
            res = _check_ssha(database_pw, password, hashlib.sha256, 32)
        elif database_pw[:9].upper() == "{SSHA512}":
            res = _check_ssha(database_pw, password, hashlib.sha512, 64)
        # check for hashed password.
        elif userinfo.get("password", "XXXXX")[:5].upper() == "{SHA}":
            res = _check_sha(database_pw, password)
        elif len(userinfo.get("password")) == 64:
            # OTRS sha256 password
            res = _otrs_sha256(database_pw, password)
        
        return res
    
    def getUserInfo(self, userId):
        '''
        This function returns all user info for a given userid/object.
        
        :param userId: The userid of the object
        :type userId: string
        :return: A dictionary with the keys defined in self.map
        :rtype: dict
        '''
        userinfo = {}
        
        try:
            conditions = []
            column = self.map.get("userid")
            conditions.append(getattr(self.TABLE, column).like(userId))
            filter_condition = and_(*conditions)
            result = self.session.query(self.TABLE).filter(filter_condition)
                                                      
            for r in result:
                if len(userinfo.keys()) > 0:
                    raise Exception("More than one user with userid %s found!"
                                    % userId)
                userinfo = self._get_user_from_mapped_object(r)
        except Exception as exx:
            log.error("Could not get the userinformation: %r" % exx)
        
        return userinfo
    
    def getUsername(self, userId):
        '''
        Returns the username/loginname for a given userid
        :param userid: The userid in this resolver
        :type userid: string
        :return: username
        :rtype: string
        '''
        info = self.getUserInfo(userId)
        return info.get('username', "")
   
    def getUserId(self, LoginName):
        '''
        resolve the loginname to the userid.
        
        :param LoginName: The login name from the credentials
        :type LoginName: string
        :return: UserId as found for the LoginName
        '''
        userid = ""
        
        try:
            conditions = []
            column = self.map.get("username")
            conditions.append(getattr(self.TABLE, column).like(LoginName))
            filter_condition = and_(*conditions)
            result = self.session.query(self.TABLE).filter(filter_condition)
                                                      
            for r in result:
                if userid != "":
                    raise Exception("More than one user with loginname"
                                    " %s found!" % LoginName)
                user = self._get_user_from_mapped_object(r)
                userid = user["id"]
        except Exception as exx:
            log.error("Could not get the userinformation: %r" % exx)
        
        return userid
    
    def _get_user_from_mapped_object(self, ro):
        '''
        :param r: row
        :type r: Mapped Object
        :return: User
        :rtype: dict
        '''
        r = ro.__dict__
        user = {}
        try:
            if self.map.get("userid") in r:
                user["id"] = r[self.map.get("userid")]
        except UnicodeEncodeError:
            log.error("Failed to convert user: %r" % r)
            log.error(traceback.format_exc())
        
        for key in ["username",
                    "surname",
                    "givenname",
                    "email",
                    "mobile",
                    "phone",
                    "password"]:
            try:
                if r.get(self.map.get(key)):
                    val = r.get(self.map.get(key))
                    # val is a unicode!
                    # log.error("CKO: %r" % val)
                    # log.error("CKO: %r" % type(val))
                    user[key] = val
            except UnicodeEncodeError:
                log.error("Failed to convert user: %r" % r)
                log.error(traceback.format_exc())
        
        return user

    def getUserList(self, searchDict=None):
        '''
        :param searchDict: A dictionary with search parameters
        :type searchDict: dict
        :return: list of users, where each user is a dictionary
        '''
        users = []
        conditions = []
        if searchDict is None:
            searchDict = {}
        for key in searchDict.keys():
            column = self.map.get(key)
            value = searchDict.get(key)
            value = value.replace("*", "%")
            conditions.append(getattr(self.TABLE, column).like(value))
            
        if self.where:
            # this might result in erros if the
            # administrator enters nonsense
            (w_column, w_cond, w_value) = self.where.split()
            if w_cond.lower() == "like":
                conditions.append(getattr(self.TABLE, w_column).like(w_value))
            elif w_cond == "==":
                conditions.append(getattr(self.TABLE, w_column) == w_value)
            elif w_cond == ">":
                conditions.append(getattr(self.TABLE, w_column) > w_value)
            elif w_cond == "<":
                conditions.append(getattr(self.TABLE, w_column) < w_value)
        filter_condition = and_(*conditions)

        result = self.session.query(self.TABLE).\
            filter(filter_condition).\
            limit(self.limit)
                                                      
        for r in result:
            user = self._get_user_from_mapped_object(r)
            if "id" in user:
                users.append(user)
        return users
    
    def getResolverId(self):
        '''
        Returns the resolver Id
        This should be an Identifier of the resolver, preferable the type
        and the name of the resolver.
        '''
        return "sqlresolver." + self.resolverId

    @classmethod
    def getResolverClassType(cls):
        return 'sqlresolver'

    def getResolverType(self):
        return IdResolver.getResolverClassType()
    
    def loadConfig(self, config, conf):
        '''
        Load the config from conf.
        
        :param config: The configuration from the Config Table
        :type config: dict
        :param conf: the instance of the configuration
        :type conf: string
        
        The information which config entries we need to load is taken from
            manage.js: function save_sql_config
                    
        '''
        self.resolverId = conf
        self.server = self.getConfigEntry(config,
                                          'privacyidea.sqlresolver.Server',
                                          conf)
        self.driver = self.getConfigEntry(config,
                                          'privacyidea.sqlresolver.Driver',
                                          conf)
        self.database = self.getConfigEntry(config,
                                            'privacyidea.sqlresolver.Database',
                                            conf)
        self.port = self.getConfigEntry(config,
                                        'privacyidea.sqlresolver.Port',
                                        conf, required=False)
        self.limit = self.getConfigEntry(config,
                                         'privacyidea.sqlresolver.Limit',
                                         conf, required=False, default=100)
        self.user = self.getConfigEntry(config,
                                        'privacyidea.sqlresolver.User',
                                        conf, required=False)
        self.password = self.getConfigEntry(config,
                                            'privacyidea.sqlresolver.Password',
                                            conf, required=False)
        self.table = self.getConfigEntry(config,
                                         'privacyidea.sqlresolver.Table',
                                         conf)
        usermap = self.getConfigEntry(config,
                                      'privacyidea.sqlresolver.Map',
                                      conf)
        self.map = yaml.load(usermap)
        self.reverse_map = dict([[v, k] for k, v in self.map.items()])
        self.where = self.getConfigEntry(config,
                                         'privacyidea.sqlresolver.Where',
                                         conf, required=False)
        self.encoding = self.getConfigEntry(config,
                                            'privacyidea.sqlresolver.Encoding',
                                            conf,
                                            required=False, default="latin1")
        self.conParams = self.getConfigEntry(config,
                                             'privacyidea.sqlresolver.'
                                             'conParams',
                                             conf, required=False)
        
        # create the connectstring like
        params = {'Port': self.port,
                  'Password': self.password,
                  'conParams': self.conParams,
                  'Driver': self.driver,
                  'User': self.user,
                  'Server': self.server,
                  'Database': self.database}
        self.connect_string = self._create_connect_string(params)
        log.info("using the connect string %s" % self.connect_string)
        self.engine = create_engine(self.connect_string,
                                    encoding=self.encoding)
        # create a configured "Session" class
        Session = sessionmaker(bind=self.engine)

        # create a Session
        self.session = Session()
        self.db = SQLSoup(self.engine)
        self.TABLE = self.db.entity(self.table)
        
        return self

    def getResolverDescriptor(self):
        descriptor = {}
        typ = self.getResolverType()
        descriptor['clazz'] = "useridresolver.SQLIdResolver.IdResolver"
        descriptor['config'] = {'Server': 'string',
                                'Driver': 'string',
                                'Database': 'string',
                                'User': 'string',
                                'Password': 'string',
                                'Port': 'int',
                                'Limit': 'int',
                                'Table': 'string',
                                'Map': 'string',
                                'Where': 'string',
                                'Encoding': 'string',
                                'conParams': 'string'}
        return {typ: descriptor}

    def getConfigEntry(self, config, key, conf, required=True, default=None):
        ckey = key
        cval = ""
        if conf != "" or None:
            ckey = ckey + "." + conf
            if ckey in config:
                cval = config[ckey]
        if cval == "":
            if key in config:
                cval = config[key]
        if cval == "" and required is True:
            raise Exception("missing config entry: " + key)
        if cval == "" and default:
            cval = default
        return cval
            
    @classmethod
    def _create_connect_string(self, param):
        '''
        create the connectstring
        
        Port, Password, conParams, Driver, User,
        Server, Database
        '''
        port = ""
        password = ""
        conParams = ""
        if param.get("Port"):
            port = ":%s" % param.get("Port")
        if param.get("Password"):
            password = ":%s" % param.get("Password")
        if param.get("conParams"):
            conParams = "?%s" % param.get("conParams")
        connect_string = "%s://%s%s%s%s%s/%s%s" % (param.get("Driver", ""),
                                                   param.get("User", ""),
                                                   password,
                                                   "@" if (param.get("User")
                                                           or
                                                           password) else "",
                                                   param.get("Server", ""),
                                                   port,
                                                   param.get("Database", ""),
                                                   conParams)
        # SQLAlchemy does not like a unicode connect string!
        if param.get("Driver").lower() == "sqlite":
            connect_string = str(connect_string)
        log.debug("SQL connectstring: %r" % connect_string)
        return connect_string
            
    @classmethod
    def testconnection(self, param):
        '''
        This function lets you test the to be saved SQL connection.
              
        :param param: A dictionary with all necessary parameter
                        to test the connection.
        :type param: dict
        
        :return: Tuple of success and a description
        :rtype: (bool, string)
        
        Parameters are: Server, Driver, Database, User, Password, Port,
                        Limit, Table, Map
                        Where, Encoding, conParams
            
        '''
        num = -1
        desc = None
        
        connect_string = self._create_connect_string(param)
        log.info("using the connect string %s" % connect_string)
        engine = create_engine(connect_string)
        # create a configured "Session" class
        session = sessionmaker(bind=engine)()
        db = SQLSoup(engine)
        TABLE = db.entity(param.get("Table"))
            
        try:
            result = session.query(TABLE).count()
            num = result
            desc = "Found %i users." % num
        except Exception as exx:
            desc = "failed to retrieve users: %s" % exx
            
        return (num, desc)
    
    
if __name__ == "__main__":  # pragma: no cover

    print " SQLIdResolver - IdResolver class test "
        
    y = getResolverClass("SQLIdResolver", "IdResolver")()
    
    print y
    
    y.loadConfig({'privacyidea.sqlresolver.Driver': 'mysql',
                  'privacyidea.sqlresolver.Database': 'wordpress',
                  'privacyidea.sqlresolver.Server': 'localhost',
                  'privacyidea.sqlresolver.User': 'root',
                  'privacyidea.sqlresolver.Password': 'mspw.',
                  'privacyidea.sqlresolver.Limit': 2,
                  'privacyidea.sqlresolver.Encoding': "utf-8",
                  'privacyidea.sqlresolver.Table': 'wp_users',
                  'privacyidea.sqlresolver.Map': '{ "username": "user_login", \
                      "userid" : "ID", \
                      "email" : "user_email", \
                      "surname" : "display_name", \
                      "givenname" : "user_nicename", \
                      "password" : "user_pass"}',
                  },
                 "")

    print "Config loaded"
    
    print "====== getUserList =========="
    result = y.getUserList()
    for entry in result:
        print entry
    print "======== getUserId ==============="

    user = "admin"
    loginId = y.getUserId(user)

    print " %s -  %s" % (user, loginId)

    print " reId - " + y.getResolverId()
    print "======== getUserInfo ==============="

    ret = y.getUserInfo(loginId)
    print "Userinfo for %r" % loginId
    print ret
    print "============ checkPass =============="
    uid = y.getUserId("cornelius")
    ret = y.checkPass(uid, "test")
    print ret
    ret = y.checkPass(uid, "wrong")
    print ret
    print "============ getUserList ============"
    
    ret = y.getSearchFields()
    
    search = {"username": "admin"}
    
    print "=== we should only see the admin ===="
    ret = y.getUserList(search)
    for entry in ret:
        print entry
