""" This script searches the database for files flagged "N"ew or "M"odified.
For each date in the configured range, it checks if other stations are
available and defines the new jobs to be processed. Those are inserted in the
*jobs* table of the database.

To run it from the console:

.. code-block:: sh

    $ msnoise new_jobs

.. warning:: Upon first run, if the number of jobs, pass the ``--init``
    parameter to optimize the insert. Only use this flag once, otherwise
    problems will arise from duplicate entries in the jobs table.
"""

from api import *
import logging
import numpy as np


def main(init=False):
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s [%(levelname)s] %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    logging.info('*** Starting: New Jobs ***')

    db = connect()
    autocorr = get_config(db, name="autocorr", isbool=True)

    stations_to_analyse = ["%s.%s" % (sta.net, sta.sta) for sta in get_stations(db, all=False)]
    all_jobs = []
    updated_days = []
    nfs = get_new_files(db)
    for nf in nfs:
        start, end = nf.starttime.date(), nf.endtime.date()
        updated_days.append(start)
        updated_days.append(end)

    updated_days = np.asarray(updated_days)
    updated_days = np.unique(updated_days)

    count = 0
    for day in updated_days:
        jobs = []
        modified = []
        available = []
        for data in get_data_availability(db, starttime=day, endtime=day+datetime.timedelta(days=1)):
            sta = "%s.%s" % (data.net, data.sta)
            if sta in stations_to_analyse:
                available.append(sta)
                if data.flag in ["N", "M"]:
                    modified.append(sta)

        for m in modified:
            for a in available:
                if m != a or autocorr:
                    pair = ':'.join(sorted([m, a]))
                    if pair not in jobs:
                        all_jobs.append({"day": day, "pair": pair,
                                         "jobtype": "CC", "flag": "T",
                                         "lastmod": datetime.datetime.utcnow()})
                        jobs.append(pair)

        if init and len(all_jobs) > 1e5:
            logging.debug('Already 100.000 jobs, inserting')
            massive_insert_job(all_jobs)
            all_jobs = []
            count += 1e5

    if len(all_jobs) != 0:
        logging.debug('Inserting %i jobs' % len(all_jobs))
        if init:
            massive_insert_job(all_jobs)
        else:
            for job in all_jobs:
                update_job(db, job['day'], job['pair'],
                           job['jobtype'], job['flag'])
    count += len(all_jobs)

    for sta in get_stations(db, all=True):
        mark_data_availability(db, sta.net, sta.sta, flag='A')

    db.commit()
    logging.info('*** Finished: New Jobs ***')

    return count


if __name__ == "__main__":
    main()