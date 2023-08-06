#!/usr/bin/env python3

#---------------------------------------------------------------
# FoLiA Document Server
#   by Maarten van Gompel
#   Centre for Language Studies
#   Radboud University Nijmegen
#   http://proycon.github.io/folia
#   http://github.com/proycon/foliadocserve
#   proycon AT anaproy DOT nl
#
# The FoLiA Document Server is a backend HTTP service to interact with
# documents in the FoLiA format, a rich XML-based format for linguistic
# annotation (http://proycon.github.io/folia). It provides an interface to
# efficiently edit FoLiA documents through the FoLiA Query Language (FQL).
#
#   Licensed under GPLv3
#
#----------------------------------------------------------------


from __future__ import print_function, unicode_literals, division, absolute_import
import cherrypy
import argparse
import time
import os
import json
import random
import datetime
import subprocess
import sys
import traceback
import threading
import queue
import gc
from copy import copy
from collections import defaultdict
from pynlpl.formats import folia, fql, cql
from foliadocserve.flat import parseresults, getflatargs
from foliadocserve.test import test

from jinja2 import Environment, FileSystemLoader
syspath = os.path.dirname(os.path.realpath(__file__))
env = Environment(loader=FileSystemLoader(syspath + '/templates'))

def fake_wait_for_occupied_port(host, port): return

class NoSuchDocument(Exception):
    pass


VERSION = "0.3.0"

logfile = None
def log(msg):
    global logfile
    if logfile:
        logfile.write(msg+"\n")
        logfile.flush()


def parsegitlog(data):
    commit = None
    date = None
    msg = None
    for line in data.split("\n"):
        line = line.strip()
        if line[0:6] == 'commit':
            #yield previous
            if commit and date and msg:
                yield commit, date, msg
            commit = line[7:]
            msg = None
            date = None
        elif line[0:7] == 'Author:':
            pass
        elif line[0:5] == 'Date:':
            date = line[6:].strip()
        elif line:
            msg = line
    if commit and date and msg:
        yield commit, date, msg




class BackgroundTaskQueue(cherrypy.process.plugins.SimplePlugin):
    """For background tasks that need not tie-up the request process"""

    thread = None
    def __init__(self, bus, qsize=100, qwait=2, safe_stop=True):
        cherrypy.process.plugins.SimplePlugin.__init__(self, bus)
        self.q = queue.Queue(qsize)
        self.qwait = qwait
        self.safe_stop = safe_stop

    def start(self):
        self.running = True
        if not self.thread:
            self.thread = threading.Thread(target=self.run)
            self.thread.start()

    def stop(self):
        if self.safe_stop:
            self.running = "draining"
        else:
            self.running = False

        if self.thread:
            self.thread.join()
            self.thread = None
        self.running = False

    def run(self):
        while self.running:
            try:
                try:
                    func, args, kwargs = self.q.get(block=True, timeout=self.qwait)
                except queue.Empty:
                    if self.running == "draining":
                        return
                    continue
                else:
                    func(*args, **kwargs)
                    if hasattr(self.q, 'task_done'):
                        self.q.task_done()
            except:
                self.bus.log("Error in BackgroundTaskQueue %r." % self, level=40, traceback=True)

    def put(self, func, *args, **kwargs):
        """Schedule the given func to be run."""
        self.q.put((func, args, kwargs))

class AutoUnloader(cherrypy.process.plugins.SimplePlugin):
    """Calls docstore.autounload() every tick"""

    thread = None
    def __init__(self, bus, docstore, interval=60):
        self.docstore = docstore
        self.interval = interval
        self.safe_stop = True
        cherrypy.process.plugins.SimplePlugin.__init__(self, bus)

    def start(self):
        self.running = True
        if not self.thread:
            self.thread = threading.Thread(target=self.run)
            self.thread.start()

    def stop(self):
        if self.safe_stop:
            self.running = "draining"
        else:
            self.running = False

        if self.thread:
            self.thread.join()
            self.thread = None
        self.running = False

    def run(self):
        while self.running:
            print("tick, ", len(self.docstore),file=sys.stderr)
            self.docstore.autounload()
            time.sleep(self.interval)


