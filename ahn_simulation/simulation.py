import tkinter as tk
import time
import threading
import random
import math
import json

# ROUTING TABLE
# < dest_id ; dest_seq_num ; next_hop ; num_hops ; expiration_time >
#    key         0         ;    1     ;    2     ;    3            >

# RREQ
# < last_hop ; src_id ; src_seq_num ; broadcast_id ; dest_id ; dest_seq_num ; hop_cnt >
# <    1     ;    2   ;    3        ;    4         ;    5    ;    6         ;    7    >
# RREP
# < last_hop ; src_id ; dest_id ; dest_seq_num ; hop_cnt >
# <    1     ;    2   ;    3    ;    4         ;    5    >
# PACKET
# < src_id ; dest_id ; message >
# <    1   ;    2    ;    3    >

# AODVLM - AODV Low Mobility
class AODVLMNode(object):
    def __init__(self, simulation_canvas, width, cor_x, cor_y, node_config):
        super().__init__()
        self.simulation_canvas = simulation_canvas

        self.width = width
        self.cor_x = cor_x
        self.cor_y = cor_y

        self.node_id = node_config[0]
        self.tx_range = node_config[1]
        self.tx_probability = node_config[2]
        self.seq_num = random.randint(0,100)
        self.broadcast_id = 0
#        self.expiration_time_route = node_config[3]
        self.long_expiration_time = node_config[3]
        self.diameter_expiration_time = 40



        self.routing_table = dict()
#        self.last_rrequests = dict() # fixme is this list replaceable by a lookup in routing table?
#        self.last_rreplies = dict() # fixme is this list replaceable by a lookup in routing table?
        self.route_request_memory = []
        self.rrequest_sent = False

        self.draw_entity(self.cor_x,cor_y)

        self.tx_buffer = []
        self.rx_buffer = []

    def draw_entity(self,cor_x,cor_y):
        self.entity = self.simulation_canvas.canvas.create_oval(cor_x-self.width/2,cor_y-self.width/2,cor_x+self.width/2,cor_y+self.width/2)
        self.entity_text = self.simulation_canvas.canvas.create_text(cor_x,cor_y,text=str(self.node_id))
        self.draw_vrt()
        if self.node_id == 0:
            for i in range(5):
                self.simulation_canvas.canvas.create_oval(cor_x-(i*self.tx_range),cor_y-(i*self.tx_range),cor_x+(i*self.tx_range),cor_y+(i*self.tx_range))

    def get_vrt_text(self):
        out = "{},#{},n,h,et\n".format(self.node_id,self.seq_num)
        table_entries = "\n".join(sorted(["{}:{}".format(k,self.routing_table[k]) for k in self.routing_table.keys() if self.routing_table[k][2] < 255]))
#        table_entries = "\n".join(sorted(["{}:{}".format(k,self.routing_table[k]) for k in self.routing_table.keys()]))

        out += table_entries
        return out

    # vrt = visual routing table
    def draw_vrt(self):
        self.routing_table_text = self.simulation_canvas.canvas.create_text(self.cor_x,self.cor_y+(self.width/2)+2,anchor=tk.N, text=self.get_vrt_text())

    def refresh_vrt(self):
        self.simulation_canvas.canvas.itemconfigure(self.routing_table_text,text=self.get_vrt_text())


    def get_distance(self, posxy):
        x,y = posxy
        return math.hypot(self.cor_x-x,self.cor_y-y)

    # a greater than function which accounts for 2byte overflow integer
    def gt_16(self, num1, num2):
        if num1 > num2:
            if not num1 > num2+32768:
                return True
        return False

    def inc_16(self, num):
        return (num+1)%65536

    def inc_8(self, num):
        return (num+1)%256

    def decrease_expiration_time_route_request_memory(self):
        to_remove = []
        for i in range(len(self.route_request_memory)):
            if self.route_request_memory[i][-1] > 0:
                self.route_request_memory[i][4] -= 1
            else: # rreq is stale -> rreq took longer than 2x diameter of network
                to_remove.append(i)
        for i in to_remove[::-1]:
            #####
            src_id,broadcast_id,dest_id,rrep_sent,expiration_time = self.route_request_memory.pop(i)
            print_str = "{} -> REMOVE RREQ-ENTRY src:{},bID:{},dest{}"
            print_str = print_str.format(self.node_id,src_id,broadcast_id,dest_id)
            self.simulation_canvas.simulation.output_add(print_str)
            print(print_str)




    def edit_routing_table(self, dest_id, dest_seq_num, next_hop, num_hops, long_expiration=False):
        if dest_id in self.routing_table.keys():
            #fixme - exp. time update is not right here??
