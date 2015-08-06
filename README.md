# eziopi

eziopi is a set of scripts for [webiopi](https://code.google.com/p/webiopi/) which allows to create new applications easily.

### Features:
- unique JSON configuration file
- integrated program scheduler: [APScheduler](https://pypi.python.org/pypi/APScheduler/)
- multiple program types (cron-style, sensor's min/max, sunrise/sunset, custom)
- sensor monitoring (with [RRDtool](http://oss.oetiker.ch/rrdtool/) and [javascriptRRD](http://javascriptrrd.sourceforge.net/))
- unified interface

### How it works
A script manage sensor monitoring and logging (status.py), while another manage the programs scheduling (command.py). A configuration file (cfg/cfg.json) defines sensors, graphs and applications.
A status page shows all monitored data, and each application page generate buttons to program a GPIO's activation based on a common JS script (eziopi.js).

### Installation

##### Dependencies:
- [webiopi](https://code.google.com/p/webiopi/)
- [APScheduler](https://pypi.python.org/pypi/APScheduler/)

    ```
    cd ~/eziopi/python
    tar -xvzf APScheduler-3.0.0.tar.gz
    cd APScheduler-3.0.0/
    sudo python3 setup.py install
    ```
- [rrdtool](http://oss.oetiker.ch/rrdtool/)
    - rrdtool dependencies:

        ```
        sudo apt-get install rrdtool libcairo2-dev libpango1.0-dev libglib2.0-dev libxml2-dev librrd-dev
        ```
    ```
    cd ~/eziopi/python
    tar -xvzf python-rrdtool-1.4.7.tar.gz
    cd python-rrdtool-1.4.7/
    sudo python3 setup.py install
    ```
- [ephem](http://rhodesmill.org/pyephem/)

    ```
    cd ~/eziopi/python
    tar -xvzf ephem-3.7.5.1.tar.gz
    cd ephem-3.7.5.1/
    sudo python3 setup.py install
    ```
- additionnal python modules

    ```
    sudo apt-get install python3-requests python3-sqlalchemy
    ```

### Configuration
- webiopi config file

    ```
    cd ~/eziopi/
    sudo cp cfg/webiopi_config /etc/webiopi/config
    ```
- configuration file

    a JSON file including following parts:

    - location

        used to get weather conditions or compile sunrise/sunset times

    - graphs

        define graphs data sources and parameters

    - sensors

        list sensors type and id

    - app

        define applications program type and GPIO

    example: see cfg/cfg.json, creates a simple application to control 2 lights and monitor in & out temperature

- create new app folder

    for each app created webiopi needs a new folder (with eziopi it's simply a symbolic link to the default app)

    ```
    cd ~/eziopi/html/app/
    ln -s default-app/ NEW_APP_NAME
    ```

- generate RRD graphs

    a script generates graphs from configuration file

    ```
    cd ~/eziopi/utils/
    ./rrdcreate.py -d ../html/app/status/
    ```

### Customisation

