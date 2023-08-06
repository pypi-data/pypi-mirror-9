from commandr import command


@command("apache")
def apache(metric=None):
    from zems.apache import Apache

    run_test(Apache(), metric)


@command("haproxy")
def haproxy(metric=None, pxname=None, svname=None):
    from zems.haproxy import HAProxy

    run_test(HAProxy(), metric, need_root=True, pxname=pxname, svname=svname)


@command("nginx")
def nginx(metric=None):
    from zems.nginx import Nginx

    run_test(Nginx(), metric)


@command("php-fpm")
def phpfpm(metric=None, pool=None):
    from zems.phpfpm import PhpFpm

    run_test(PhpFpm(), metric, pool=pool)


@command("rdiff-backup")
def rdiffbackup(metric=None):
    from zems.rdiffbackup import RdiffBackup

    run_test(RdiffBackup(), metric, need_root=True)


@command("redis")
def redis(metric=None, db=None):
    from zems.redis import Redis

    run_test(Redis(), metric, db=db)


@command("sphinx")
def sphinx(metric=None):
    from zems.sphinx import Sphinx

    run_test(Sphinx(), metric)


def run_test(test, metric, need_root=False, **kwargs):
    if metric is not None:
        if need_root:
            test.need_root()
        test.get(metric, **kwargs)
    else:
        test.print_metrics()