#            self.reset_expiration_time(dest_id,long_expiration=False)

            # if routing_table entry is fresher, dont edit
            if self.gt_16(self.routing_table[dest_id][0], dest_seq_num):
                return False

            # if routing_table entry is equal, and its num_hops is
            # same or better, dont edit
            elif self.routing_table[dest_id][0] == dest_seq_num:
                if not self.gt_16(self.routing_table[dest_id][2], num_hops):
                    return False

        self.routing_table[dest_id] = [dest_seq_num, next_hop, num_hops, 0]
        self.reset_expiration_time(dest_id,long_expiration=False)
        self.refresh_vrt()
        return True

    def reset_expiration_time(self, nid, long_expiration=False):
        if nid in self.routing_table.keys():
            if not long_expiration:
                new_exp_time = 2*self.diameter_expiration_time
            else:
                new_exp_time = self.long_expiration_time
            new_exp_time = max(new_exp_time,self.routing_table[nid][3])
            self.routing_table[nid][3] = new_exp_time

    def send(self, message):
        self.simulation_canvas.medium_access(self,message)

    def is_RREQ(self, message):
        return message.startswith("RREQ")

    #automatically makes address check
    def is_RREP(self, message):
        if message.startswith("RREP"):
            addr = int(message.split(":")[1])
            if self.node_id == addr:
                return True
        return False

    def is_Packet(self, message):
        if message.startswith("Packet"):
            addr = int(message.split(":")[1])
            if self.node_id == addr:
                return True
        return False

    def is_duplicate_RREQ(self, src_id, broadcast_id):
#        if src_id in self.last_rrequests.keys():
#            if self.last_rrequests[src_id] == broadcast_id:
#                return True
##        print("not a duplicate RREQ: {}:{}, {}".format(src_id,broadcast_id,self.last_rrequests))
#        return False
        for mem_src_id,mem_broadcast_id,dest_id,rrep_sent,expiration_time in self.route_request_memory:
            if src_id == mem_src_id and broadcast_id == mem_broadcast_id:
                return True
        return False

