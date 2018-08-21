import tkinter as tk
import time
import threading
import random
import math
import json

## RREQ:
#           "RREQ:last_hop:src_id:src_seq_num:dest_id:dest_seq_num:hop_count"
## RREP:
#           "RREP:last_hop:next_hop:dest_id:dest_seq_num:src_id:hop_count" # src_id is initiator of rreq
## routing_table:
#           dict: dest_id   -> [dest_seq_num,next_hop,hop_count]
## last_requests:
#           dict: src_id    -> src_seq_num

class AODVLMNode(object):
    def __init__(self, simulation_canvas, width, cor_x, cor_y, tx_range, node_id):
        super().__init__()
        self.simulation_canvas = simulation_canvas

        self.width = width
        self.cor_x = cor_x
        self.cor_y = cor_y

        self.tx_range = tx_range
        self.tx_probability = (1/self.simulation_canvas.update_rate)/5 # every 5 seconds

        self.node_id = node_id
        self.seq_num = random.randint(0,100)

        self.draw_entity(self.cor_x,cor_y)

        self.routing_table = dict()
        self.last_requests = dict()
        self.rreq_sent = False

    def draw_entity(self,cor_x,cor_y):
        self.entity = self.simulation_canvas.canvas.create_oval(cor_x-self.width/2,cor_y-self.width/2,cor_x+self.width/2,cor_y+self.width/2)
        self.entity_text = self.simulation_canvas.canvas.create_text(cor_x,cor_y,text=str(self.node_id))

    def get_distance(self, posxy):
        x,y = posxy
        return math.hypot(self.cor_x-x,self.cor_y-y)

    def is_new_RREQ(self,message):
        if message.startswith("RREQ"):
            if not is_duplicate_RREQ():
                return True
        return False

    def is_fresh_RREP(self,message):
#           "RREP:last_hop:next_hop:dest_id:dest_seq_num:src_id:hop_count" # src_id is initiator of rreq
        if message.startswith("RREP"):
            dest_id,dest_seq_num = message.split(":")[3:5]
            num_hops = int(message.split(":")[6])
            if dest_id in self.routing_table.keys():
                if dest_seq_num < self.routing_table[dest_id][0]:
                    return False
                elif dest_seq_num == self.routing_table[dest_id][0]:
                    if num_hops >= self.routing_table[dest_id][2]:
                        return False
            return True
        return False

    def is_MSG(self,message):
        pass

    def is_duplicate_RREQ(self,message):
        src_id,src_seq_num = message.split(":")[2:4]
        if src_id in self.last_requests.keys():
            if src_seq_num == self.last_requests[src_id]:
                return True
        return False

    def fresher_route_in_table_RREQ(self,message):
        dest_id,dest_seq_num = message.split(":")[4:6]
        if dest_id in self.routing_table.keys():
            if self.routing_table[dest_id] > dest_seq_num:
                return True
        return False

    def is_destination_RREQ(self,message):
        dest_id = message.split(":")[4]
        if self.node_id == dest_id:
            return True
        return False

    def is_source_RREP(self,message):
        src_id = int(message.split(":")[5])
        if self.node_id == src_id:
            return True
        return False


    def send(self, message):
        self.simulation_canvas.medium_access(self,message)

    def receive(self, message):
        if self.is_new_RREQ(message):
            if self.fresher_route_in_table_RREQ(message):
                src_id          = int(message.split(":")[2])
                dest_id         = int(message.split(":")[4])
                dest_seq_num    = int(self.routing_table[dest_id][0])
                dest_num_hops   = int(self.routing_table[dest_id][2])

                self.route_reply(src_id,dest_id,dest_seq_num,dest_num_hops+1)

            else:
                last_hop        = int(message.split(":")[1])
                src_id          = int(message.split(":")[2])
                src_seq_num     = int(message.split(":")[3])
                self.last_requests[src_id] = src_seq_num
                self.routing_table[src_id] = [src_seq_num,last_hop,hop_count]

                if self.is_destination_RREQ(message):
                    dest_seq_num = int(message.split(":")[5])
                    self.seq_num = max(self.seq_num, dest_seq_num)

                    src_id = int(message.split(":")[2])
                    self.route_reply(src_id)

                else:
                    rreq_pkt = message.split(":")
                    rreq_pkt[1] = str(self.node_id)
                    rreq_pkt[6] = str(int(rreq_pkt[6])+1)
                    rreq_msg = ":".join(rreq_pkt)

                    self.send(rreq_msg)

        if self.is_fresh_RREP(message):
            last_hop            = int(message.split(":")[1])
            dest_id             = int(message.split(":")[3])
            dest_seq_num        = int(message.split(":")[4])
            num_hops            = int(message.split(":")[6])

            self.routing_table[dest_id] = [dest_seq_num,last_hop,num_hops]

            next_hop            = int(message.split(":")[2])
            if self.node_id == next_hop:
                if not self.is_source_RREP(message):
                    src_id = int(message.split(":")[5])
                    self.route_reply(src_id,dest_id,dest_seq_num,num_hops+1)
                else:
                    self.rreq_sent = False



    def route_request(self,dest_id=0):
