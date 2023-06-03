from mininet.net import Mininet
from mininet.node import OVSController
from topo_16_star import center_star
import sys

input_cmd = ""
if len(sys.argv) > 2:
	input_1 = sys.argv[1]
	input_2 = sys.argv[2]
	input_cmd = "%s %s" % (input_1, input_2)
	print("Using inputs %s" % input_cmd)

network_topo = center_star()
net = Mininet(topo=network_topo, controller = OVSController)
net.start()

server_port = 9999

h00 = net.hosts[0]
servers = net.hosts[1:]

print("Testing connections...")
for host in servers:
	print(host)
	print(host.cmd('ping -c1 %s' % h00.IP()))

print("Starting servers")
for server in servers:
	command = 'python -u ../src/abft_server.py %s %s' % (server.IP(), server_port) 
	log_cmd = '> output/%s.log 2>&1 &'% (server)
	command = command + " " + log_cmd
	print("Starting server %s : %s" % (server, command))
	server.cmd(command)

print("Starting client process...")
command = 'python ../src/multi_driver.py %s' % (input_cmd)
log_cmd = '> output/client_%s.log' % (h00)
command = command + " " + log_cmd
print(command)
print(h00.cmd(command))
print("Processing finished!")

print("Cleaning up")
print("Done!")
net.stop()
