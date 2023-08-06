"""
Running this script will keep launching trying to launch an instance of
CloudMan until one is allocated. It randomly chooses m1.xlarge or
m1.xxlarge instance type and checks if an instance has been allocated.
"""
import os
import sys
import time
import random
import logging
import smtplib
import datetime

from bioblend.util import Bunch
from bioblend.cloudman import CloudManConfig
from bioblend.cloudman import CloudManInstance
from bioblend.cloudman import VMLaunchException


logging.getLogger('boto').setLevel(logging.INFO)  # Only log boto messages >=INFO
logging.getLogger('bioblend').setLevel(logging.WARN)  # Only log boto messages >=INFO
log = None


def _setup_logging():
    # Logging setup
    # formatter = logging.Formatter("[%(levelname)s] %(module)s:%(lineno)d %(asctime)s: %(message)s")
    formatter = logging.Formatter("%(message)s")
    console = logging.StreamHandler()  # log to console - used during testing
    # console.setLevel(logging.INFO) # accepts >INFO levels
    console.setFormatter(formatter)
    log_file = logging.FileHandler(("%s.log" % os.path.splitext(sys.argv[0])[0]), 'w')
    log_file.setLevel(logging.DEBUG)  # accepts all levels
    log_file.setFormatter(formatter)
    log = logging.root
    log.addHandler(console)
    # log.addHandler(log_file)
    log.setLevel(logging.DEBUG)
    return log


def terminate_instance(reservation):
    try:
        reservation.instances[0].terminate()
        log.debug("Terminated it")
    except:
        log.debug("An instance not terminated")


def start_cloudman(name, pwd, inst_type, ami, ak, sk):
    """
    Start an instance of CloudMan with the provided arguments.

    Returns a tuple: an instance of ``CloudManConfig`` pointing to the
    settings used to launch this instance of CloudMan; and an instance
    of ``CloudManInstance`` pointing to the given instance of CloudMan.
    """
    cloud = None  # If left as None, BioBlend will default to Amazon
    # Define properties for the NeCTAR cloud
    cloud = Bunch(id='-1',
                  name="NeCTAR",
                  cloud_type='openstack',
                  bucket_default='cloudman-os',
                  region_name='NeCTAR',
                  region_endpoint='nova.rc.nectar.org.au',
                  ec2_port=8773,
                  ec2_conn_path='/services/Cloud',
                  cidr_range='115.146.92.0/22',
                  is_secure=True,
                  s3_host='swift.rc.nectar.org.au',
                  s3_port=8888,
                  s3_conn_path='/')
    success = False
    placement_options = ['monash-01', 'melbourne-qh2']
    placement = placement_options[random.randint(0, len(placement_options) - 1)]
    # Create an instance of the CloudManConfig class and launch a CloudMan instance
    cmc = CloudManConfig(ak, sk, name, ami, inst_type, pwd, cloud_metadata=cloud,
        placement=placement)
    log.debug("")
    log.debug("-------- %s" % datetime.datetime.now())
    log.debug("Configured an instance; requesting one (of type %s in zone %s)..."
        % (inst_type, placement))
    try:
        cmi = CloudManInstance.launch_instance(cmc)
    except VMLaunchException, e:
        log.debug("Launch exception: %s" % e)
        return None, None, success
    done_checking = False
    while not done_checking:
        time.sleep(5)
        cmi.update()
        if cmi.vm_status == 'pending':
            log.debug("Got one! Instance status: %s" % cmi.vm_status)
            while not cmi.cloudman_url:
                log.debug("Waiting for the instance to boot... (status: %s)" % cmi.vm_status)
                time.sleep(5)
                cmi.update()
                if cmi.vm_status == 'error':
                    break
                elif cmi.cloudman_url:
                    log.debug("Done! CloudMan IP is {0} - pwd is {1}".format(cmi.cloudman_url, pwd))
                    success = True
                    done_checking = True
        elif cmi.vm_status == 'error':
            log.debug("Instance errored...")
            terminate_instance(cmi.launch_result['rs'])
            done_checking = True
        else:
            log.debug("No instance state, waiting longer")
    return cmc, cmi, success


def send_email(cml, cm):
    fromaddr = 'afgane@gmail.com'
    toaddrs = 'afgane@gmail.com'
    msg = 'Got an instance! Available at %s' % cm.cloudman_url

    # Credentials (if needed)
    username = 'afgane'
    password = "Idon't8S0)"

    # The actual mail send
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(username, password)
    server.sendmail(fromaddr, toaddrs, msg)
    server.quit()
    print "Sent an email with msg: %s" % msg


def launch():
    now = datetime.datetime.utcnow()
    cluster_name = 'galaxy-tut_' + now.strftime("%m_%d_%H_%M_%S")
    pwd = 'Keyboardbookontable!'
    ami = 'ami-00001303'  # GVL-2.09
    ak = 'd8bcdbd01f7732842855f047d7a8d8fc'
    sk = '08f2cda0-b749-b7ac-1021-465c1fbc4645'
    instance_types = ['m1.xlarge', 'm1.xxlarge']
    instance_type = instance_types[random.randint(0, 1)]

    cml, cm, success = start_cloudman(cluster_name, pwd, instance_type, ami, ak, sk)
    if success:
        send_email(cml, cm)
    return cml, cm, success


def keep_trying():
    global log
    log = _setup_logging()
    success = False
    counter = 0
    while not success:
        counter += 1
        cml, cm, success = launch()
        secs = random.randint(10, 30)
        log.debug("[%s] Sleeping %s seconds..." % (counter, secs))
        time.sleep(secs)


# if __name__ == "__main__":
#     keep_trying()

class CM(object):
    def __init__(self):
        self.cloudman_url = 'localhost'