class DocStore:
    def __init__(self, workdir, expiretime, git=False):
        log("Initialising document store in " + workdir)
        self.workdir = workdir
        self.expiretime = expiretime
        self.data = {}
        self.updateq = defaultdict(lambda: defaultdict(set)) #update queue, (namespace,docid) => session_id => set(folia element id), for concurrency
        self.lastaccess = defaultdict(dict) # (namespace,docid) => session_id => time
        self.changelog = defaultdict(list) # (namespace,docid) => [changemessage]

        self.lock = set() #will contain (namespace,docid) of temporarily locked documents, loading/unloading/saving are blocking operations
        self.setdefinitions = {}
        self.git = git
        super().__init__()

    def getfilename(self, key):
        assert isinstance(key, tuple) and len(key) == 2
        if key[0] == "testflat":
            return syspath + '/testflat.folia.xml'
        else:
            return self.workdir + '/' + key[0] + '/' + key[1] + '.folia.xml'

    def getpath(self, key):
        assert isinstance(key, tuple) and len(key) == 2
        return self.workdir + '/' + key[0]


    def use(self, key):
        while key in self.lock:
            time.sleep(0.1)
        self.lock.add(key)

    def done(self, key):
        self.lock.remove(key)


    def load(self,key, forcereload=False):
        if key[0] == "testflat": key = ("testflat", "testflat")
        self.use(key)
        filename = self.getfilename(key)
        if not key in self or forcereload:
            if not os.path.exists(filename):
                log("File not found: " + filename)
                self.done(key)
                raise NoSuchDocument
            log("Loading " + filename)
            try:
                self.data[key] = folia.Document(file=filename, setdefinitions=self.setdefinitions, loadsetdefinitions=True)
                self.data[key].changed = False
            except Exception as e:
                log("Error reading file " + filename + ": " + str(e))
                self.done(key)
                raise
            self.lastaccess[key]['NOSID'] = time.time()
        self.done(key)
        return self.data[key]



    def save(self, key, message = ""):
        doc = self[key]
        if key[0] == "testflat":
            #No need to save the document, instead we run our tests:
            log("Running test " + key[1])
            return test(doc, key[1])
        elif doc.changed:
            self.use(key)
            log("Saving " + self.getfilename(key) + " - " + message)
            doc.save()
            if self.git:
                if os.path.exists(self.workdir + '/.git'):
                    # entire workdir is one git repo (old style)
                    dir = self.workdir
                    os.chdir(self.workdir)
                else:
                    dir = self.getpath(key)
                    os.chdir(dir)
                    if not os.path.exists(dir + '/.git'):
                        log("Initialising git repository in  " + dir)
                        r = os.system("git init")
                        if r != 0:
                            log("ERROR during git init of " + dir)
                            self.done(key)
                            return
                message = "\n".join(self.changelog[key]) + "\n" + message
                self.changelog[key] = [] #reset changelog
                message = message.strip("\n")
                log("Doing git commit for " + self.getfilename(key) + " -- " + message.replace("\n", " -- "))
                r = os.system("git add " + self.getfilename(key) + " && git commit -m \"" + message.replace('"','') + "\"")
                if r != 0:
                    log("ERROR during git add/commit of " + self.getfilename(key))
                self.done(key)


    def unload(self, key, save=True):
        if key in self:
            if save:
                self.save(key)
            self.use(key) #save set its own lock
            log("Unloading " + "/".join(key))
            del self.data[key]
            del self.lastaccess[key]
            if key in self.changelog:
                del self.changelog[key]
            self.done(key)

    def __getitem__(self, key):
        assert isinstance(key, tuple) and len(key) == 2
        if key[0] == "testflat":
            key = ("testflat","testflat")
        self.load(key)
        return self.data[key]

    def __setitem__(self, key, doc):
        assert isinstance(key, tuple) and len(key) == 2
        assert isinstance(doc, folia.Document)
        doc.filename = self.getfilename(key)
        self.data[key] = doc

    def __contains__(self,key):
        assert isinstance(key, tuple) and len(key) == 2
        return key in self.data


    def __len__(self):
        return len(self.data)

    def keys(self):
        return self.data.keys()

    def items(self):
        return self.data.items()

    def values(self):
        return self.data.values()

    def __iter__(self):
        return iter(self.data)

    def autounload(self, save=True):
        unload = []
        for d in self.lastaccess:
            for sid, t in self.lastaccess[d].items():
                if time.time() - t > self.expiretime:
                    unload.append(d)

        for key in unload:
            self.unload(key, save)


def validatenamespace(namespace):
    return namespace.replace('..','').replace('"','').replace(' ','_').replace(';','').replace('&','').strip('/')

