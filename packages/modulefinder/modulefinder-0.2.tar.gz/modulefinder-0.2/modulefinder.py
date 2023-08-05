#!python
# Copyright (c) 2015, Sven Thiele <sthiele78@gmail.com>
#
# This file is part of modulefinder.
#
# modulefinder is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# modulefinder is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with modulefinder.  If not, see <http://www.gnu.org/licenses/>.
# -*- coding: utf-8 -*-
import sys
import os
import argparse
#from pyasp.asp import *
from __modulefinder__ import bioquali

def find_mod( graph, node, visited, observed) :
    edges =[]
    new_visited= visited+[node]   
    if graph.has_key(node) :
      (pos,neg) = graph[node]
      #print 's',successors
      for s in pos:
        edges.append((s,node,1))
        if not (s in visited):
          if not (s in observed):
            found = find_mod( graph, s, new_visited, observed)
            edges+=found
      for s in neg:
        edges.append((s,node,-1))
        if not (s in visited):
          if not (s in observed):
            found = find_mod( graph, s, new_visited, observed)
            edges+=found    
      return edges
    else : return edges
    



if __name__ == '__main__':
       
       
    desc = ('modulefinder finds modules.')
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("networkfiles",
                        help="directory of influence graphs in SIF format")
    parser.add_argument("observationfile",
                        help="list of observed nodes")


    args = parser.parse_args()
    
    net_dir = args.networkfiles
    obs_string = args.observationfile
    
    
    flist =  os.listdir(net_dir)
    print '\nReading',len(flist),'network from',net_dir,'...\n'
    NETS = []
    for f in flist :
      net_string= os.path.join(net_dir,f)
      print '   reading',net_string,'... '
      net = bioquali.readSIFGraph(net_string)
      NETS.append((net,f))
      print 'done.'

      
    print '\nReading list of observed nodes',obs_string, '...'
    obs_nodes = []
    file = open(obs_string,'r')
    s = file.readline()
    while s!="":
      #print s.strip()
      obs_nodes.append(s.strip())
      s = file.readline()
    file.close()
    print 'done.'

    
    found_modules = {}
    for (n,name) in NETS :
      for o in obs_nodes:
         mod = find_mod(n, o, [], obs_nodes)
         nodup = list(set(mod))
         ident = str(nodup)
         if found_modules.has_key(ident):
           (edges,names) = found_modules[ident]
           names.append(name)
         else:
           found_modules[ident]=(nodup,[name])

    
    modulcounter=1
    for m in found_modules:
      print 'module',modulcounter,':'
      (edges,names) = found_modules[m]
      print 'module is part of the following networks:'
      print names
      print 'list of edges:'
      for (a,e,s) in edges :
        print a,'\t',s,'\t',e
      print ''
      modulcounter+=1
      
      
    if os.path.isfile("parser.out"): os.remove("parser.out")
    if os.path.isfile("parsetab.py"): os.remove("parsetab.py")
    if os.path.isfile("parsetab.pyc"): os.remove("parsetab.pyc")
    if os.path.isfile("sif_parser_lextab.py"): os.remove("sif_parser_lextab.py")
    if os.path.isfile("sif_parser_lextab.pyc"): os.remove("sif_parser_lextab.pyc")