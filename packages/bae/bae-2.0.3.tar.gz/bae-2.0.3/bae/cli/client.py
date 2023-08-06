#*- coding : utf-8 -*-
'''
Bae Client contains main apis for BAE

@Author    : zhangguanxing01@baidu.com
@Copyright : 2013 Baidu Inc. 
@Date      : 2013-07-26 11:09:00
'''

import sys
import re
import os
import time
import messages
import code_tool            
import shutil
import json
import Auth_tools

from   bae.cli.messages          import g_messager
from   bae.config.parser    import BaeParser
from   bae.rest.rest        import BaeRest
from   bae.config.constants import *
from   bae.config.config    import *
from   bae.errors           import *

class BaeClient:
    def __init__(self):
        pass
    def start(self):
        parser = BaeParser()
        
        if parser.debug:
            messages.DEBUG = True
            g_messager.debug("Debug mode ON")
        else:
            messages.DEBUG = False

        #Load Global Configs or Local App Configs
        #if cmd is not init or setup, config non-exist will considered an error
        try:
            self.globalconfig = BaeGlobalConfig()
            self.globalconfig.model.use_color = True
            self.globalconfig.load()
            #set global message settings
            g_messager.use_color = self.globalconfig.model.use_color
            g_messager.use_cn    = self.globalconfig.model.use_cn or False
            if parser.cmd == "login":
                raise BaeConfigError("Nothing")

            Auth_tools.authTool.stringkey(
                self.globalconfig.model.user.access_key,
                self.globalconfig.model.user.secret_key,
                int(time.time()),
                1200)
            self.rest = BaeRest(auth_tool = Auth_tools.authTool, debug = parser.debug)
            self._check_version()
        except (BaeConfigError, IOError):
            if parser.cmd != "login":
                g_messager.suggestion("Bae Configuration not founded or broken, please use '{prog} login' to "
                                   "init your bae environment"
                                   .format(prog=PROG_NAME))
                sys.exit(-1)
            else:
                self.rest = BaeRest(None, debug = parser.debug)
        try:
            self.appconfig = DevAppConfig()
            self.appconfig.load()
        except (BaeConfigError, IOError):
            if parser.cmd != "login" and parser.appcmd != "setup" and not parser.force:
                g_messager.suggestion("NO local app directory founded, Please visit "+\
                                   "{0} apply a appid and use '{1} app setup' ".format(DEVELOPER, PROG_NAME) +\
                                    "to connect current directory to bae")
                g_messager.exception()
                sys.exit(-1)
            else:
                g_messager.debug("Load app config done")

            #If User set appid mannualy, this means he didn't want any local cache
            self.appconfig = None

        subcmd = "parser.{0}cmd".format(parser.cmd)

        if eval (subcmd):
            fullcmd = "{0}_{1}".format(parser.cmd, eval(subcmd))
        else:
            fullcmd = parser.cmd

        try:
            #call subcmd functions
            getattr(self, fullcmd)(parser)
        except (BaeCliError, BaeRestError, BaeConfigError, KeyError, ValueError, TypeError, IOError):
            g_messager.exception()

    def _check_version(self):

        def cmp_version(a, b):
            return cmp(a.split('.'), b.split("."))

        data = {}
        data["tool_name"] = "cli"
        ret = self.rest.post(API_ENTRY + "/api/bae/app/getVersionInfo", data = data)
        dir(ret)
        min_ver = ret["minVersion"]
        cur_ver = ret["curVersion"]
        my_ver  = VERSION
        if cmp(my_ver, min_ver) < 0:
            g_messager.error("your BAE cli version is out of date, please run 'pip install bae --upgrade' to update")
            sys.exit(-1)
        if cmp(my_ver, cur_ver) < 0:
            g_messager.warning("new BAE cli version {0} availiable, please run 'pip install bae --upgrade'to update")

    def config(self, parser):
        try:
            k,v = parser.configitem.split("=")
            if v.lower() in ['y', 'yes', 'true', '1']:
                v = True
            elif v.lower() in ['n', 'no', 'false', '0']:
                v = False
            else:
                v = False

            setattr(self.globalconfig.model, k, v)
            self.globalconfig.save()
        except ValueError:
            g_messager.error("Config Format Error, Please use <Key>=<Value> pair (set one key once)")

    #Init Global Varaibles
    def login(self, parser):
        access_key = g_messager.input("input your access_key:")
        self.globalconfig.model.user.access_key = access_key
        secret_key = g_messager.input("input your secret_key:")
        self.globalconfig.model.user.secret_key = secret_key
        self.globalconfig.save()

        Auth_tools.authTool.stringkey(access_key,secret_key, int(time.time()),30)
        self.rest = BaeRest(auth_tool= Auth_tools.authTool, debug = parser.debug)
        try:
            self._check_version()
            g_messager.trace("login success")
        except Exception,e:
            g_messager.warning("AK/SK is invalid {msg}".format(msg = e.messages))

    def app_support(self, parser):
        data = {}

        ret = self.rest.get(API_ENTRY + "/api/bae/app/precreateEx", data = data)

        self.appconfig.model.solutions = [BaeSolution(_) for _ in ret["solutions"]]
        self.appconfig.save()

        g_messager.output("suppport language types:")
            
        for index, solution in enumerate(ret["solutions"]):
            g_messager.output("%d : %s" %(index+1, solution["name"]))
        self.appconfig.model.packages = [BasicPackage(_) for _ in ret["packageInfo"]["packlist"]]
        self.appconfig.save()
        g_messager.output("suppport packages:")
        index1=0
        self.supportpack={}
        for index, solution in enumerate(ret["packageInfo"]["packlist"]):
            if solution["type"] != "runtime":
                continue
            resources = []
            self.supportpack[index1]=solution
            index1+=1
            for k,v in solution["resource"].iteritems():
                resources.append(" %s %sM" %(k, v))
            g_messager.output("%d : %s" %(index+1, ",".join(resources)))
        userinfo=[ret["user"]]
        self.appconfig.model.userinfo = [BaeUserInfo(_) for _ in userinfo]
        self.appconfig.save()
    def app_setup(self, parser):
        if self.appconfig:
            answer=g_messager.yes_or_no("local app exists,clean up the .devapp file to setup again(Y) or  update app info(N) (Y/N):")
            if answer:
                cwd=os.getcwd()
                localdir= os.path.join(cwd,DEV_APP_CONFIG)
                try:
                    os.remove(localdir)
                except OSError, e:
                    g_messager.warning(str(e))
            else:
                parser.force = True
                self.app_update(parser)
                g_messager.trace("local app exists, try to update")
                return

        app_id = self._get_app_id(parser)
        #Require User Input a appid
        if app_id:
            g_messager.output("developer app id is no longer needed ");

        g_messager.output("BAE cli will setup this app in {curdir}".format(curdir= os.getcwd()))
        cwd = os.getcwd()
        self.appconfig = DevAppConfig(os.path.join(cwd, DEV_APP_CONFIG))

        try:
            self.appconfig.load_bae_app()
        except BaeConfigError:
            g_messager.warning("Load Bae Config Error, But setup will continued")

        self.appconfig.model.app_id   = app_id
        self.appconfig.bae_app_configs = self._app_cat()
        self.appconfig.save()

        for bae_app_config in self.appconfig.bae_app_configs:
            self._app_setup_bae(bae_app_config)

        #init support information
        self.app_support(parser)
        
    def app_update(self, parser):
        bae_app_confs = self._get_bae_confs(parser)
        if parser.force and self.appconfig:
            #TODO add delete logic
            #server_del_set = [conf for bae_app_confs if conf not in self.appconfig.bae_app_configs]
            #local_del_set  = [conf for self.appconfig.bae_app_configs if conf not in bae_app_confs]

            #for server_del_conf in server_del_set:
            #    g_messager.output("Local Cache {0} is Deleted in server side, would want delete local one?")
            pass

        if not bae_app_confs:
            return

        for bae_app_conf in bae_app_confs:
            self._app_setup_bae(bae_app_conf)
            bae_app_conf.save()

    def _do_publish(self, bae_app_conf):
        data = {}
        data["appid"] = bae_app_conf.model.appid
        data["url"]       = ""
        requestid         = self._gen_request_id()
        data["requestid"] = requestid.__str__()

        ret = self.rest.post(API_ENTRY + "/api/bae/app/republish", data = data)
        self._get_operation_log(requestid)

    def app_publish(self, parser):
        bae_app_conf  = self._get_cur_bae_conf(parser)
        
        if not bae_app_conf:
            g_messager.error("no local bae app found, please goto a bae app dir to publish code")
            sys.exit(-1)
        if not parser.local:
            self._do_publish(bae_app_conf)
        else:
            if bae_app_conf.model.lang_type == 'java':
                cmd = "bae_build %s %s %s"%(bae_app_conf.model.solution, bae_app_conf.dirname(), bae_app_conf.model.domain)
            else:
                cmd="bae_build %s %s %s"%(bae_app_conf.model.lang_type, bae_app_conf.dirname(), bae_app_conf.model.domain)
            os.system(cmd)
        
    def app_list(self, parser):
        if parser.detail:
            parser.force = True

        bae_app_confs = self._get_bae_confs(parser)

        if len(bae_app_confs) == 1:
            parser.single_list = True

        if parser.single_list:
            for bae_app_conf in bae_app_confs:
                    g_messager.output(str(bae_app_conf.model))
        else:
            if parser.detail:
                print bae_app_detail_table("Application Detail Table", [bae_app_conf.model.tuple() for bae_app_conf in bae_app_confs])
            else:
                print bae_app_table("Application General Infos (use --detail to see more)", [bae_app_conf.model.tuple() for bae_app_conf in bae_app_confs])

        if not parser.force:
            self.appconfig.bae_app_configs = bae_app_confs
            self.appconfig.save()

    def service_list(self, parser):
        data    = {}
        ret = self.rest.post(API_ENTRY + "/api/bae/service/getServiceList", data = data)
        
        services    = [Service(service_conf) for service_conf in ret["servList"]]
        #add an index to each tuple
        service_tuple = [tuple([idx] + list(service)) for idx, service in 
                         (zip ([str(i) for i in range(1, len(services)+1)], [service.tuple() for service in services]))
                         ]
        
        print service_table("Bae Service list", service_tuple)

    def service_status(self, parser):
        data    = {}
        ret = self.rest.post(API_ENTRY + "/api/bae/service/getResourceList", data = data)
        resources = [Resource(resource_conf) for resource_conf in ret]
        #This ugly code add index to a tuple
        resource_tuple = [tuple([idx] + list(resource)) for idx, resource in 
                         (zip ([str(i) for i in range(1, len(resources)+1)], [resource.tuple() for resource in resources]))
                         ]
        print resource_table("Your BAE Service List", resource_tuple)

    def service_mysql(self, parser):
        def _progress(uri, flag = True):
            timeout = 300
            if uri.startswith("import"):
                status_info = {"1": "waiting", "2": "downloading", "3": "importing", "10": "imported", "-1": "fail to import"}
            else:
                status_info = {"1": "waiting", "2": "exporting", "3": "compressing", "4": "uploading", "10": "exported", "-1": "fail to export"}
            start_time = time.time() 
            while 1:
                job_status = self.rest.get(API_ENTRY + "/api/bae/sqld/db/" + uri, data = data)
                msg = status_info.get(job_status.get("job_status"), "")
                if job_status["job_status"] == "-1":
                    msg += "\t Err:%s"%job_status["errmsg"]
                g_messager.trace("Status: %s"%msg)
                if job_status["job_status"] in ["10", "-1"] or time.time() - start_time > timeout or not flag:
                    break
                time.sleep(1)  

        data   = {}
        ret = self.rest.post(API_ENTRY + "/api/bae/service/getResourceList", data = data)
        database = filter(lambda x: x.serviceName == "BaeMySQLService", [Resource(resource_conf) for resource_conf in ret])
        if len(database) != 1:
            g_messager.warning("failed to get valid MySQL resource, please make sure your MySQL is enabled")
            sys.exit(-1)
        
        data["database_id"] = database[0].resourceName
        
        ### FIXME: the number of users' MySQL is more than 1, we also can deal with --db  
        if parser.database_id:
            data["database_id"] = parser.database_id
        # comments by pysqz
     
        mysql_action = parser.mysqlaction 
        
        if mysql_action == "import":
            if parser.FROM.startswith("http://") or parser.FROM.startswith("https://"):
                data['url'] = parser.FROM
                rest_uri = "importTask" 
            else:
                if ":" not in parser.FROM:
                    g_messager.warning("please set bcs FROM with 'bucket:object'")
                    sys.exit(-1)
                data['bucket'], data['object'] = parser.FROM.split(":", 1)
                rest_uri = "importBcs"
            
            ret = self.rest.post(API_ENTRY + "/api/bae/sqld/db/" + rest_uri, data = data)
            if ret.get("condition", -1) != 0:
                g_messager.error("failed to run mysql import, Err: %s"%ret["errmsg"])
                sys.exit(-1) 
                                   
            if parser.progress:
                _progress("importStat")
                                          
        elif mysql_action == "export":
            data['bucket'] = parser.TO
            data['compress'] = parser.format
                
            ret = self.rest.post(API_ENTRY + "/api/bae/sqld/db/exportTask", data = data)
            if ret.get("condition", -1) != 0:
                g_messager.error("failed to run mysql export, Err: %s"%ret["errmsg"])
                sys.exit(-1)
 
            if parser.progress:
                _progress("exportStat")  

        elif mysql_action == "status":
            if not parser.JOB or parser.JOB not in ["import", "export"]:
                g_messager.warning("please set argument with 'import' or 'export'")
                sys.exit(-1)
            
            _progress("%sStat"%parser.JOB, False) 
             
        else:
            g_messager.error("invalid argument, just suportted (import | export | status)")

    def domain_list(self, parser):
        parser.force = True
        bae_app_conf = self._get_cur_bae_conf(parser)
        
        if bae_app_conf is None:
            g_messager.warning("please  change to bae app directory")
            sys.exit(-1)
        if bae_app_conf.model.alias:
            g_messager.trace("domain alias: " + "||".join([str(alias) for alias in bae_app_conf.model.alias]))
        else:
            g_messager.warning("this app has no domain alias")

    def domain_add(self, parser):
        bae_app_conf = self._get_cur_bae_conf(parser)

        if not bae_app_conf:
            g_messager.error("Bae app not set or not exists in local cache")
            sys.exit(-1)

        data = {}
        data["domain"] = parser.domain
        data["appid"]   = bae_app_conf.model.appid
        ret = self.rest.post(API_ENTRY + "/api/bae/app/domainbind", data = data)

        g_messager.trace("Bind to " + ret["aliasDomain"] +" Success")

    def domain_delete(self, parser):
        bae_app_conf = self._get_cur_bae_conf(parser)

        if not bae_app_conf:
            g_messager.error("Bae app not set or not exists in local cache")
            sys.exit(-1)

        data = {}
        data["domain"] = parser.domain
        data["appid"]   = bae_app_conf.model.appid

        ret = self.rest.post(API_ENTRY + "/api/bae/app/domainunbind", data = data)

        g_messager.trace("Del domain alias" + ret["aliasDomain"] +" Success")

    def instance_list(self, parser,flag=True):
        data = {}
        bae_app_conf  = self._get_cur_bae_conf(parser)

        if not bae_app_conf:
            g_messager.warning("Please use set baeappid or at least cd to a bae app directory")
            sys.exit(-1)

        data["appid"] = bae_app_conf.model.appid

        ret = self.rest.post(API_ENTRY + "/api/bae/app/catInsList", data = data)

        instances = [BaeInstance(ins).tuple() for ins in ret]
        print instance_table("Instance List", instances)

    def instance_restart(self, parser):
        data = {}
        bae_app_conf = self._get_cur_bae_conf(parser)

        if not bae_app_conf:
                g_messager.warning("Please use set baeappid or at least cd to a bae app directory")
                sys.exit(-1)

        if not parser.local:
            data["appid"] = bae_app_conf.model.appid
            data["fid"]   = parser.insids
            ret = self.rest.post(API_ENTRY + "/api/bae/package/restartIns", data = data)

            g_messager.trace("Restart success")
        else:
            if bae_app_conf.model.lang_type == 'java':
                cmd = "bae_run %s start"%bae_app_conf.model.solution
            else:
                cmd = "bae_run %s start"%bae_app_conf.model.lang_type
            os.system(cmd)

    def instance_start(self, parser):
        data = {}
        bae_app_conf = self._get_cur_bae_conf(parser)

        if not bae_app_conf:
                g_messager.warning("Please use set baeappid or at least cd to a bae app directory")
                sys.exit(-1)
        if not parser.local:
            g_messager.trace("start your online server. Comming soon...")
        else:
            if bae_app_conf.model.lang_type == 'java':
                cmd = "bae_run %s start"%bae_app_conf.model.solution
            else:
                cmd = "bae_run %s start"%bae_app_conf.model.lang_type
            os.system(cmd)

    def instance_stop(self, parser): 
        data = {}
        bae_app_conf = self._get_cur_bae_conf(parser)

        if not bae_app_conf:
            g_messager.warning("Please use set baeappid or at least cd to a bae app directory")
            sys.exit(-1)
        if not parser.local:
            g_messager.trace("start your online server. Comming soon...")
        else:
            if bae_app_conf.model.lang_type == 'java':
                cmd = "bae_run %s stop"%bae_app_conf.model.solution
            else:
                cmd = "bae_run %s stop"%bae_app_conf.model.lang_type
            os.system(cmd)

    def log_list(self, parser):
        
        data  = {}
        bae_app_conf = self._get_cur_bae_conf(parser)

        if not bae_app_conf:
            g_messager.error("Can't found your bae app or not set bae appid")
            sys.exit(-1)
        fid = parser.instanceid  
        if not fid:
            self.instance_list(parser,flag=False) 
            fid = g_messager.input("pleae input the instance id : ")

        data["appid"] = bae_app_conf.model.appid
        data["fid"]       = str(fid)
        data["logType"]  = "local"

        ret = self.rest.post(API_ENTRY + "/api/bae/farsee/log/filelist", data = data)
        
        if 0 == len(ret["type"]):
            g_messager.warning("no log file in container now")
        else:
            g_messager.output("log file names in container(%d) :" %(len(ret["type"])))
            g_messager.output("\n".join([ value["name"] for value in ret["type"]]))
            g_messager.warning("You can check the detail messages of every file by using the command  bae log tail/ bae log head ")
        
    def log_tail(self, parser):
        self._query_log(parser, "tail")

    def log_head(self, parser):
        self._query_log(parser, "head")

    def _query_log(self, parser, method):
        data ={}
        bae_app_conf = self._get_cur_bae_conf(parser)
        fid = parser.instanceid  
        if not bae_app_conf:
            g_messager.error("Can't found your bae app or not set bae appid")
            sys.exit(-1)
        if not fid:
            self.instance_list(parser,flag=False) 
            fid = g_messager.input("pleae input the instance id : ")  
        filename=parser.file
        if not filename:
            filename = g_messager.input("pleae input the filename you want to check : ") 

        data["appid"] = bae_app_conf.model.appid
        data["fid"]       = str(fid)
        data["filename"]  = filename
        data["limit"]     = str(parser.max or 50)
        data["logType"]  = "local"

        ret = self.rest.post(API_ENTRY + "/api/bae/farsee/log/%s" %(method), data = data)

        if 0 == len(ret):
            g_messager.warning("no log in %s now" %(parser.file))
        else:
            g_messager.output("\n".join(ret))

    def _get_app_id(self, parser):
        appid        = None

        if parser.appid:
            appid = parser.appid
        else:
            return None
        '''
        elif self.appconfig and self.appconfig.model.app_id:
            appid = self.appconfig.model.app_id
            '''
        return appid


    def _get_cur_bae_conf(self, parser):
        baeappid = None
        conf     = None
        if self.appconfig and self.appconfig.cur_bae_app:
            baeappid = self.appconfig.cur_bae_app.model.appid
            conf     = self.appconfig.cur_bae_app
            if parser.force:
                conf = self._app_cat_bae(conf.model.appid)
        
        if parser.baeappid:
            baeappid = parser.baeappid
            try:
                conf     = self._app_cat_bae(baeappid)
            except BaeRestError as e:
                #try get conf from localdir
                if self.appconfig.bae_app_configs:
                    for bae_app_conf in self.appconfig.bae_app_configs:
                        if os.path.basename(bae_app_conf.dirname()) == parser.baeappid:
                            return bae_app_conf
                raise e
        if not conf:
            return None

        return conf

    def _get_bae_confs(self, parser):
        confs = []
        if parser.baeappids:
            if parser.force:
                    confs = self._app_cat_bae(parser.baeappids)
            elif self.appconfig:
                 confs = [conf for conf in self.appconfig.bae_app_configs if conf.model.appid in parser.baeappids]
        else:
            if self.appconfig:
                if self.appconfig.cur_bae_app:
                    confs = self._app_cat_bae([self.appconfig.cur_bae_app.model.appid])
                else:
                    if parser.force:
                        confs =  self._app_cat()
                        self.appconfig.bae_app_configs = confs
                        self.appconfig.save()
                    else:
                        confs = self.appconfig.bae_app_configs

        return confs
               
    def _app_cat_bae(self, bae_appids):
        if not bae_appids:
            return []
        if not isinstance(bae_appids, list):
            bae_appids = [bae_appids]
            issingle   = True
        else:
            issingle   = False

        data = {}

        data["appids"] = json.dumps(bae_appids)
        ret = self.rest.post(API_ENTRY + "/api/bae/app/catCodeBatch", data = data)
        bae_app_configs = []

        for bae_app_conf in ret["appinfo"]:
            new_bae_app = BaeApp(bae_app_conf)
            g_messager.trace("Loading config for {0}".format(new_bae_app.name))
            if self.appconfig:
                app_dir    = self.appconfig.appdir()
                local_dir  = os.path.join(app_dir, new_bae_app.name)
                local_conf = os.path.join(local_dir, BAE_APP_CONFIG) 
                bae_config = BaeAppConfig(local_conf)

                if not os.path.exists(local_dir):
                    import distutils
                    import distutils.dir_util
                    distutils.dir_util.mkpath(local_dir)
                elif not os.path.isdir(local_dir):
                    g_messager.error(local_dir + "exists and it's not a dir")
                    sys.exit(-1)
            else:
                bae_config = BaeAppConfig()
            bae_config.model = new_bae_app       
            bae_app_configs.append(bae_config)

        if issingle:
            return bae_app_configs[0]
        else:
            return bae_app_configs

    def _app_setup_bae(self, bae_app_conf):
        bae_app = bae_app_conf.model

        g_messager.trace("begin setup {0}".format(bae_app.appid))
        try:
            tool = code_tool.get_tool(bae_app.versionType, bae_app.reposUrl, bae_app_conf.dirname())
            tool.pull()
        except NotImplementError, e:
            g_messager.bug("Bae App {0} Tool not supported".format(str(bae_app)))

    def _app_cat(self):
        data = {}
        data["status"]   = "all"
        data["limit"]    = "10000"
        data["start"]    = "0"
        ret = self.rest.post(API_ENTRY + "/api/bae/app/list", data = data)

        bae_app_ids = [bae_app_conf["appid"] for bae_app_conf in ret]
        bae_app_conf_list = self._app_cat_bae(bae_app_ids)
        
        return bae_app_conf_list

    def _gen_request_id(self):
        import uuid
        return uuid.uuid4()

    
    def _format_operation_log(self, log_json):
        END     = 0
        ERROR   = 1
        WARNING = 2
        TRACE   = 3

        try:
            import json
            log = json.loads(log_json)

	    tm =  log["timestamp"]
            date  = time.strftime("%T", time.localtime(tm))
            logfmt = "{0} : {1}".format(date, log["log"])

            if log["status"] == 3:
                g_messager.trace(logfmt)
            elif log["status"] == 2:
                g_messager.warning(logfmt)
            elif log["status"] == 1:
                raise BaeCliError(logfmt)
            else:
                g_messager.success(logfmt)
                return True
        except KeyError:
            pass

        return False

    def _get_operation_log(self, requestid):
        TIMEOUT = 60
        start   = int(time.time())
        log_end = False
        data     = {}
        data["requestid"] = requestid.__str__()
        
        while True:
            ret = self.rest.post(API_ENTRY + "/api/bae/app/clilog", data, timeout = 10 )

            for log in ret["logs"]:
                log_end =  self._format_operation_log(log)
                
            now = int(time.time())
            if log_end :
                break
            if now - start >= TIMEOUT:
                raise BaeCliError("get Server infomation error")
            else:
                time.sleep(1)