def getdocumentselector(query):
    if query.startswith("USE "):
        end = query[4:].index(' ') + 4
        if end >= 0:
            try:
                namespace,docid = query[4:end].rsplit("/",1)
            except:
                raise fql.SyntaxError("USE statement takes namespace/docid pair")
            return (validatenamespace(namespace),docid), query[end+1:]
        else:
            try:
                namespace,docid = query[4:end].rsplit("/",1)
            except:
                raise fql.SyntaxError("USE statement takes namespace/docid pair")
            return (validatenamespace(namespace),docid), ""
    return None, query






class Root:
    def __init__(self,docstore,bgtask,args):
        self.docstore = docstore
        self.bgtask = bgtask
        self.workdir = args.workdir
        self.debug = args.debug

    def createsession(self,namespace,docid, sid=None, results=None):
        """Create or update a session"""
        if sid[-5:] != 'NOSID':
            log("Creating session " + sid + " for " + "/".join((namespace,docid)))
            self.docstore.lastaccess[(namespace,docid)][sid] = time.time()
            self.docstore.updateq[(namespace,docid)][sid] #will create it if it does not exist yet, does nothing otherwise, other sessions will write here what we need to update
            for othersid in self.docstore.updateq[(namespace,docid)]:
                if othersid != sid:
                    for result in results:
                        if result.id:
                            self.docstore.updateq[(namespace,docid)][othersid].add(result.id)

    def addtochangelog(self, doc, query, docselector):
        if self.docstore.git:
            if query.action and query.action.action != "SELECT":
                if query.action.focus and query.action.focus.Class:
                    changemsg = query.action.action.lower() + " on " + query.actions.focus.Class.XMLTAG
                    if query.action.assignments and query.action.assignments['annotator']:
                        changemsg += " by " + query.action.assignments['annotator']
                    self.docstore.changelog[docselector].append(changemsg)

    @cherrypy.expose
    def createnamespace(self, *namespaceargs):
        namespace = validatenamespace('/'.join(namespaceargs))
        if not os.path.exists(self.workdir + '/' + namespace):
            try:
                os.makedirs(self.workdir + '/' + namespace)
            except:
                raise cherrypy.HTTPError(403, "Unable to create namespace: " + namespace)
        cherrypy.response.headers['Content-Type']= 'text/plain'
        return "ok"




    @cherrypy.expose
    def query(self, **kwargs):
        """Query method, all FQL queries arrive here"""

        if 'X-sessionid' in cherrypy.request.headers:
            sid = cherrypy.request.headers['X-sessionid']
        else:
            sid = 'NOSID'

        if 'query' in kwargs:
            rawqueries = kwargs['query'].split("\n")
        else:
            cl = cherrypy.request.headers['Content-Length']
            rawqueries = cherrypy.request.body.read(int(cl)).split("\n")

        #Get parameters for FLAT-specific return format
        flatargs = getflatargs(cherrypy.request.params)

        prevdocsel = None
        sessiondocsel = None
        queries = []
        for rawquery in rawqueries:
            try:
                docsel, rawquery = getdocumentselector(rawquery)
                if not docsel: docsel = prevdocsel
                self.docstore.use(docsel)
                if not sessiondocsel: sessiondocsel = docsel
                if rawquery == "GET":
                    query = "GET"
                elif rawquery == "PROBE":
                    query = "PROBE" #gets no content data at all, but allows returning associated metadata used by FLAT, forces FLAT format
                else:
                    if rawquery[:4] == "CQL ":
                        if rawquery.find('FORMAT') != -1:
                            end = rawquery.find('FORMAT')
                            format = rawquery[end+7:]
                        else:
                            end = 9999
                            format = 'xml'
                        try:
                            query = fql.Query(cql.cql2fql(rawquery[4:end]))
                            query.format = format
                        except cql.SyntaxError as e :
                            raise fql.SyntaxError("Error in CQL query: " + str(e))
                    else:
                        query = fql.Query(rawquery)
                    if query.format == "python":
                        query.format = "xml"
                    if query.action and not docsel:
                        raise fql.SyntaxError("Document Server requires USE statement prior to FQL query")
            except fql.SyntaxError as e:
                log("[QUERY ON " + "/".join(docsel)  + "] " + str(rawquery))
                log("[QUERY FAILED] FQL Syntax Error: " + str(e))
                raise cherrypy.HTTPError(404, "FQL syntax error: " + str(e))
            finally:
                self.docstore.done(docsel)

            queries.append( (query, rawquery))
            prevdocsel = docsel

        results = []
        doc = None
        prevdocid = None
        multidoc = False #are the queries over multiple distinct documents?
        for query, rawquery in queries:
            try:
                doc = self.docstore[docsel]
                self.docstore.lastaccess[docsel][sid] = time.time()
                log("[QUERY ON " + "/".join(docsel)  + "] " + str(rawquery))
                if isinstance(query, fql.Query):
                    if prevdocid and doc.id != prevdocid:
                        multidoc = True
                    result =  query(doc,False,self.debug >= 2)
                    results.append(result) #False = nowrap
                    if self.debug:
                        log("[QUERY RESULT] " + result)
                    format = query.format
                    if query.action and query.action.action != "SELECT":
                        doc.changed = True
                        self.addtochangelog(doc, query, docsel)
                elif query == "GET":
                    results.append(doc.xmlstring())
                    format = "single-xml"
                elif query == "PROBE":
                    #no queries to perform
                    format = "flat"
                else:
                    raise Exception("Invalid query")
            except NoSuchDocument:
                log("[QUERY FAILED] No such document")
                raise cherrypy.HTTPError(404, "Document not found: " + docsel[0] + "/" + docsel[1])
            except fql.QueryError as e:
                log("[QUERY FAILED] FQL Query Error: " + str(e))
                raise cherrypy.HTTPError(404, "FQL query error: " + str(e))
            except Exception as e:
                log("[QUERY FAILED] FoLiA Error: " + str(e))
                raise cherrypy.HTTPError(404, "FoLiA error: " + str(e))
            prevdocid = doc.id

        if not format:
            raise cherrypy.HTTPError(404, "No queries given")
        if format.endswith('xml'):
            cherrypy.response.headers['Content-Type']= 'text/xml'
        elif format.endswith('json'):
            cherrypy.response.headers['Content-Type']= 'application/json'


        if format == "xml":
            out = "<results>" + "\n".join(results) + "</results>"
        elif format == "json":
            out = "[" + ",".join(results) + "]"
        elif format == "flat":
            if sid != 'NOSID' and sessiondocsel and not multidoc:
                self.createsession(sessiondocsel[0],sessiondocsel[1],sid, results)
            cherrypy.response.headers['Content-Type']= 'application/json'
            if multidoc:
                raise "{} //multidoc response, not producing results"
            elif doc:
                out =  parseresults(results, doc, **flatargs)
        else:
            if len(results) > 1:
                raise cherrypy.HTTPError(404, "Multiple results were obtained but format dictates only one can be returned!")
            out = results[0]


        if docsel[0] == "testflat":
            testresult = self.docstore.save(docsel) #won't save, will run tests instead
            log("Test result: " +str(repr(testresult)))


            if format == "flat":
                out = json.loads(str(out,'utf-8'))
                out['testresult'] = testresult[0]
                out['testmessage'] = testresult[1]
                out['queries'] = rawqueries
                out = json.dumps(out)

            #unload the document, we want a fresh copy every time
            del self.docstore.data[('testflat','testflat')]

        if self.debug:
            log("[FINAL RESULTS] " + out)

        if isinstance(out,str):
            return out.encode('utf-8')
        else:
            return out


    @cherrypy.expose
    def index(self):
        template = env.get_template('index.html')
        return template.render(VERSION=VERSION)


    @cherrypy.expose
    def getdochistory(self, *args):
        namespace, docid = self.docselector(*args)
        log("Returning history for document " + "/".join((namespace,docid)))
        cherrypy.response.headers['Content-Type'] = 'application/json'
        if not os.path.exists(self.docstore.getfilename((namespace,docid))):
            raise cherrypy.HTTPError(404, "Document not found")
        if self.docstore.git:
            log("Invoking git log " + namespace+"/"+docid + ".folia.xml")
            if os.path.exists(self.workdir + '/.git'):
                dir = self.workdir
            else:
               dir = self.docstore.getpath((namespace,doc))
            os.chdir(dir)
            proc = subprocess.Popen("git log " + docid + ".folia.xml", stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True,cwd=dir)
            outs, errs = proc.communicate()
            if errs: log("git log errors? " + errs.decode('utf-8'))
            d = {'history':[]}
            count = 0
            for commit, date, msg in parsegitlog(outs.decode('utf-8')):
                count += 1
                d['history'].append( {'commit': commit, 'date': date, 'msg':msg})
            if count == 0: log("git log output: " + outs.decode('utf-8'))
            log(str(count) + " revisions found - " + errs.decode('utf-8'))
            return json.dumps(d).encode('utf-8')
        else:
            return json.dumps({'history': []}).encode('utf-8')

    @cherrypy.expose
    def save(self, *args, message=""):
        namespace, docid = self.docselector(*args)
        if (namespace,docid) in self.docstore:
            self.bgtask.put( self.docstore.save, (namespace,docid), message)
            return "scheduling save"
        else:
            return "nothing to save"


    @cherrypy.expose
    def revert(self, *args, commithash=None):
        if not commithash:
            raise cherrypy.HTTPError(400, "Expected commithash")

        if not all([ x.isalnum() for x in commithash ]):
            return b"{}"

        cherrypy.response.headers['Content-Type'] = 'application/json'
        if self.docstore.git:
            if (namespace,docid) in self.docstore:
                os.chdir(self.workdir)
                #unload document (will even still save it if not done yet, cause we need a clean workdir)
                key = (namespace,docid)
                self.docstore.unload(key)

            log("Doing git revert for " + self.docstore.getfilename(key) )
            os.chdir(self.workdir)
            r = os.system("git checkout " + commithash + " " + self.docstore.getfilename(key) + " && git commit -m \"Reverting to commit " + commithash + "\"")
            if r != 0:
                log("Error during git revert of " + self.docstore.getfilename(key))
            return b"{}"
        else:
            return b"{}"



    def checkexpireconcurrency(self):
        #Delete concurrency information for sessions that fail to poll within the expiration time (they almost certainly closed the page/browser)
        deletelist = []
        for d in self.docstore.lastaccess:
            for sid in self.docstore.updateq[d]:
                if sid in self.docstore.lastaccess[d]:
                    lastaccess = self.docstore.lastaccess[d][sid]
                    if time.time() - lastaccess > self.docstore.expiretime:
                        deletelist.append( (d,sid) )
        for d,sid in deletelist:
            if sid != 'NOSID':
                log("Expiring session " + sid + " for " + "/".join(d))
                del self.docstore.lastaccess[d][sid]
                del self.docstore.updateq[d][sid]
                if len(self.docstore.lastaccess[d]) == 0:
                    del self.docstore.lastaccess[d]
                if len(self.docstore.updateq[d]) == 0:
                    del self.docstore.updateq[d]


    def docselector(self, *args):
        try:
            docid = args[-1]
            namespace = validatenamespace('/'.join(args[:-1]))
            if not namespace or not docid:
                raise
        except:
            raise cherrypy.HTTPError(404, "Expected namespace/docid")
        docid = docid.replace('/','').replace('..','').replace(';','').replace('&','').replace(' ','_')
        return namespace, docid



    @cherrypy.expose
    def poll(self, *args):
        namespace, docid = self.docselector(*args)

        if 'X-sessionid' in cherrypy.request.headers:
            sid = cherrypy.request.headers['X-sessionid']
        else:
            raise cherrypy.HTTPError(404, "Expected X-sessionid" + docselector[0] + "/" + docselector[1])

        if namespace == "testflat":
            return "{}" #no polling for testflat

        self.checkexpireconcurrency()

        if sid in self.docstore.updateq[(namespace,docid)]:
            ids = self.docstore.updateq[(namespace,docid)][sid]
            self.docstore.updateq[(namespace,docid)][sid] = set() #reset
            if ids:
                cherrypy.log("Succesful poll from session " + sid + " for " + "/".join((namespace,docid)) + ", returning IDs: " + " ".join(ids))
                doc = self.docstore[(namespace,docid)]
                results = [ doc[id] for id in ids if id in doc ]
                return parseresults(results, doc, **{'sid':sid, 'lastaccess': self.docstore.lastaccess[(namespace,docid)]})
            else:
                return json.dumps({'sessions': len([s for s in self.docstore.lastaccess[(namespace,docid)] if s != 'NOSID' ])}).encode('utf-8')
        else:
            return json.dumps({'sessions': len([s for s in self.docstore.lastaccess[(namespace,docid)] if s != 'NOSID' ])}).encode('utf-8')



    @cherrypy.expose
    def namespaces(self, *namespaceargs):
        namespace = validatenamespace('/'.join(namespaceargs))
        try:
            namespaces = [ x for x in os.listdir(os.path.join(self.docstore.workdir,namespace)) if x != "testflat" and x[0] != "." and os.path.isdir(os.path.join(self.docstore.workdir,namespace,x)) ]
        except FileNotFoundError:
            raise cherrypy.HTTPError(404, "Namespace not found: " + str(namespace))
        return json.dumps({
                'namespaces': namespaces
        })

    @cherrypy.expose
    def documents(self, *namespaceargs):
        namespace = validatenamespace('/'.join(namespaceargs))
        try:
            docs = [ x for x in os.listdir(self.docstore.workdir + "/" + namespace) if x[-10:] == ".folia.xml" ]
        except FileNotFoundError:
            raise cherrypy.HTTPError(404, "Namespace not found: " + str(namespace))
        return json.dumps({
                'documents': docs,
                'timestamp': { x:os.path.getmtime(self.docstore.workdir + "/" + namespace + "/"+ x) for x in docs  },
                'filesize': { x:os.path.getsize(self.docstore.workdir + "/" + namespace + "/"+ x) for x in docs  }
        })


    @cherrypy.expose
    def upload(self, *namespaceargs):
        namespace = validatenamespace('/'.join(namespaceargs))
        log("In upload, namespace=" + namespace)
        response = {}
        cl = cherrypy.request.headers['Content-Length']
        data = cherrypy.request.body.read(int(cl))
        cherrypy.response.headers['Content-Type'] = 'application/json'
        #data =cherrypy.request.params['data']
        try:
            log("Loading document from upload")
            doc = folia.Document(string=data,setdefinitions=self.docstore.setdefinitions, loadsetdefinitions=True)
            response['docid'] = doc.id
            self.docstore[(namespace,doc.id)] = doc
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            formatted_lines = traceback.format_exc().splitlines()
            traceback.print_tb(exc_traceback, limit=50, file=sys.stderr)
            response['error'] = "Uploaded file is no valid FoLiA Document: " + str(e) + " -- " "\n".join(formatted_lines)
            log(response['error'])
            return json.dumps(response).encode('utf-8')

        filename = self.docstore.getfilename( (namespace, doc.id))
        i = 1
        while os.path.exists(filename):
            filename = self.docstore.getfilename( (namespace, doc.id + "." + str(i)))
            i += 1
        self.docstore.save((namespace,doc.id), "Initial upload")
        return json.dumps(response).encode('utf-8')