#    def is_new_er_or_better_RREP(self, src_id, dest_id, dest_seq_num, hop_cnt):
#        if not src_id in self.last_rreplies.keys():
#            return True
#        else:
#            if dest_id in self.last_rreplies[src_id].keys():
#                last_dest_seq_num   = self.last_rreplies[src_id][dest_id][0]
#                last_hop_cnt        = self.last_rreplies[src_id][dest_id][1]
#
#                # newer if greater dest_seq_num
#                if self.gt_16(dest_seq_num,last_dest_seq_num):
#                    return True
#                # better if less hops with same dest_seq_num
#                elif dest_seq_num == last_dest_seq_num:
#                    if self.gt_16(last_hop_cnt,hop_cnt):
#                        return True
#        return False
    def is_first_RREP(self,src_id,dest_id):
        # first RREP Packet
        for mem_src_id,mem_broadcast_id,mem_dest_id,rrep_sent,expiration_time in self.route_request_memory:
            if src_id == mem_src_id and dest_id == mem_dest_id and rrep_sent == 0:
                return True
        return False

    def update_route_request_memory_entry(self,src_id,dest_id):
        for i in range(len(self.route_request_memory)):
            mem_src_id,mem_broadcast_id,mem_dest_id,rrep_sent,expiration_time = self.route_request_memory[i]
            if src_id == mem_src_id and dest_id == mem_dest_id:
                self.route_request_memory[i][3] = 1

    def unicast_RREP(self, src_id, dest_id):

        if dest_id == self.node_id:
            dest_seq_num = self.seq_num
            hop_cnt = 1

        else:
            dest_seq_num = self.routing_table[dest_id][0]
            hop_cnt = self.inc_8(self.routing_table[dest_id][2])

        next_hop = self.routing_table[src_id][1]

        packet = ["RREP"]
        packet.append(next_hop)
        packet.append(self.node_id)
        packet.append(src_id)
        packet.append(dest_id)
        packet.append(dest_seq_num)
        packet.append(hop_cnt)

        msg = ":".join([str(p) for p in packet])
        self.send(msg)

    def schedule_unicast_Packet(self, src_id, dest_id, payload, demand_new_route=False):

        self.tx_buffer.append([src_id,dest_id,payload])

        if not dest_id in self.routing_table.keys():
            self.broadcast_RREQ(src_id, 0, dest_id, 0)
        elif (not self.routing_table[dest_id][2] < 255) or demand_new_route:
            dest_seq_num = self.routing_table[dest_id][0]
            self.broadcast_RREQ(src_id, 0, dest_id, dest_seq_num)


    def unicast_Packet(self, src_id, dest_id, payload):

        if not dest_id in self.routing_table.keys():
            self.schedule_unicast_Packet(src_id, dest_id, payload)
            return
        if not self.routing_table[dest_id][2] < 255:
            self.schedule_unicast_Packet(src_id, dest_id, payload)
            return

        packet = ["Packet"]
        packet.append(self.routing_table[dest_id][1])
        packet.append(src_id)
        packet.append(dest_id)
        packet.append(payload)

        msg = ":".join([str(p) for p in packet])
        self.send(msg)

        self.reset_expiration_time(dest_id, long_expiration=True)


    def broadcast_RREQ(self, src_id, broadcast_id, dest_id, dest_seq_num):

        packet = ["RREQ"]
        packet.append(self.node_id)

        if src_id == self.node_id:
            self.seq_num = self.inc_16(self.seq_num)
            self.broadcast_id = self.inc_16(self.broadcast_id)
            self.refresh_vrt()

#            self.last_rrequests[self.node_id] = self.broadcast_id
#            self.last_rreplies = dict()
            self.route_request_memory.append([self.node_id,self.broadcast_id,dest_id,0,2*self.diameter_expiration_time])

            packet.append(self.node_id)
            packet.append(self.seq_num)
            packet.append(self.broadcast_id)
            packet.append(dest_id)
            packet.append(dest_seq_num)
            packet.append(1)

            # needed only for simulation?
            self.rrequest_sent = True

        else:
            packet.append(src_id)
            packet.append(self.routing_table[src_id][0])
            packet.append(broadcast_id)
            packet.append(dest_id)
            packet.append(dest_seq_num)
            packet.append(self.inc_16(self.routing_table[src_id][2]))

        msg = ":".join([str(p) for p in packet])
        self.send(msg)


    def process_received_message(self, message):

        if self.is_RREQ(message):


            src_id          = int(message.split(":")[2])
            broadcast_id    = int(message.split(":")[4])

            ## necessary after next if
            last_hop        = int(message.split(":")[1])
            src_seq_num     = int(message.split(":")[3])
            dest_id         = int(message.split(":")[5])
            dest_seq_num    = int(message.split(":")[6])
            hop_cnt         = int(message.split(":")[7])
            ## necessary after next if

            if self.is_duplicate_RREQ(src_id,broadcast_id):
                #####
                print_str = "RREQ: [{}#{} -> {}#{}], bID={}, {} -> {}, h={} DUPLICATE"
                print_str = print_str.format(src_id,src_seq_num,dest_id,dest_seq_num,broadcast_id,last_hop,self.node_id,hop_cnt)
                self.simulation_canvas.simulation.output_add(print_str)
                print(print_str)
                #####
                return


            #####
            print_str = "RREQ: [{}#{} -> {}#{}], bID={}, {} -> {}, h={}"
            print_str = print_str.format(src_id,src_seq_num,dest_id,dest_seq_num,broadcast_id,last_hop,self.node_id,hop_cnt)
            self.simulation_canvas.simulation.output_add(print_str)
            print(print_str)
            #####


