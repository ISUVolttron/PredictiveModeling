import sys, settings, time, logging, unicodedata, array, csv, threading

from volttron.platform.agent import BaseAgent, PublishMixin
from volttron.platform.agent import utils, matching
from volttron.platform.messaging import headers as headers_mod
from volttron.platform.messaging import topics
from agent import ZoneModelAgent

def arxModel(config_path, **kwargs):
    config = utils.load_config(config_path)
    
    def get_config(name):
            try:
                return kwargs.pop(name)
            except KeyError:
                return config.get(name, '')
            
    agent_id = get_config('agentid')
    a1 = get_config('arx_a1')
    a2 = get_config('arx_a2')
    a3 = get_config('arx_a3')
    b = get_config('arx_b')
    c = get_config('arx_c')
    d = get_config('arx_d')
    T1 = get_config('arx_T1')
    massFlowLoc = get_config('MassFlow_Zone1') 
    tempSatLoc = get_config('TempSat_Zone1')
    outputLoc = get_config('OutputLoc')
    timeInterval = get_config('arx_TimeInterval_sec')
    zoneTemps = []
    weatherTemps = [70]
    zoneTemps = [0,0,T1] 
    
    with open(massFlowLoc, 'rb') as f:
        reader = csv.reader(f)
        tempSAT = []
        for row in reader:
            tempSAT.append(float("".join(row)))
                                 
    with open(tempSatLoc, 'rb') as f:
        reader = csv.reader(f)
        massFlow = []
        for row in reader:
            massFlow.append(float("".join(row)))        
                 
    class arxModelAgent(ZoneModelAgent):
        
        def setup(self):
            super(arxModelAgent,self).setup()
            threading.Timer(timeInterval,self.predict_ZoneTemp).start() 
            self.predict_ZoneTemp()
            
        def update_ModelParm(self, temp):
            weatherTemps.append(temp)
            return 
        
        def request_Temp(self):
            headers = {}
            headers[headers_mod.REQUESTER_ID] = self.agent_id 
            msg = {"zipcode": "50014"}
            self.publish_json('weather/request', headers, msg)
            print "temperature requested"
        
        def predict_ZoneTemp(self):
            threading.Timer(timeInterval,self.predict_ZoneTemp).start() 
            i = len(weatherTemps)            
            curTemp = a1*zoneTemps[i+1] + a2*zoneTemps[i] + a3*zoneTemps[i-1] + b*weatherTemps[i-1] + c*massFlow[i+1]*(tempSAT[i+1]-zoneTemps[i+1]) + d
            zoneTemps.append(curTemp)
            print "arxModel Temperature {curTemp}".format(curTemp=curTemp)
            print(time.ctime())           
            self.request_Temp()
            
        def publish_Output(self):
            with open(outputLoc, "w") as output: 
                writer = csv.writer(output, lineterminator='\n')
                writer.writerows(zoneTemps)
            
             
    arxModelAgent.__name__ = 'Arx Model Agent'
    return arxModelAgent(**kwargs)
        
def main(argv=sys.argv):
    '''Main method called by the eggsecutable.'''
    utils.default_main(arxModel,
                   description='Arx Model Agent',
                   argv=argv)


if __name__ == '__main__':
    # Entry point for script
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
                