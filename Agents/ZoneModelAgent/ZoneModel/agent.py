import sys
import time
import logging

from volttron.platform.agent import BaseAgent, PublishMixin
from volttron.platform.agent import utils, matching
from volttron.platform.messaging import headers as headers_mod
from volttron.platform.messaging import topics
import settings

utils.setup_logging()
_log = logging.getLogger(__name__)

# Zone Model Agent will act as a virtual class -> not designed to withhold information 
class ZoneModelAgent(PublishMixin, BaseAgent):
    
    def __init__(self,**kwargs):
        super(ZoneModelAgent,self).__init__(**kwargs)
        self.agent_id = 'ZoneModel'
        print(time.ctime())
        
    def setup(self):
        super(ZoneModelAgent,self).setup()
              
    @matching.match_start('heartbeat/listeneragent')
    def on_heartbeat_topic(self, topic, headers, message, match):        
        print "Zone Model Agent got\nTopic: {topic}, {headers}, Message: {message}".format(topic=topic,headers=headers, message=message)
                
    # Retrieve weather data
    @matching.match_exact('weather/response/temperature/temp_f')   
    def on_weather(self, topic, headers, message, match):
        print "Weather Agent temperature: {message} time: {time}".format(message=message,time = time.ctime())
        temp = float("".join(message))
        self.update_ModelParm(temp)
    
    # Send new weather data to model    
    def update_ModelParm(self,temp):
        return
            
    # Pushes a schedule request message to the Actuator Agent
    def publish_schedule(self):
        headers = { 'AgentID': self._agent_id,
                    'type': 'NEW_SCHEDULE',
                    'requesterID': self._agent_id + "-TASK",
                    'priority': 'LOW',}
        
        msg = [["Zone1/VAV1",
                "2015-1-31 12:27:00", #Start of Time
                "2015-7-8 12:43:00"], #End of Time
               ["Zone1/VAV2",
                "2015-1-31 12:27:00",
                "2015-7-8 12:43:00"]
               ]
        self.publish_json(topics.ACTUATOR_SCHEDULE_REQUEST,headers,msg)
 
    # Listen to actuator results and schedule announcements
    @matching.match_start(topics.ACTUATOR_SCHEDULE_RESULT)
    def on_schedule_result(self, topic, headers, message, match):
        print "Zone Model Agent schedule result \nTopic: {topic}, {headers}, Message: {message}".format(topic=topic,headers=headers, message=message)
         
def main(argv=sys.argv):
    '''Main method called by the eggsecutable.'''
    utils.default_main(ZoneModelAgent,
                   description='Zone Model Agent',
                   argv=argv)


if __name__ == '__main__':
    # Entry point for script
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
    