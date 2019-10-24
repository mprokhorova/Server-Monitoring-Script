import socket, time, json, datetime, platform, psutil, requests, pprint, uuid
from jira import JIRA



def main():
    # Hostname Info
    hostname = socket.gethostname()
    print("Hostname:", hostname)

    # CPU Info
    cpu_count = psutil.cpu_count()
    cpu_usage = psutil.cpu_percent(interval=1)
    print("CPU:\n\tCount:", cpu_count, "\n\tUsage:", cpu_usage)

    # Memory Info
    memory_stats = psutil.virtual_memory()
    memory_total = memory_stats.total
    memory_used = memory_stats.used
    memory_used_percent = memory_stats.percent
    print("Memory:\n\tPercent:", memory_used_percent, "\n\tTotal:", memory_total / 1e+6, "MB", "\n\tUsed:", memory_used / 1e+6, "MB")

    # Disk Info
    disk_info = psutil.disk_partitions()
    print("Disks:")
    disks = []
    for x in disk_info:
        # Try fixes issues with connected 'disk' such as CD-ROMS, Phones, etc.
        try:
            disk = {
                "name" : x.device, 
                "mount_point" : x.mountpoint, 
                "type" : x.fstype, 
                "total_size" : psutil.disk_usage(x.mountpoint).total, 
                "used_size" : psutil.disk_usage(x.mountpoint).used, 
                "percent_used" : psutil.disk_usage(x.mountpoint).percent
            }

            disks.append(disk)

            print("\tDisk name",disk["name"], "\tMount Point:", disk["mount_point"], "\tType",disk["type"], "\tSize:", disk["total_size"] / 1e+9,"\tUsage:", disk["used_size"] / 1e+9, "\tPercent Used:", disk["percent_used"])
        except:
            print("")

    # Bandwidth Info 
    network_stats = get_bandwidth()
    print("Network:\n\tTraffic in:",network_stats["traffic_in"] / 1e+6,"\n\tTraffic out:",network_stats["traffic_out"] / 1e+6)

    # Network Info
    nics = []
    print("NICs:")
    for name, snic_array in psutil.net_if_addrs().items():
        # Create NIC object
        nic = {
            "name": name,
            "mac": "",
            "address": "",
            "address6": "",
            "netmask": ""
        }
        # Get NiC values
        for snic in snic_array:
            if snic.family == -1:
                nic["mac"] = snic.address
            elif snic.family == 2:
                nic["address"] = snic.address
                nic["netmask"] = snic.netmask
            elif snic.family == 23:
                nic["address6"] = snic.address
        nics.append(nic)
        print("\tNIC:",nic["name"], "\tMAC:", nic["mac"], "\tIPv4 Address:",nic["address"], "\tIPv4 Subnet:", nic["netmask"], "\tIPv6 Address:", nic["address6"])
    
    # Platform Info
    system = {
        "name" : platform.system(),
        "version" : platform.release()
    }
    print("OS:\n\t",system["name"],system["version"])

    # Time Info
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S+00:00")
    uptime = int(time.time() - psutil.boot_time())
    print("System Uptime:\n\t",uptime)

    # System UUID
    sys_uuid = uuid.getnode()
	
    # Set Machine Info
    machine = {
    	"hostname" : hostname,
		"uuid" : sys_uuid,
        "system" : system,
        "uptime" : uptime,
    	"cpu_count" : cpu_count,
    	"cpu_usage" : cpu_usage,
    	"memory_total" : memory_total,
    	"memory_used" : memory_used,
    	"memory_used_percent" : memory_used_percent,
    	"drives" : disks,
    	"network_up" : network_stats["traffic_out"],
    	"network_down" : network_stats["traffic_in"],
        "network_cards": nics,
        "timestamp" : timestamp
    }

    data = json.dumps(machine)
    print("\nData:")
    pprint.pprint(machine, indent=4)

    send_data(machine)
	

def get_bandwidth():
    # Get net in/out
    net1_out = psutil.net_io_counters().bytes_sent
    net1_in = psutil.net_io_counters().bytes_recv

    time.sleep(1)

    # Get new net in/out
    net2_out = psutil.net_io_counters().bytes_sent
    net2_in = psutil.net_io_counters().bytes_recv

    # Compare and get current speed
    if net1_in > net2_in:
        current_in = 0
    else:
        current_in = net2_in - net1_in
    
    if net1_out > net2_out:
        current_out = 0
    else:
        current_out = net2_out - net1_out
    
    network = {"traffic_in" : current_in, "traffic_out" : current_out}
    return network

def send_data(machine):
    # Attempt to send data up to 30 times
	for attempt in range(1):
		try:
		
			#Jira comment posting
			#jira = JIRA()
			
			#options = {'server': 'https://jira.accelrys.com','verify':False}
			#jira = JIRA(options)
			
			jira_options = {
				'server': 'https://jira.accelrys.com',
				'verify': False,
				'cert': 'C:\Python27\jiraaccelryscom.pem'
				}
			#jira = JIRA(basic_auth=('MPA2', '19QAZ08wsx'))
			jira = JIRA(options=jira_options, basic_auth=('MPA2', '19QAZ08wsx'))
			
			#jac = JIRA('https://jira.accelrys.com')
			#auth_jira = JIRA(auth=('MPA2', '19QAZ08wsx'))
			
			Issue_number = 'DS7429-122';
			
			issue = jira.issue(Issue_number, fields='comment')
			
			drives = machine.get("drives")
			
					
			comment_body = ('||ServerName||Check Parameter Name||Result value|' + '\n' +
							'|' + machine.get("hostname") + '|cpu_usage|' + str(machine.get("cpu_usage")) + '|' + '\n' +
							'|' + machine.get("hostname") + '|memory_used_percent|' + str(machine.get("memory_used_percent")) + '|' + '\n' +
							'|' + machine.get("hostname") + '|drives.name|' + str(drives[0].get("name")) + '\n'  + 
							'|' + machine.get("hostname") + '|drives.percent_used|' + str(drives[0].get("percent_used")) + '|' + '\n' + 
							'|' + machine.get("hostname") + '|drives.name|' + str(drives[1].get("name"))  + '\n'  + 
							'|' + machine.get("hostname") + '|drives.percent_used|' + str(drives[1].get("percent_used")) + '|' + '\n' +
							'|' + machine.get("hostname") + '|drives.name|' + str(drives[2].get("name"))  + '\n'  + 
							'|' + machine.get("hostname") + '|drives.percent_used|' + str(drives[2].get("percent_used")) + '|' + '\n' )
			
			comment = jira.add_comment(Issue_number, comment_body)
			
 
		except OSError as err:
			print("OS error: {0}".format(err))

            # Sleep 1 minute before retrying
			#time.sleep(60)
	else:
        # If no connection established for half an hour, kill script
		exit(0)
while True:
    main()
    print("-----------------------------------------------------------------")
    time.sleep(3)