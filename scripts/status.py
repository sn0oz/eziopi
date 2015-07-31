#!/usr/bin/python
# -*- coding:utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4


# Imports
import webiopi, logging
import time, subprocess, os, sys, re, json
#sys.path.append('/usr/local/lib/python3.2/dist-packages')
import rrdtool, requests
from threading import Timer
from webiopi.devices.sensor.onewiretemp import DS18B20

# Enable debug output
webiopi.setDebug()
#webiopi.setInfo()
requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.DEBUG)


# Retrieve GPIO lib
GPIO = webiopi.GPIO

# eziopi dir
eziopi_dir, script_path = os.path.split(os.path.dirname(os.path.realpath(__file__)))



# Config
cfgFile = os.path.join(eziopi_dir, "cfg/cfg.json")
cfgAll = json.load(open(cfgFile))

# RRDs
statusDir = os.path.join(eziopi_dir, "html/app/status/")


# Sensors & commands GPIOs
sensors = cfgAll["sensors"]
graphs = cfgAll["graphs"]

# Called by WebIOPi at script loading
def setup():
    webiopi.info("Script with macros - Setup")
    try:
        # Setup GPIOs
        sensorlist = sensors.keys() 
        for sensorname in sensorlist:
            sensor = sensors[sensorname]
            if sensor["type"] == "DHT22" or sensor["type"] == "relay":                
                GPIO.setFunction(sensor["id"], GPIO.OUT)
                GPIO.digitalWrite(sensor["id"], GPIO.LOW)
    except:
        webiopi.exception("! setup failed ! %s %s" % (sys.exc_info()[0], sys.exc_info()[1]))
        pass



# Looped by WebIOPi
def loop():
    try:
        loc = cfgAll["location"]
        lat = loc["lat"]
        lon = loc["lon"]
        for graph in graphs:
            dsnames = ""
            values = ""
            sources = graph["sources"]
            for source in sources:
                if source["disabled"] == True:
                    webiopi.debug("data source %s disabled !" % source["ds"])
                else:   
                    sensor = sensors[source["sensor"]]
                    if sensor["disabled"] == False:
                        if sensor["type"] == "WU":
                            data = measureWU(sensor["id"], source["data_index"], lat, lon)
                        elif sensor["type"] == "DHT22":
                            data = measureDHT("22", sensor["id"], source["data_index"])
                        elif sensor["type"] == "DS18B20":
                            data = measureDS18B20(sensor["id"])
                        elif sensor["type"] == "relay":
                            data = measureRelay(sensor["id"])
                        else:
                            webiopi.info("! sensor %s type unknown (%s) !" % (source["sensor"], sensor["type"]))
                            data = "U"
                    else:
                        # Sensor disabled, unknown data
                        webiopi.debug("! sensor -%s- disabled !" % (source["sensor"]))
                        data = "U"
                    dsnames += ':' + source["ds"]
                    values += ':' + str(data)
            # Remove first character (":") in ds names list
            dss = dsnames[1:]
            rrdupdate = rrdtool.update(statusDir + graph["rrd"], '--template', dss, 'N' + values)
    except:
        webiopi.info("! loop failed ! %s %s" % (sys.exc_info()[0], sys.exc_info()[1]))
        pass
    finally:
        # delay next measure in 5 min
        time.sleep(300)


# Called by WebIOPi at server shutdown
def destroy():
    webiopi.info("Script with macros - Destroy")
    try:
        # Reset GPIOs
        sensorlist = sensors.keys() 
        for sensorname in sensorlist:
            sensor = sensors[sensorname]
            if sensor["type"] == "DHT22" or sensor["type"] == "relay":                
                GPIO.setFunction(sensor["id"], GPIO.OUT)
                GPIO.digitalWrite(sensor["id"], GPIO.LOW)
    except:
        webiopi.info("! destroy failed ! %s %s" % (sys.exc_info()[0], sys.exc_info()[1]))
        pass



def measureDHT(DHTtype, gpio, index):
    try:
        script = os.path.join(eziopi_dir, "scripts/adafruit_dht")
        tries = 5
        for i in range(tries):
            val = str(subprocess.check_output([script, DHTtype, str(gpio)]))
            match = re.search('Temp.+\s([\d\.]+)\s.+Hum.+\s([\d\.]+)\s%', val)
            if match:
                temp, hr = match.group(1), match.group(2)
                webiopi.debug("DHT22 measure %s: temp=%s hr=%s" % (str(i+1), temp, hr))
                break
            else:
                # Erreur mesure gpioDHT22
                if i == tries-1:
                    temp = "U"
                    hr = "U"
                    webiopi.info("! DHT22 error after %s tries ! - stop trying" % str(i+1))
                else:
                    time.sleep(2)
    except:
        temp = "U"
        hr = "U"
        webiopi.exception("! DHT22 error ! %s" % sys.exc_info()[1])
    finally:
        values = [temp, hr]
        return values[index]


def measureDS18B20(sid):
    try:
        tmp = DS18B20(slave=sid)
        temp = tmp.getCelsius()
        webiopi.debug("DS18B20_temp = %s" % temp)
    except:
        webiopi.exception("! DS18B20 error ! %s %s" % (sys.exc_info()[0], sys.exc_info()[1]))
        temp = "U"
    finally:
        return temp
       


def measureWU(api_key, index, lat, lon):
    # get WeatherUnderground data
    try:
        webiopi.debug("Starting WU measure")
        url = "http://api.wunderground.com/api/" + api_key + "/conditions/q/" + lat + "," + lon + ".json"
        r = requests.get(url, timeout=2)
        data = r.json()
        dat = data["current_observation"]
        try:
            temp = str(round(dat["temp_c"], 1))
        except:
            temp = "U"
        #hr = str(round(dat["relative_humidity"], 1))
        match = re.search('([\d\.]+)%', dat["relative_humidity"])
        if match:
            hr = match.group(1)
        else:
            hr = "U"
        match = re.search('([\d\.]+)', dat["precip_1hr_metric"])
        if match:
            rain = match.group(1)
        else:
            rain = "U"
        #match = re.search('([\d\.]+)%', dat["clouds"]["all"])
        clouds = "0"
    except:
        temp = "U"
        hr = "U"
        clouds = "U"
        rain = "U"
        webiopi.info("! WU request error ! %s %s" % (sys.exc_info()[0], sys.exc_info()[1]))
    finally:
        values = [temp, hr, clouds, rain]
        webiopi.debug("WU values = %s" % values)
        return values[index]



def measureRelay(gpio):
    try:
        gpio = int(gpio)
        gpioState = int(GPIO.digitalRead(gpio))
    except:
        gpioState = "U"
        webiopi.info("! error checking gpio %s state ! %s - %s"  % (gpio, sys.exc_info()[0], sys.exc_info()[1]))
    finally:
        return gpioState