#            self.last_rrequests[src_id] = broadcast_id
            self.route_request_memory.append([src_id,broadcast_id,dest_id,0,2*self.diameter_expiration_time])
            #####
            old_table_entry = "no entry"
            if src_id in self.routing_table.keys():
                old_table_entry = self.routing_table[src_id]
            #####
            routing_table_edited = self.edit_routing_table(src_id,src_seq_num,last_hop,hop_cnt)
            self.reset_expiration_time(src_id)
            #####
            print_str = "ADDED RREQ-Entry"
            if routing_table_edited:
                print_str += ", EDITED ROUTING_TABLE"
            self.simulation_canvas.simulation.output_add(print_str)
            print(print_str)
            new_table_entry = self.routing_table[src_id]
            print(old_table_entry, new_table_entry)
            #####

            if dest_id == self.node_id:
                if self.gt_16(dest_seq_num, self.seq_num):
                    self.seq_num = dest_seq_num
                self.unicast_RREP(src_id,self.node_id)
                #####
                print_str = "RREQ TARGET"
                self.simulation_canvas.simulation.output_add(print_str)
                print(print_str)
                #####
                return

            if dest_id in self.routing_table.keys():
                if self.routing_table[dest_id][2] < 255: #addme
                    # if the dest_seq_num of packet is not greater than routing table entry
                    if not self.gt_16(dest_seq_num, self.routing_table[dest_id][0]):
                        self.unicast_RREP(src_id,dest_id)
                        #####
                        print_str = "ANSWER RREQ with RREP"
                        self.simulation_canvas.simulation.output_add(print_str)
                        print(print_str)
                        #####
                        return

            self.broadcast_RREQ(src_id,broadcast_id,dest_id,dest_seq_num)

            #####
            print_str = "REBROADCAST RREQ"
            self.simulation_canvas.simulation.output_add(print_str)
            print(print_str)
            #####
            return

        if self.is_RREP(message):


            last_hop        = int(message.split(":")[2])
            src_id          = int(message.split(":")[3])
            dest_id         = int(message.split(":")[4])
            dest_seq_num    = int(message.split(":")[5])
            hop_cnt         = int(message.split(":")[6])

            #####
            print_str = "RREP: [{}#.. -> {}#{}], {} -> {}, h={}"
            print_str = print_str.format(src_id,dest_id,dest_seq_num,last_hop,self.node_id,hop_cnt)
            self.simulation_canvas.simulation.output_add(print_str)
            print(print_str)
            #####

            if self.is_first_RREP(src_id,dest_id):
                forward_rrep = True
                #####
                old_table_entry = "no entry"
                if dest_id in self.routing_table.keys():
                    old_table_entry = self.routing_table[dest_id]
                #####
                # use 2x diameter expiration time to allow worse entries from worse rrep to become stale
                self.edit_routing_table(dest_id,dest_seq_num,last_hop,hop_cnt)
                self.reset_expiration_time(dest_id)
#                self.remove_route_request_memory_entry(src_id,dest_id)
                self.update_route_request_memory_entry(src_id,dest_id)
                #####
                print_str = "UPDATED RREQ-ENTRY, EDITED ROUTING_TABLE"
                self.simulation_canvas.simulation.output_add(print_str)
                print(print_str)
                new_table_entry = self.routing_table[dest_id]
                print(old_table_entry, new_table_entry)
                #####
            else:
                #####
                old_table_entry = "no entry"
                if dest_id in self.routing_table.keys():
                    old_table_entry = self.routing_table[dest_id]
                #####
                # use 2x diameter expiration time to allow worse entries from worse rrep to become stale
                forward_rrep = self.edit_routing_table(dest_id,dest_seq_num,last_hop,hop_cnt)
                #####
                print_str = "DUPLICATE RREP"
                if forward_rrep:
                    self.reset_expiration_time(dest_id)
                    print_str += ", FRESHER OR BETTER ROUTE"
                self.simulation_canvas.simulation.output_add(print_str)
                print(print_str)
                new_table_entry = self.routing_table[dest_id]
                print(old_table_entry, new_table_entry)
                #####


            if src_id == self.node_id:
                self.rrequest_sent = False
                #####
                print_str = "RREQ INITIATOR"
                self.simulation_canvas.simulation.output_add(print_str)
                print(print_str)
                #####
                # do not forward rrep
                return

            if forward_rrep:
                self.unicast_RREP(src_id,dest_id)
                #####
                print_str = "FORWARD RREP"
                self.simulation_canvas.simulation.output_add(print_str)
                print(print_str)
                #####


