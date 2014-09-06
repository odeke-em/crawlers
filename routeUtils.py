#!/usr/bin/env python3
import re
import random

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
        baseUrl = self.restDriver.getBaseUrl()
        rResponse = self.restDriver.getRoutes(address=baseUrl)
        value = rResponse.get('value', {})
        if rResponse.get('status_code', 400) == 200 and value.get('data', None):
            print('Already registered', baseUrl)
        else:
            cResponse = self.restDriver.newRoute(
                address=self.restDriver.getBaseUrl()
            )
            print('After logging the route', cResponse)

        # Let's now get the list of all present routes
        routeManifest = self.restDriver.getRoutes(select='address')
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
        workerCheck = self.restDriver.getWorkers(
            purpose='Crawling', select='id', format='short'
        ).get('value', {})

        if workerCheck.get('data', None):
            workersPresent = workerCheck['data']
            randWorkerId = random.sample(workersPresent, 1)[0].get('id', -1)
            self.__workerId = randWorkerId
            print('Present workers: {wp} randPickedWorker: {rw}'.format(
                wp=workersPresent, rw=randWorkerId)
            )
        else:
            nwResp = self.restDriver.newWorker(purpose='Crawling').get('value', {})
            print('nwResp', nwResp)
            self.__workerId = nwResp.get('data', {'id': -1}).get('id', -1)

        print('Initialized WorkerId: ', self.__workerId)

def main():
    pass

if __name__ == '__main__':
    main()
