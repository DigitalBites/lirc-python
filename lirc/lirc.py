import sys
import subprocess


class Lirc(object):
    """Parses the lircd.conf file and can send remote commands through irsend.
    """
    codes = {}

    def __init__(self, conf="/etc/lirc/lircd.conf"):
        self._parse(conf)

    def _parse(self, conf):
        """Parse the lircd.conf config file and create a dictionary.
        """
        remote_name = None
        code_section = False

        # Open the config file
        with open(conf, 'rb') as fp:
            for line in fp:
                # Convert tabs to spaces
                l = line.replace('\t',' ')

                # Look for a 'begin remote' line
                if l.strip()=='begin remote':
                    # Got the start of a remote definition
                    remote_name = None
                    code_section = False

                elif not remote_name and l.strip().find('name')>-1:
                    # Got the name of the remote
                    remote_name = l.strip().split(' ')[-1]
                    if remote_name not in self.codes:
                        self.codes[remote_name] = {}

                elif remote_name and l.strip()=='end remote':
                    # Got to the end of a remote definition
                    remote_name = None

                elif remote_name and l.strip()=='begin codes':
                    code_section = True

                elif remote_name and l.strip()=='end codes':
                    code_section = False

                elif remote_name and code_section:
                    # Got a code key/value pair... probably
                    fields = l.strip().split(' ')
                    self.codes[remote_name][fields[0]] = fields[-1]

    def has_device(self, device_id):
    	"""Check if a device exists in the configuration"""
    	return self.codes.has_key(device_id)
    
    def has_device_bttn(self, device_id, btn):
    	"""Check to see if a given device exists AND has the button defined"""
    	return self.codes.has_key(device_id) and self.codes.get(device_id).has_key(btn)

    def get_devices(self):
        """Return a list of devices."""
        return self.codes.keys()
        
    def get_device_bttns(self, device_id):
    	"""Get the list of buttons defined for a given device"""
    	if self.has_device(device_id):
    		return self.codes.get(device_id).keys()
    	else:
    		return
    
    def send_once(self, device_id, message):
    	"""Send single call to IR LED."""
    	cmd_output = ""
    	
    	print "Lirc::send_once : irsend command: ",['irsend', 'SEND_ONCE', device_id, message]
    	
    	try:
    		cmd_output = subprocess.check_output(['irsend', 'SEND_ONCE', device_id, message], stderr=subprocess.STDOUT)
    		print "Lirc::send_once : CMD_OK: ",cmd_output
    	except subprocess.CalledProcessError as e:
    		print "Lirc::send_once : CPE_ERR:", e.returncode, e.output
    	except OSError as e:
    		print "Lirc::send_once : OS_ERR", e.errno, e.strerror
		    
    def send_once_old(self, device_id, message):
        """Send single call to IR LED... With ZERO error checking."""
        subprocess.call(['irsend', 'SEND_ONCE', device_id, message])


if __name__ == "__main__":
    lirc = Lirc()