#            if not self.is_new_er_or_better_RREP(src_id,dest_id,dest_seq_num,hop_cnt):
#                #####
#                print_str = "old and worse RREP"
#                self.simulation_canvas.simulation.output_add(print_str)
#                print(print_str)
#                #####
#                return
#
#
#            if not src_id in self.last_rreplies.keys():
#                self.last_rreplies[src_id] = dict()
#            self.last_rreplies[src_id][dest_id] = [dest_seq_num,hop_cnt]
#
#            #####
#            old_table_entry = "no entry"
#            if dest_id in self.routing_table.keys():
#                old_table_entry = self.routing_table[dest_id]
#            #####
#            self.edit_routing_table(dest_id,dest_seq_num,last_hop,hop_cnt,long_expiration=True)
#            #####
#            print_str = "ADDED LAST_RREP, EDITED ROUTING_TABLE"
#            self.simulation_canvas.simulation.output_add(print_str)
#            print(print_str)
#            new_table_entry = self.routing_table[dest_id]
#            print(old_table_entry, new_table_entry)
#            #####
#
#            if src_id == self.node_id:
#                self.rrequest_sent = False
#                #####
#                print_str = "RREQ INITIATOR"
#                self.simulation_canvas.simulation.output_add(print_str)
#                print(print_str)
#                #####
#                return
#
#            self.unicast_RREP(src_id,dest_id)
#
#            #####
#            print_str = "FORWARD RREP"
#            self.simulation_canvas.simulation.output_add(print_str)
#            print(print_str)
#            #####
#
#            return


        if self.is_Packet(message):

            src_id          = int(message.split(":")[2])
            dest_id         = int(message.split(":")[3])
            payload         = message.split(":")[4]

            #####
            print_str = "Pack: [{}#.. -> {}#..], {}, <{}>"
            print_str = print_str.format(src_id,dest_id,self.node_id,payload)
            self.simulation_canvas.simulation.output_add(print_str)
            print(print_str)
            #####

#            # node lost routing information although it forwarded RREQ
#            # -> node has been turned off after RREP and before data forwarded
#            # very uncommon
#            if not dest_id in self.routing_table.keys():
#                return
            if dest_id == self.node_id:
                return

            self.unicast_Packet(src_id,dest_id,payload)


    def receive(self, message):
        self.rx_buffer.append(message)

    def step(self):

        to_remove = []
        for dest_id in self.routing_table.keys():
            if self.routing_table[dest_id][3] > 0:
                #route becomes stale, but do not announce that, just dont trust your route any more
                if self.routing_table[dest_id][3] == 1:
                    self.routing_table[dest_id][2] = 255
                    # better for path optimality -> unused routes expire and a new route is forced to build up independent on worse rrep for other nodes
                    self.routing_table[dest_id][0] = self.inc_16(self.routing_table[dest_id][0])
                self.routing_table[dest_id][3] -= 1

        self.refresh_vrt()

        while len(self.rx_buffer) > 0:
            message = self.rx_buffer.pop(0)
            self.process_received_message(message)

        self.decrease_expiration_time_route_request_memory()

        if self.node_id == 0:
            return

        if self.rrequest_sent:
            return

        if len(self.tx_buffer) > 0:
            src_id,dest_id,payload = self.tx_buffer[0]
            if dest_id in self.routing_table.keys():
                hop_cnt = self.routing_table[dest_id][1]
                if hop_cnt < 255:
                    self.unicast_Packet(src_id,dest_id,payload)
                    self.tx_buffer.pop(0)



        rolling = random.random()
        if rolling <= self.tx_probability:
            src_id = self.node_id
            dest_id = 0
            message = "dummy_message{}".format(self.node_id)

            # randomly assume that the known route is stale to ensure a route refreshing over time
            demand_new_route = random.random() < 0.05
            self.schedule_unicast_Packet(src_id,dest_id,message, demand_new_route=demand_new_route)

        if self.tx_probability == 0:
            current_second = self.simulation_canvas.tick/self.simulation_canvas.update_rate
            if str(current_second) in self.tx_at.keys():
                src_id = self.node_id
                dest_id = self.tx_at[str(current_second)][0]
                message = self.tx_at[str(current_second)][1]
                self.schedule_unicast_Packet(src_id,dest_id,message)