def main():
    global logfile
    parser = argparse.ArgumentParser(description="", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-d','--workdir', type=str,help="Work directory", action='store',required=True)
    parser.add_argument('-p','--port', type=int,help="Port", action='store',default=8080,required=False)
    parser.add_argument('-l','--logfile', type=str,help="Log file", action='store',default="foliadocserve.log",required=False)
    parser.add_argument('-D','--debug', type=int,help="Debug level", action='store',default=0,required=False)
    parser.add_argument('--git',help="Enable versioning control using git (separate git repositories will be automatically created for each namespace, OR you can make one global one in the workdir manually)", action='store_true',default=False)
    parser.add_argument('--expirationtime', type=int,help="Expiration time in seconds, documents will be unloaded from memory after this period of inactivity", action='store',default=900,required=False)
    parser.add_argument('--interval', type=int,help="Interval at which the unloader checks documents (in seconds)", action='store',default=60,required=False)
    parser.add_argument('--host',type=str,help="Host/IP to listen for (defaults to all interfaces)", action='store',default="0.0.0.0")
    args = parser.parse_args()
    logfile = open(args.logfile,'w',encoding='utf-8')
    os.chdir(args.workdir)
    cherrypy.config.update({
        'server.socket_host': args.host,
        'server.socket_port': args.port,
        'request.show_tracebacks':False,
    })
    cherrypy.process.servers.wait_for_occupied_port = fake_wait_for_occupied_port
    docstore = DocStore(args.workdir, args.expirationtime, args.git)
    bgtask = BackgroundTaskQueue(cherrypy.engine)
    bgtask.subscribe()
    autounloader = AutoUnloader(cherrypy.engine, docstore, args.interval)
    autounloader.subscribe()
    cherrypy.quickstart(Root(docstore,bgtask,args))

if __name__ == '__main__':
    main()
