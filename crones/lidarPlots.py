# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import datetime as dt
import sys, os, time, locale
import multiprocessing as mp
from multiprocessing.pool import Pool


##############################################################################

# baseDir = '/home/jhernandezv/Lidar/lidar/crones/'
# kind    = 'FixedPoint'
# kind    = '3D'
baseDir = os.path.dirname(os.path.abspath(__file__))
print sys.argv
kind = sys.argv[1]

baseDir = os.path.join( baseDir, kind )
print baseDir
if not os.path.exists( baseDir ):
    os.makedirs( baseDir )

os.chdir ( baseDir )

from lidar.lidar import Lidar
from lidar.utils.utils import LoggingPool, listener_configurer
locale.setlocale(locale.LC_TIME, ('en_GB','utf-8'))

now = dt.datetime.now() #- dt.timedelta(days=8)



def plots (obj,  scan, **kwargs):

    kwgs = dict(
        height=4.5 if scan  != 'Zenith' else 6,
        # cla=True
    )
    kwgs.update(kwargs)

    obj.plot( output='LVD', totalSignal=True, **kwgs )

    obj.plot( output='RCS', totalSignal=True, **kwgs )

    if kwargs.get('operational', False):
        obj.plot( output='fdfLn(RCS)', **kwgs)



def plotting(element, scan,  **kwargs):
    if 'hora' in kwargs.keys():
        element.raw = element.raw[
                        (now-dt.timedelta(hours=kwargs.pop('hora'))
                            ).strftime('%Y-%m-%d %H:%M'):]
    if element.raw.shape[0] > 1:
        plots(element, scan, operational=True, **kwargs)
        if scan != 'FixedPoint':
            plots(element, scan,
                dates=element.raw.index,
                scp=False,
                makeGif=True,
                **kwargs)
    else:
        print "No values to draw"
        pass


def worker_wrapper(arg):
    args, kwargs = arg
    return plotting(*args, **kwargs)

def main(scan):

    print 'cpu_count() = %d\n' % mp.cpu_count()

    instance =   Lidar(
        fechaI=(now-dt.timedelta(hours=48)).strftime('%Y-%m-%d %H:%M'),
        fechaF=now.strftime('%Y-%m-%d %H:%M'),
        scan=scan,
        output='raw',
        path='CalidadAire/Lidar/'
    )
    PROCESSES = 5
    print 'Creating pool with %d processes\n' % PROCESSES
    pool = LoggingPool(PROCESSES)
    print 'pool = %s' % pool

    if scan == 'FixedPoint':
        # instance.datos = instance.datos.resample('30s').mean()
        instance.raw = instance.raw.resample('30s').mean()
        instance.datosInfo = instance.datosInfo.resample('30s').mean()

        args    = (instance, scan)
        TASKS   = [(args, dict(hora=h,textSave='_%dh' %h)) for h in [48,24,12,6,3]]
        pool.map( worker_wrapper, TASKS)

    else:
        args    = (instance, scan)
        task    = [(args, dict(hora=12,textSave='_last'))]
        pool.map( worker_wrapper, task )


    # pool.map(worker_wrapper, TASKS)
    # time.sleep(300)
    # print 'Testing close():'
    # for worker in pool._pool:
    #     assert worker.is_alive()

    # pool.close()

    # while True:
    #     for worker in pool._pool:
    #         if not worker.is_alive():
    #             worker.close()
    #             worker.join()
    #         else:
    #             print 'Waiting to finish worker processes'
    #             time.sleep(10)

    pool.join()

    # for r in result:
    # print result.get()

    # for worker in pool._pool:
    #     assert not worker.is_alive()

    print '\tclose() succeeded\n'

    print  "Time: {} minutos".format( (dt.datetime.now()-now).total_seconds() /60. )


# main(kind)


if __name__ == '__main__':
    listener_configurer(kind)
    main(kind)
    # p = Process(target=lidar_cron, args=(kind,), name="r")
    # print "time start {}".format(dt.datetime.now())
    # p.start()
    # time.sleep(300)
    # print "time running {}".format(dt.datetime.now())
    # while True:
    #     if not p.is_alive():
    #         p.terminate()
    #         break
    # print "time end {}".format(dt.datetime.now())
    # p.join()