class Transmission(object):
    def __init__(self, simulation_canvas, n1, n2, tx_duration):
        self.simulation_canvas = simulation_canvas
        self.n1 = n1
        self.n2 = n2
        self.tx_duration = tx_duration
        self.colorised_counter = -1
        self.draw_entity()

    def get_coords(self):
        x1,y1 = self.n1.cor_x,self.n1.cor_y
        x2,y2 = self.n2.cor_x,self.n2.cor_y

        node_distance = math.hypot(x1-x2,y1-y2)

        begin_ratio = ((self.n2.width/2)+1)/node_distance
        end_ratio = 1-((self.n1.width/2)+1)/node_distance

        x1 = begin_ratio*x2+(1-begin_ratio)*x1
        y1 = begin_ratio*y2+(1-begin_ratio)*y1
        x2 = end_ratio*x2+(1-end_ratio)*x1
        y2 = end_ratio*y2+(1-end_ratio)*y1

        return x1,y1,x2,y2

    def draw_entity(self):
        x1,y1,x2,y2 = self.get_coords()
        self.entity = self.simulation_canvas.canvas.create_line(x1,y1, x2,y2, width=2)

    def remove(self):
        self.simulation_canvas.canvas.delete(self.entity)

    def step(self):
        self.tx_duration -= 1



