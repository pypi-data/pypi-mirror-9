import gc
import os
import sys
import psutil
import time
import datetime
import errno
import socket
from pandas import HDFStore, DataFrame
import numpy as np
from execo_g5k import get_host_cluster
from kwapi.utils import cfg, log




LOG = log.getLogger(__name__)

hdf5_opts = [
    cfg.BoolOpt('signature_checking',
                required=True,
                ),
    cfg.MultiStrOpt('probes_endpoint',
                    required=True,
                    ),
    cfg.MultiStrOpt('watch_probe',
                    required=False,
                    ),
    cfg.StrOpt('driver_metering_secret',
               required=True,
               ),
    cfg.StrOpt('hdf5_dir',
               required=True,
               ),
]

cfg.CONF.register_opts(hdf5_opts)

measurements = {}


def print_memory(m=None):
    p = psutil.Process(os.getpid())
    (rss, vms) = p.get_memory_info()
    mp = p.get_memory_percent()
    LOG.info("%-10.10s cur_mem->%.2f (MB),per_mem->%.2f" % (m, rss / 1000000.0, mp))


def _get_hdf5_file(ts=None):
    """ """
    if not ts:
        ts = int(time.time())
    return cfg.CONF.hdf5_dir + '/store_' + \
        datetime.datetime.fromtimestamp(ts).strftime("%Y-%m") + \
        '.h5'
        
    

def get_probe_path(probe):
    if '.' in probe:
        host = probe.split('.')[1]
        cluster = get_host_cluster(host)
        if cluster:
            return cluster + '/' + host.replace('-', '_')
    else:
        return probe



def create_dir():
    """Creates all required directories."""
    try:
        os.makedirs(cfg.CONF.hdf5_dir)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


def update_hdf5(probe, watts):
    """Updates HDF5 file associated with this probe."""

    if probe not in measurements:
        measurements[probe] = []
    measurements[probe].append((round(time.time(), 3), watts))
    
    if len(measurements[probe]) == 5: ## Change to 10
        try:
            LOG.debug('STORE : %s', _get_hdf5_file())
            zipped = map(list, zip(*measurements[probe]))
            write_hdf5_file(probe, np.array(zipped[0]), np.array(zipped[1]))
        except:
            print_memory(probe)
            LOG.error('unable to update HDF5 file for %s', probe)
            raise
        finally:
            del measurements[probe][:]


def write_hdf5_file(probe, timestamps, measurements):
    """ """
    store = HDFStore(_get_hdf5_file())
    LOG.info('Store open')
    try:     
        
        df = DataFrame(measurements, index=timestamps)
        print_memory(probe)
        store.append(get_probe_path(probe), df)
    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise
    finally:
        store.close()
        LOG.info('Store close')
        print_memory(probe)
    
