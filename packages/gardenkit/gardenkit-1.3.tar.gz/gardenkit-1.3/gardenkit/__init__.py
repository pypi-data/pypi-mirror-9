# $Id: gardenkit.py 2015-01-08 $
# Author: Golan Derazon <golan@greeniq.co>
# Copyright: GreenIQ LTD

import urllib,json
from urllib import request
from xml.etree import ElementTree as ET

'''




'''

GREENIQ_DOMAIN = 'greeniq.net'
PROTOCOL = 'https'

def get_version():
    '''
    Returns GardenKit API version
    '''
    return '1.3'

def extract_json(data):
    try:
        res = json.loads(data.decode())
    except Exception as e:
        raise GardenKitException('%s - %s' %(str(e),data))
    if not res['status'] == True:
        raise GardenKitException('Unexpected results %s' % data)
    return res.get('data')


class GardenKit(object):
    
        
    def __init__(self,username,password,client_id=None,client_secret=None,domain=GREENIQ_DOMAIN,protocol = PROTOCOL):
        '''
        Constructs GardenKit Api instance
        
        Args:
                
        '''
        self.domain = domain
        self.protocol = protocol
        self.username = username
        self.password = password
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
    
    
    def login(self):
        '''
        Authenticates provided credentials and fetches token.
        
        Note:
        API methods can be used only after successfull login.
        
        '''
        if self.client_id and self.client_secret:
            return self.__oauth_login()
        else:
            return self.__simple_login()
    
    def __oauth_login(self):
        '''
        oAuth2 based login
        '''
        data= {'grant_type':'password',
               'client_id':self.client_id,
               'client_secret':self.client_secret,
               'username':self.username,
               'password':self.password}
        res = self.__process_request('', 
                                     request_type='POST',
                                     data= data,
                                     validation=None,
                                     full_url='%(PROTOCOL)s://%(DOMAIN)s/oauth2/access_token' % {'PROTOCOL':self.protocol,'DOMAIN':self.domain})[1]
                                     
        self.access_token= json.loads(res.decode()).get('access_token')
    
    def __simple_login(self):
        '''
        Simple api login with 
        
        '''
        res = self.__process_request('signin', request_type='POST',data= {'username':self.username,'password':self.password},validation=None,api_path='/')[1]
        res = json.loads(res.decode())
        if res['status'] != 'GreenIQFTPLoginSuccess':
            raise GardenKitException(res['status'])
        self.access_token= res['hiddenhash']
    
    def set_valves_configuration(self,master,ports):
        '''
        Sets irrigation valves configuration
        
        Args:
        
        Returns:
        
        Raises:
        
        Examples:
        
        '''
        self.__assert_access_token()
        valves_state = {}
        valves_state['master'] = master
        valves_state['ports'] = ports
        post_data = {'access_token':self.access_token,'data':json.dumps(valves_state)}
        self.__process_request('set_valves_config', request_type='POST',data= post_data)

    def get_valves_configuration_and_status(self):
        '''
        
        
        Args:
        
        Returns:
        
        Raises:
        
        Examples:
        
        '''
        self.__assert_access_token()
        res = self.__process_request('get_valves_state_and_config', request_type='GET',data= {'access_token':self.access_token})
        return res


    def set_light_configuration(self,master,ports):
        '''
        
        
        Args:
        
        Returns:
        
        Raises:
        
        Examples:
        
        '''
        self.__assert_access_token()
        valves_state = {}
        valves_state['master'] = master
        valves_state['ports'] = ports
        post_data = {'access_token':self.access_token,'data':json.dumps(valves_state)}
        self.__process_request('set_light_config', request_type='POST',data= post_data)

    def get_light_configuration_and_status(self):
        '''
        
        
        Args:
        
        Returns:
        
        Raises:
        
        Examples:
        
        '''
        self.__assert_access_token()
        res = self.__process_request('get_light_state_and_config', request_type='GET',data= {'access_token':self.access_token})
        return res

    def get_hub_status(self):
        '''
                
        Args:
        
        Returns:
        
        Raises:
        
        Examples:
        
        '''
        self.__assert_access_token()
        data= {'access_token':self.access_token}
        res = self.__process_request('get_hub_status', request_type='GET',data=data)
        return res

    def update_program(self,port_index,program_index,enable,weather=None,starttime=None,endtime=None,days ={},interval={}):
        '''
        
        
        Args:
        
        Returns:
        
        Raises:
        
        Examples:
        
        '''

        self.__assert_access_token()
        if port_index > 6 or port_index < 1:
            raise GardenKitException('Irrigation port index should be between 1-6')
        if program_index > 4 or program_index < 1:
            raise GardenKitException('Program index should be between 1-4')

        configxml = self.get_config()
        try:
            the_dom = ET.fromstring(configxml)
        except Exception as e:
            raise GardenKitException('Internal error, got an invalid configuration from HUB ') from e
        
        program_selector = './port/attributes/[number="%(port_index)d"]/../program/[number="%(program_index)d"]/' % {'port_index':port_index,'program_index':program_index}
        the_dom.find(program_selector+'enable').text = str(enable)
        
        if weather != None:
            the_dom.find(program_selector+'weather_dependancy').text = str(weather)
        if starttime != None:
            the_dom.find(program_selector+'schedule/on/time').text = starttime.strftime('%H:%M')
        if endtime != None:
            the_dom.find(program_selector+'schedule/off/time').text = endtime.strftime('%H:%M')
        
        if days:
            week_days = list(the_dom.find(program_selector+'schedule/weekdays').text)
            for day in days:
                week_days[(day+1)% 7] = days[day] and '1' or '0'
            the_dom.find(program_selector+'schedule/weekdays').text = ''.join(week_days)
        
        if interval:
            every_x_days = interval['every_x_days'] 
            start_date = interval.get('starting')
            the_dom.find(program_selector+'schedule/cycle_period/starting/year').text = str(start_date.year)
            the_dom.find(program_selector+'schedule/cycle_period/starting/month').text = str(start_date.month)
            the_dom.find(program_selector+'schedule/cycle_period/starting/day').text = str(start_date.day)
            the_dom.find(program_selector+'schedule/cycle_period/every_x_days').text = str(every_x_days)
            
        configxml = ET.tostring(the_dom)
        return self.set_config(configxml.decode())
        
    def get_config(self):
        '''
        
        
        Args:
        
        Returns:
        
        Raises:
        
        Examples:
        
        '''        
        self.__assert_access_token()
        data= {'access_token':self.access_token}
        res = self.__process_request('get_config', request_type='GET',data=data)
        return res

    def set_config(self,configxml):
        '''
        
        
        Args:
        
        Returns:
        
        Raises:
        
        Examples:
        
        '''

        self.__assert_access_token()
        try:
            ET.fromstring(configxml)
        except Exception as e:
            raise GardenKitException('Illegal config mxl structure ') from e
                
        data= {'access_token':self.access_token,'data':json.dumps(configxml)}
        res = self.__process_request('set_config', request_type='POST',data= data)        
        return res
                
    def __assert_access_token(self):
        if not self.access_token:
            raise (GardenKitException('Please login before activating API'))
    
    #################################################################################
    #
    #
    #
    #################################################################################
    def __process_request(self,api_call,request_type='GET',data = {},validation=extract_json,api_path='/api/',full_url = None):
        if full_url:
            url = full_url
        else:
            url =  '%s://%s/php%s%s.php' %(self.protocol,self.domain,api_path,api_call)
        
        if data:
            data = urllib.parse.urlencode(data)
        if request_type == 'GET':
            if data:
                url+='?%s'%data
            post_data = None
        else:
            post_data = data
        if post_data != None:
            post_data = post_data.encode()
        req = request.Request(url, post_data)
        response =  request.urlopen(req)
        res = response,response.read(),response.info()
        response.close()
        if not validation:
            return res
        return validation(res[1])

class GardenKitException(Exception):
    pass