class SimulationCanvas(threading.Thread):
    def __init__(self, simulation, width, height):
        super().__init__()
        self.width = width
        self.height = height
        self.simulation = simulation
        self.canvas = tk.Canvas(self.simulation.root, width=self.width, height=self.height, borderwidth=0, highlightthickness=0, bg="#DDD")
        self.canvas.grid(row=0, column=1, padx=10, pady=10)

        self.update_rate = 20
        self.simulation_on = False

        self.node_width = 20
        self.node_tx_range = 120
        self.tx_duration = max(1, int(self.update_rate/10)) # min 100ms
        self.node_min_distance = self.node_tx_range*0.75
        self.node_at_most_one_max_distance = self.node_tx_range*0.9

        self.package_generation_T  = 60
        self.route_expiration_T     = 60

        self.reset_network()

    def reset_network(self):
        self.canvas.delete("all")
        self.nodes = []
        self.transmissions = []
        self.medium_transmission_buffer = []
        self.tick = 0

    def initialise_network(self, number_nodes):
        self.reset_network()
        self.number_nodes = number_nodes

        self.create_random_nodes()
        for node in self.nodes:
            self.canvas.itemconfigure(node.entity,fill="cyan")

    def load_network(self, testfile):
        self.reset_network()

        with open(testfile, "r") as json_file:
            loaded = json.load(json_file)

        simulation_config = loaded["simulation_canvas"]
        if "node_width"             in simulation_config.keys():
            self.node_width             = simulation_config["node_width"]
        if "node_tx_range"          in simulation_config.keys():
            self.node_tx_range          = simulation_config["node_tx_range"]
        if "update_rate"            in simulation_config.keys():
            self.update_rate            = simulation_config["update_rate"]
        if "package_generation_T"   in simulation_config.keys():
            self.package_generation_T   = simulation_config["package_generation_T"]
        if "route_expiration_T"   in simulation_config.keys():
            self.route_expiration_T     = simulation_config["route_expiration_T"]

        nodes_config = loaded["nodes"]
        for node_conf in nodes_config:
            cor_x       = node_conf["cor_x"]
            cor_y       = node_conf["cor_y"]
            node_id     = node_conf["node_id"]
            self.add_node(cor_x,cor_y,node_id)
            node = self.nodes[-1]
            if "tx_probability"         in node_conf.keys():
                node.tx_probability         = node_conf["tx_probability"]
                if node.tx_probability == 0:
                    node.tx_at = dict()
            if "tx_at"                  in node_conf.keys():
                node.tx_at                  = node_conf["tx_at"]
            if "seq_num"                in node_conf.keys():
                node.seq_num                = node_conf["seq_num"]
            if "routing_table"          in node_conf.keys():
                for entry in node_conf["routing_table"].keys():
                    node.routing_table[int(entry)] = node_conf["routing_table"][entry]
                    node.routing_table[int(entry)][3] *= self.update_rate

        for node in self.nodes:
            self.canvas.itemconfigure(node.entity,fill="cyan")

    def add_node(self,cor_x,cor_y,node_id):
        send_probability = 1/self.update_rate / self.package_generation_T # e.g. 60 -> every minute
        expiration_time = self.update_rate * self.route_expiration_T # e.g. 60 -> every minute
        node_properties = [node_id, self.node_tx_range, send_probability, expiration_time]
        new_node = AODVLMNode(self, self.node_width, cor_x, cor_y, node_properties)
        self.nodes.append(new_node)

    def create_random_nodes(self):
        rand_range_x1,rand_range_x2 = self.node_width/2,self.width-self.node_width/2
        rand_range_y1,rand_range_y2 = self.node_width/2,self.height-self.node_width/2

        node_id_counter = 0
        while len(self.nodes) < self.number_nodes:
            self.canvas.update()
            cor_x = random.randint(rand_range_x1,rand_range_x2)
            cor_y = random.randint(rand_range_y1,rand_range_y2)

            cor_x = max(self.node_width/2, cor_x)
            cor_x = min(self.width-self.node_width/2, cor_x)
            cor_y = max(self.node_width/2, cor_y)
            cor_y = min(self.height-self.node_width/2, cor_y)

            dists = [n.get_distance((cor_x,cor_y)) for n in self.nodes]
            if all(dist > self.node_min_distance for dist in dists) and any(dist < self.node_at_most_one_max_distance for dist in dists):
                self.add_node(cor_x,cor_y,node_id_counter)
                node_id_counter += 1
                rand_range_x1 = min(rand_range_x1,self.nodes[-1].cor_x-self.node_at_most_one_max_distance)
                rand_range_x2 = max(rand_range_x2,self.nodes[-1].cor_x+self.node_at_most_one_max_distance)
                rand_range_y1 = min(rand_range_y1,self.nodes[-1].cor_y-self.node_at_most_one_max_distance)
                rand_range_y2 = max(rand_range_y2,self.nodes[-1].cor_y+self.node_at_most_one_max_distance)
            elif len(self.nodes) == 0:
                self.add_node(self.width/2,self.height/2,node_id_counter)
                node_id_counter += 1
                rand_range_x1 = self.nodes[-1].cor_x-self.node_at_most_one_max_distance
                rand_range_x2 = self.nodes[-1].cor_x+self.node_at_most_one_max_distance
                rand_range_y1 = self.nodes[-1].cor_y-self.node_at_most_one_max_distance
                rand_range_y2 = self.nodes[-1].cor_y+self.node_at_most_one_max_distance

    def medium_access(self, send_node, message):
        self.medium_transmission_buffer.append([send_node,message])

    def step(self):
        for node in self.nodes:
            self.canvas.itemconfigure(node.entity,fill="cyan")

        changes = False
        while len(self.medium_transmission_buffer) > 0:
            changes = True
            send_node,message = self.medium_transmission_buffer.pop(0)
            self.canvas.itemconfigure(send_node.entity,fill="red")
            for node in self.nodes:
                distance = node.get_distance((send_node.cor_x,send_node.cor_y))
                if distance <= send_node.tx_range and distance > send_node.width:
                    new_transmission = Transmission(self,send_node,node,self.tx_duration)
                    self.transmissions.append(new_transmission)
                    node.receive(message)
        if changes:
            time.sleep(2)
            #####
            print_str = "-"*20
            self.simulation.output_add(print_str)
            print(print_str)
            #####



