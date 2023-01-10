import sys
import datetime
import pytz
sys.path.append('./lib')
import Config
import Fname
import Job


def create_dt(dt_str):
    now = datetime.datetime.strptime(dt_str, '%H:%M:%S')
    now = now.replace(tzinfo=pytz.UTC)
    return now


def test_fname():
    strtime = datetime.datetime.strptime('20201011', '%Y%m%d')
    assert(Fname.render('one/two/three/$YYYYMMDD/test', strtime)=='one/two/three/20201011/test')
    assert(Fname.render('one/two/three/$YYYY/test', strtime)=='one/two/three/2020/test')
    assert(Fname.render('one/two/three/$MM/test', strtime)=='one/two/three/10/test')
    assert(Fname.render('one/two/three/$DD/test', strtime)=='one/two/three/11/test')
    assert(Fname.render('one/two/three/$YYYYMM/test', strtime)=='one/two/three/202010/test')
    assert(Fname.render('$DD/$YYYYMMDD/$YYYY/$MM/$YYYYMM/three/$YYYYMMDD/test', strtime)=='11/20201011/2020/10/202010/three/20201011/test')


def test_config():
    cfg = Config.Config('./cfg/unittest.json')
    assert(cfg.exists('store_fname'))
    assert(cfg.exists('job_config'))


def test_job():
    now = create_dt('12:00:00')

    provides = Job.file_dependency('./cfg/data/does_not_exist')
    job = Job.Job('j1', create_dt('11:00:00'), provides) 
    assert(job.would_run(now) == True)

    provides = Job.file_dependency('./cfg/data/does_not_exist')
    job = Job.Job('j2', create_dt('13:00:00'), provides)
    assert(job.would_run(now) == False)
