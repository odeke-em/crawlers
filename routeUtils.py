#!/usr/bin/env python3
import re

from resty import restDriver
from routing import RouterManager

ipPortRegCompile = re.compile('(.+):([^:]+)$', re.UNICODE)
class Router:
    def __init__(self, addrList, hashBase=10):
        self.__addrList = addrList
        self.__addrToDriverMap = {}
        self.initAddrMapping(addrList, hashBase)

    def initAddrMapping(self, addrList, hashBase=10):
        self.__routeManager = RouterManager.RouterManager(hashBase=hashBase, serverAddrList=addrList)

        routeMapList = self.__routeManager.getRoutingAddresses()
        
        for addr in routeMapList: 
            # Build WorkerManagers
            ipPortSearch = ipPortRegCompile.search(addr)
            if ipPortSearch:
                target = ipPortSearch.groups(1)
                wD = WorkerDriver(*target)
                self.__addrToDriverMap[addr] = wD

    def getWorkerDriver(self, item):
        associatedAddr = self.__routeManager.getRoute(item.__hash__())
        return self.__addrToDriverMap.get(associatedAddr, None)

class WorkerDriver:
    def __init__(self, ip, port):
        self.__workerId = -1
        self.getDefaultAuthor = restDriver.getDefaultAuthor 
        print('ip', ip, 'port', port)
        self.initMainRestDriver(ip, port)

        self.initWorker()
        self.initRouting()

    def initMainRestDriver(self, ip, port):
        self.restDriver = restDriver.RestDriver(ip, port)
        wHandler = self.restDriver.registerLiason('Worker', '/jobTable/workerHandler')
        assert(wHandler)

        jHandler = self.restDriver.registerLiason('Job', '/jobTable/jobHandler')
        assert(jHandler)

        rHandler = self.restDriver.registerLiason('Route', '/jobTable/routeHandler')
        assert(rHandler)

    def initRouting(self):
        rResponse = restDriver.produceAndParse(
            self.restDriver.getRoutes, address=self.restDriver.getBaseUrl()
        )
        if rResponse.get('status_code', 400) == 200 and rResponse.get('data', None):
            print('Already registered', self.restDriver.getBaseUrl())
        else:
            cResponse = restDriver.produceAndParse(
                self.restDriver.newRoute, address=self.restDriver.getBaseUrl()
            )
            print(cResponse)

        # Let's now get the list of all present routes
        routeManifest = restDriver.produceAndParse(
            self.restDriver.getRoutes, select='address'
        )
        if routeManifest.get('status_code', 400) == 200:
            data = routeManifest.get('data', None) or [] 
            
            addrList = []
            for item in data:
                addr = item.get('address', None)
                if addr:
                    addrList.append(addr)

            # print('addrList', addrList)
            
    def getWorkerId(self):
        return self.__workerId

    def initWorker(self):
        qResponse = restDriver.produceAndParse(self.restDriver.getWorkers, purpose='Crawling', select='id', format='short')
        if qResponse.get('data', None):
            print('Present workers', qResponse)
            self.__workerId = qResponse['data'][0].get('id', -1)
        else:
            cResponse = restDriver.produceAndParse(self.restDriver.newWorker, purpose='Crawling')
            print('Created worker response', cResponse)
            self.__workerId = cResponse.get('data', [{'id', -1}]).get('id', -1)

        print('WorkerId', self.__workerId)

def main():
    pass

if __name__ == '__main__':
    main()
