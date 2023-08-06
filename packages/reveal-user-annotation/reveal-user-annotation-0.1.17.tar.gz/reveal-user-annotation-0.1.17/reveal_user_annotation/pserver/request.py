__author__ = 'Georgios Rizos (georgerizos@iti.gr)'

import requests

from reveal_user_annotation.pserver.pserver_util import get_configuration_details


# def write_topics_to_pserver(config, user_topics_gen):
#     for user, topics in user_topics_gen:




def get_user_list(config):

    #http://idefix.iit.demokritos.gr:1111/pers?clnt=wp2_journalist%7Cwp2_5%21&com=getusrs&whr=*

    request = "pers?clnt=wp2_journalist%7Cwp2_5%21&com=getusrs&whr=*"

    request = '%s%s' % (config.pserver_host(), request)
    r = requests.get(request, auth=config.admin_panel_auth())
    print(r.text)


def construct_request(config, command, values):
    """
    Construct the request url as a string
    """
    base_request = ('{model_type}?'
                    'clnt={client_name}%7C{client_pass}%21&'
                    'com={command}&{values}'.format(model_type="pers",
                                                    client_name=config["CLIENT_NAME"],
                                                    client_pass=config["CLIENT_PASS"],
                                                    command=command,
                                                    values=values))
    return base_request


def send_request(config, request):
    request = '%s%s' % (config["PSERVER_HOST"], request)
    print(request)
    try:
        result = requests.get(request)
        if result.status_code == 200:
            print('[SUCCESS]: Request %s was successful!\n', request)
            return result
        else:
            print('Respond from Pserver: %s', result)
            raise Exception
    except Exception as e:
        print('Error while sending requests to Pserver!! %s')
        print(e)


def initialize_model(config):
    init_feats = '&'.join(['%s=0' % ["user_type", "user_topic"]])
    features_req = construct_request(config,
                                     'addftr',
                                     init_feats)
    send_request(config,
                 features_req)


def clear_model(config):
    feature_to_be_removed = "&".join(["ftr=%s" ["user_type", "user_topic"]])
    features_req = construct_request(config,
                                     'remftr',
                                     feature_to_be_removed)
    send_request(config,
                 features_req)

c = get_configuration_details()
print(initialize_model(c))


    #
    # def initialize_model(self, ):
    #     """
    #     Send the initial requests to Pserver in order to build the
    #     User profile model (contains: attributes and features)
    #     """
    #     query = ('{client_name}|{client_pass}'.format(
    #                                             client_name=config.CLIENT_NAME,
    #                                             client_pass=config.CLIENT_PASS))
    #     request = ('%s/1.0/personal/%s/users.json') % (config.PSERVER_HOST, query)
    #     print 'INITIAL REQUEST'
    #     #logging.info('Initializing Pserver User Profiles....\n')
    #     result = requests.get(request)
    #     result = result.json()
    #     #print type(result['result'])
    #     #logging.info('Initializing Pserver User Profiles....\n')
    #
    #     feats = [('%s.%s' % (config.CAMPAIGN_NAME, f)) for f in config.FEATURES]
    #     print feats
    #
    #     if type(result['result']) is dict:
    #         print '[INFO]: Already there!'
    #         return
    #     else:
    #
    #         #logging.info('Initializing Pserver User Profiles....\n')
    #         #Users - Initial Model
    #         #set init value for each attribute: attr=null
    #         print 'Initializeing PServer User Profiles...\n'
    #         init_attr = '&'.join(['%s=null' % value for value in config.ATTRIBUTES])
    #         attributes_req = self.construct_request('addattr',
    #                                                 init_attr)
    #         #set init value for each feature
    #         init_feats = '&'.join(['%s=0' % value for value in feats])
    #         #print init_feats
    #         features_req = self.construct_request('addftr',
    #                                               init_feats)
    #         print features_req
    #         #self.logger.info('Sending initial requests to Pserver....')
    #         self.send_request(attributes_req)
    #         self.send_request(features_req)
    #

    #
    #
    # def insert_data(self, row):
    #     """
    #     Sends a request to pserver to insert the given data
    #     """
    #     values = []
    #     ptags = ['attr_%s' % attr for attr in config.ATTRIBUTES] + \
    #                            ['ftr_%s' % ftr for ftr in feats]
    #     if not (len(row) - 1) == len(config.PROFILE_TAGS):
    #         self.logger.error('Found error in the format of the given row. '
    #                           'Ignoring row: %s \n', row)
    #         return
    #     for index, tag in enumerate(config.PROFILE_TAGS):
    #         values.append('%s=%s' % (tag, row[index + 1]))
    #     joined_values = '&'.join(values)
    #     complete_values = 'usr=%s&%s' % (row[0], joined_values)
    #     self.send_request(self.construct_request('setusr', complete_values))
    #
    # def update_feature_value(self, data, feature):
    #     username = data[0]
    #     feature_value = '{0:.7f}'.format(data[1])
    #     joined_ftr_value = 'ftr_'+feature+'='+str(feature_value)
    #     complete_values = 'usr=%s&%s' % (username, joined_ftr_value)
    #     self.send_request(self.construct_request('setusr', complete_values))
