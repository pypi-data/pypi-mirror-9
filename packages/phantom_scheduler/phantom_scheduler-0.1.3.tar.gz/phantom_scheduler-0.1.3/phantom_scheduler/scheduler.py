#
# This file is part of phantom_scheduler.
#
# phantom_scheduler is free software: you can redistribute it and/or modify
# it under the terms of the LGNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# phantom_scheduler is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# LGNU Lesser General Public License for more details.
#
# You should have received a copy of the LGNU Lesser General Public License
# along with phantom_scheduler.  If not, see <http://www.gnu.org/licenses/>.
#
# DTU UQ Library
# Copyright (C) 2014 The Technical University of Denmark
# Scientific Computing Section
# Department of Applied Mathematics and Computer Science
#
# Author: Daniele Bigoni
#

__all__ = ['Scheduler', 'BLOCKING', 'NON_BLOCKING']

import threading
import Queue
import subprocess
import socket
import SocketServer
import os.path
import inspect
import time

BLOCKING = 'BLOCKING'
NON_BLOCKING = 'NON_BLOCKING'

class Node(threading.Thread):
    NOT_RUNNING = 'NOT_RUNNING'  # Node created but thread not started
    WAITING = 'WAITING'          # Waiting to enter the queue
    IDLE = 'IDLE'                # Running but waiting for some work
    WORKING = 'WORKING'          # Running some job
    DEAD = 'DEAD'                # The node dropped dead
    
    def __init__(self, base_port, job_queue, terminationFlag):
        super(Node,self).__init__()
        self.own_port = base_port
        self.status = Node.NOT_RUNNING
        self.job_queue = job_queue
        self.terminationFlag = terminationFlag
        
        # Set up socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                self.socket.bind( ('',self.own_port) )
                break
            except socket.error as serr:
                if serr.errno != 98: # Address already in use
                    raise serr
                self.own_port += 1
    
    def run(self):
        self.status = Node.WAITING
        
        self.socket.listen(1)
        
        # Get the connection
        self.conn, self.addr = self.socket.accept()
        print 'Connected by ', self.addr
        self.status = Node.IDLE
        
        # Check the queue for jobs and the termination flag
        while not self.terminationFlag.terminated or \
              (self.terminationFlag.terminated == 1 and not self.job_queue.empty()):
            try:
                self.status = Node.WORKING
                (blocking_flag,job, client_addr, client_port) = self.job_queue.get(block=False)
            except Queue.Empty:
                pass
            else:
                # Pass the job to the worker
                self.conn.sendall(job)
                # Wait for job completion
                returncode = self.conn.recv(1024)
                if blocking_flag == BLOCKING:
                    # Connect to the blocked process and signal the completion
                    bhost = client_addr
                    bport = client_port
                    bsocket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
                    bsocket.connect( (bhost,bport) )
                    bsocket.sendall(str(returncode))
                    bsocket.close()
            self.status = Node.IDLE
            time.sleep(0.1)
        
        job = 'EXIT'
        self.conn.sendall(job)

        self.conn.close()

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

class OutThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        client_addr = self.client_address[0]
        # Get the blocking flag
        blocking_flag = self.request.recv(1024)
        self.request.sendall('SET')
        if blocking_flag == BLOCKING:
            client_port = self.request.recv(1024)
            client_port = int(client_port)
            self.request.sendall('SET')
        else:
            client_addr = None
            client_port = None
        job = self.request.recv(1024)
        if job == 'EXIT':
            self.server.terminationFlag.terminated = 1
        else:
            # Equeue job
            self.server.job_queue.put( (blocking_flag,job,client_addr,client_port) )
        
class TerminationFlag():
    def __init__(self):
        # Possible statuses:
        # 0 = not terminated
        # 1 = terminated but wait to empty the queue
        # 2 = terminate now!
        self.terminated = 0

class Scheduler():
    
    def __init__(self, slots, queue_cmd, base_port):
        # Port base_port is used for the user to submit jobs
        # Ports base_port+1...base_port+slots+1 are used for connections with workers
        
        self.slots = slots
        self.queue_cmd = queue_cmd
        self.runner_file = 'psrunner'
        self.base_port = base_port
        self.hostname = socket.gethostname()
        
        self.node_list = []
        self.job_queue = Queue.Queue()

        # Create the socket servers to which the user should connect
        while True:
            try:
                self.out_server = ThreadedTCPServer(('', self.base_port), OutThreadedTCPRequestHandler)
                break
            except socket.error as serr:
                if serr.errno != 98:
                    raise serr
                # Address already in use
                self.base_port += 1
        self.out_server.job_queue = self.job_queue

    def get_input_port(self):
        return self.base_port
        
    def run(self):
        self.terminationFlag = TerminationFlag()
        self.out_server.terminationFlag = self.terminationFlag

        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        self.out_server_thread = threading.Thread(target=self.out_server.serve_forever)
        # Exit the server thread when the main thread terminates
        self.out_server_thread.daemon = True
        self.out_server_thread.start()
        
        try:
            # Create the pool of workers
            for i in xrange(self.slots):
                # Create Node and run the thread
                PORT = self.base_port + 1
                node = Node( PORT, self.job_queue, self.terminationFlag)
                node.start()
                self.node_list.append( node )

            time.sleep(0.5)

            for i,node in enumerate(self.node_list):
                PORT = node.own_port
                subprocess.Popen( self.queue_cmd + " " + self.runner_file + " -h " + str(self.hostname) + " -p " + str(PORT), shell=True )

            # # Populate the queue of jobs (artificially)
            # for i in xrange(10):
            #     self.job_queue.put("/home/dabi/tmp/sockets/job.py")
        
        except KeyboardInterrupt:
            self.terminationFlag.terminated = 2
            self.out_server_thread.stop()
