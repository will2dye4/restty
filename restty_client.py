import json
from urllib import urlencode
from urllib2 import urlopen


class ResttyClient:
    DEFAULT_PROMPT = '> '
    PROMPT_COMMAND = '$prompt'
    QUIT_COMMAND = '$quit'

    def __init__(self, hostname='localhost', port=5000):
        self.hostname = hostname
        self.port = port
        self.command = ''
        self.return_code = None
        self.prompt = ResttyClient.DEFAULT_PROMPT

    def __repr__(self):
        return 'ResttyClient(hostname=%r,port=%r)' % (self.hostname, self.port)

    def _execute(self):
        url = 'http://%s:%d/exec?%s' % (self.hostname, self.port, urlencode({'c': self.command}))
        response = urlopen(url)
        return json.loads(response.read()) if response.getcode() == 200 else None

    def _handle_command(self):
        if self.command == '$?':
            if self.return_code is not None:
                print self.return_code
            else:
                print 'Error: no return code available'
        elif self.command.startswith(ResttyClient.PROMPT_COMMAND):
            prompt = self.command[self.command.find(ResttyClient.PROMPT_COMMAND)+8:]
            if not prompt:
                prompt = ResttyClient.DEFAULT_PROMPT
            if not prompt.endswith(' '):
                prompt += ' '
            self.prompt = prompt
        elif self.command != '':
            response = self._execute()
            if response is not None:
                self.return_code = response['status']
                print response['result'].rstrip('\n')
            else:
                print 'Error: failed to make request'

    def run(self):
        print 'Enter "%s" to exit' % ResttyClient.QUIT_COMMAND
        while self.command != ResttyClient.QUIT_COMMAND:
            self._handle_command()
            self.command = raw_input(self.prompt)
        print 'Client exiting'


if __name__ == '__main__':
    ResttyClient().run()
