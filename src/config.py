from configparser import ConfigParser


class Config:
    '''
    Sample Usage:

    >>> from config import Config
    >>> c = Config('config.cfg')
    >>> c.get_data()
    {'token': '#the token name here', 'botname': 'servidora', 'bug_report_id': '#telegram id of the person that will get the bug reports', 'master_telegram_id': '#the telegram id of the person who provisions the vms'}

    '''
    def __init__(self, name_of_config_file: str):
        self.name_of_config_file = name_of_config_file

    def get_data(self):
        parser = ConfigParser()
        parser.read(self.name_of_config_file)
        return {
            'token': parser.get('creds', 'token'),
            'botname': parser.get('creds', 'botname'),
            'bug_report_id': parser.get('creds', 'bug_report_id'),
            'master_telegram_id': parser.get('master', 'master_telegram_id')
        }