#   "RREQ:last_hop:src_id:src_seq_num:dest_id:dest_seq_num:hop_count"
        if not dest_id in self.routing_table.keys():
            self.routing_table[dest_id] = [0,0,255]
        self.seq_num += 1
        rreq_pkt = []
        rreq_pkt.append("RREQ")
        rreq_pkt.append(str(self.node_id))
        rreq_pkt.append(str(self.node_id))
        rreq_pkt.append(str(self.seq_num))
        rreq_pkt.append(str(dest_id))
        rreq_pkt.append(str(self.routing_table[dest_id][0]))
        rreq_pkt.append(str(1))

        rreq_msg = ":".join(rreq_pkt)
        self.send(rreq_msg)
        self.rreq_sent = True

    def route_reply(self, src_id, dest_id=None, dest_seq_num=None, num_hops=1):
#   "RREP:last_hop:next_hop:dest_id:dest_seq_num:src_id:hop_count" # src_id is initiator of rreq
        if dest_id == None:
            dest_id = self.node_id
        if dest_seq_num == None:
            dest_seq_num = self.seq_num
        rrep_pkt = []
        rrep_pkt.append("RREP")
        rrep_pkt.append(str(self.node_id))
        rrep_pkt.append(str(self.routing_table[src_id][1]))
        rrep_pkt.append(str(dest_id))
        rrep_pkt.append(str(dest_seq_num))
        rrep_pkt.append(str(src_id))
        rrep_pkt.append(str(num_hops))

        rrep_msg = ":".join(rrep_pkt)
        self.send(rrep_msg)


    def step(self):
        rolling = random.random()
        if rolling <= self.tx_probability:
            self.message_buffer.append(message)

        if len(self.message_buffer) > 0:
            if 0 in self.routing_table :
                seq_num,next_hop,hop_count = self.routing_table[0]
                if hop_count < 255:
                    message = "MSG:dummy_message{}".format(self.node_id)
                    self.send(message)
                else:
                    if not self.rreq_sent:
                        self.route_request()



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

        self.update_rate = 2
        self.simulation_on = False

        self.node_width = 30
        self.node_tx_range = 100
        self.tx_duration = max(1, int(self.update_rate/10)) # min 100ms
        self.node_min_distance = 60
        self.node_at_most_one_max_distance = 100


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

    def add_node(self,cor_x,cor_y,node_id):
        new_node = AODVNode(self, self.node_width, cor_x, cor_y, self.node_tx_range,node_id)
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

        while len(self.medium_transmission_buffer) > 0:
            send_node,message = self.medium_transmission_buffer.pop(0)
            self.canvas.itemconfigure(send_node.entity,fill="red")
            for node in self.nodes:
                distance = node.get_distance((send_node.cor_x,send_node.cor_y))
                if distance <= send_node.tx_range and distance > send_node.width:
                    new_transmission = Transmission(self,send_node,node,self.tx_duration)
                    self.transmissions.append(new_transmission)
                    node.receive(message)


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

        self.panel_width = 400

        self.left_frame = tk.Frame(self.root,width=self.panel_width,height=self.height, bg="#F5F5F5")
        self.left_frame.grid(row=0,column=0,padx=10,pady=10)

        self.slider_num_nodes = tk.Scale(self.left_frame, from_=5, to=160, resolution=5, orient=tk.HORIZONTAL, length=160)
        self.slider_num_nodes.grid(row=0, column=0, padx=5, pady=5)

        self.button_generate_network = tk.Button(self.left_frame, text="Generate Network", bg="#00F0FF", width=20, font="Monospace", command=self.button_generate_network_callback)
        self.button_generate_network.grid(row=1, column=0, padx=5, pady=5)

        self.button_toggle_simulation = tk.Button(self.left_frame, text="Toggle Simulation", bg="#00F0FF", width=20, font="Monospace", command=self.button_toggle_simulation_callback)
        self.button_toggle_simulation.grid(row=2, column=0, padx=5, pady=5)

        self.label_ticks_string_var = tk.StringVar()
        self.label_ticks_string_var.set("0")

        self.label_ticks = tk.Label(self.left_frame, textvariable=self.label_ticks_string_var, font="Monospace", bg="#F5F5F5")
        self.label_ticks.grid(row=3, column=0, padx=5, pady=5)

        self.simulation_canvas = SimulationCanvas(self, self.width-self.panel_width,self.height)
        self.simulation_canvas.start()

        self.root.wm_title("Link Reversal Simulation")
        self.root.mainloop()

    def button_generate_network_callback(self):
        number_nodes = self.slider_num_nodes.get()
        self.simulation_canvas.initialise_network(number_nodes)

    def button_toggle_simulation_callback(self):
        self.simulation_canvas.simulation_on = not self.simulation_canvas.simulation_on


if __name__ == "__main__":

    simulation = Simulation(1500,800)