#    def mouse_click_callback_right(self, event):
#        for n in self.nodes:
#            clickdist = n.get_distance((event.x,event.y))
#            if clickdist < self.node_width/2:
#                pass
#
#    def mouse_click_callback_left(self, event):
#        for n in self.nodes:
#            clickdist = n.get_distance((event.x,event.y))
#            if clickdist <= n.width/2:
#                pass
#
#    def mouse_motion_callback(self, event):
#        for node in self.nodes:
#            dist = node.get_distance((event.x,event.y))
#            if dist <= node.width/2:
#                pass


    def run(self):
        while True:
            loop_start_time = time.time()

            if self.simulation_on:
                self.tick += 1
                self.simulation.label_ticks_string_var.set("{}".format(self.tick))
                for n in self.nodes:
                    n.step()
                to_remove_tx = []
                self.transmissions.sort(key=lambda x:x.n1.node_id)
                for t in self.transmissions:
                    t.step()
                    if(t.tx_duration <= 0):
                        to_remove_tx.append(t)
                for t in to_remove_tx:
                    t.remove()
                    self.transmissions.remove(t)

                self.step()

            self.canvas.update()

            loop_end_time = time.time()
            sleep_time = max(0, (1/self.update_rate)-(loop_end_time-loop_start_time))

            time.sleep(sleep_time)


class Simulation(object):
    def __init__(self,width,height):
        self.width = width
        self.height = height

        self.root = tk.Tk()
        self.root.config(background = "white")

        self.panel_width = 500

        self.left_frame = tk.Frame(self.root,width=self.panel_width,height=self.height, bg="#F5F5F5")
        self.left_frame.grid(row=0,column=0,padx=10,pady=10)

        self.entry_load_network_filename = tk.Entry(self.left_frame, width=20)
        self.entry_load_network_filename.grid(row=0, column=0, padx=5, pady=5)

        self.button_load_network = tk.Button(self.left_frame, text="Load Network", bg="#00F0FF", width=20, font="Monospace", command=self.button_load_network_callback)
        self.button_load_network.grid(row=1, column=0, padx=5, pady=5)

        self.slider_num_nodes = tk.Scale(self.left_frame, from_=5, to=160, resolution=5, orient=tk.HORIZONTAL, length=160)
        self.slider_num_nodes.grid(row=2, column=0, padx=5, pady=5)

        self.button_generate_network = tk.Button(self.left_frame, text="Generate Network", bg="#00F0FF", width=20, font="Monospace", command=self.button_generate_network_callback)
        self.button_generate_network.grid(row=3, column=0, padx=5, pady=5)

        self.button_toggle_simulation = tk.Button(self.left_frame, text="Toggle Simulation", bg="#00F0FF", width=20, font="Monospace", command=self.button_toggle_simulation_callback)
        self.button_toggle_simulation.grid(row=4, column=0, padx=5, pady=5)

        self.label_ticks_string_var = tk.StringVar()
        self.label_ticks_string_var.set("0")

        self.label_ticks = tk.Label(self.left_frame, textvariable=self.label_ticks_string_var, font="Monospace", bg="#F5F5F5")
        self.label_ticks.grid(row=5, column=0, padx=5, pady=5)

        self.label_output_string_var = tk.StringVar()
        self.label_output_string_var.set(".\n"*40)

        self.label_output = tk.Label(self.left_frame, textvariable=self.label_output_string_var, font=("Monospace", 8), justify=tk.LEFT, bg="#F5F5F5")
        self.label_output.grid(row=6, column=0, padx=5, pady=5)

        self.simulation_canvas = SimulationCanvas(self, self.width-self.panel_width,self.height)
        self.simulation_canvas.start()

        self.root.wm_title("Link Reversal Simulation")
        self.root.mainloop()

    def output_add(self, line):
        out = self.label_output_string_var.get().split("\n")
        out.append(line)
        out = out[-40:]
        self.label_output_string_var.set("\n".join(out))

    def button_load_network_callback(self):
        filename = self.entry_load_network_filename.get()
        filename += ".json"
        filename = filename.replace(".json.json",".json")
        self.simulation_canvas.load_network(filename)

    def button_generate_network_callback(self):
        number_nodes = self.slider_num_nodes.get()
        self.simulation_canvas.initialise_network(number_nodes)

    def button_toggle_simulation_callback(self):
        self.simulation_canvas.simulation_on = not self.simulation_canvas.simulation_on


if __name__ == "__main__":

#    simulation = Simulation(800,800)
    simulation = Simulation(1650,820)
