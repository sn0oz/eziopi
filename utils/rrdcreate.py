#!/usr/bin/python
# -*- coding:utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import os, sys, rrdtool, json
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-l", "--list",
                  action="store_true", dest="list", default=False,
                  help="print graph list")
parser.add_option("-c", "--conf", 
                  action="store", type="string", dest="cfgFile", default="../cfg/cfg.json",
                  help="configuration file")
parser.add_option("-d", "--dir", 
                  action="store", type="string", dest="dir", default="rrd/",
                  help="destination directory")


(options, args) = parser.parse_args()


cfgAll = json.load(open(options.cfgFile))
cfgGraphs = cfgAll["graphs"]

# Standard average consolidation
RRAavg = ["RRA:LAST:0.8:1:864",
        "RRA:AVERAGE:0.8:6:336",
        "RRA:AVERAGE:0.8:12:720",
        "RRA:AVERAGE:0.8:48:720",
        "RRA:AVERAGE:0.8:288:730"]
        # 3j de donnees moy 5min 80% unknown
        # 1s de donnees moy 30min 80% unknown
        # 30j de donnees moy 1h 80% unknown
        # 4m de donnees moy 4h 80% unknown
        # 2a de donnees moy 24h 80% unknown




for i, graph in enumerate(cfgGraphs):
    if options.list:
        print(str(i) + ". " + graph["title"])
    else:
        filename = options.dir + graph["rrd"]
        rrdTime = ["--step", str(graph["delay"]), "--start", "0"]
        rrdDS = []
        for source in graph["sources"]:
            ds = "DS:" + source["ds"] + ":GAUGE:" + str(int(graph["delay"]*1.2)) + ":" + str(source["min"]) + ":" + str(source["max"])
            #print(ds)
            rrdDS.append(str(ds))
        #print(rrdDS)
        rrdData = rrdTime + rrdDS + RRAavg
        #print(rrdData)
        try:
            ret = rrdtool.create(filename, rrdData)
            print ("file %s created !" % filename)
        except Exception as e:
            print(e)


