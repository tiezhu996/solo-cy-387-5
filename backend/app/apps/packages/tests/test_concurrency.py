"""并发取件：同一待取件包裹被多个请求同时取走时，只允许一次成功。

使用 TransactionTestCase 而非 APITestCase：后者把整个测试包在事务里，
其它连接（工作线程）读不到未提交数据。这里种子数据需要真正提交，
并发 UPDATE 才能在数据库行锁（PostgreSQL）/写锁（SQLite）上真实竞争。
"""
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

from django.db import close_old_connections
from django.test import TransactionTestCase

from app.apps.packages import services
from app.apps.packages.models import Package
from app.apps.packages.tests.factories import create_stored
from app.constants.enums import PACKAGE_STATUS_PICKED
from app.utils.business_error import BusinessError

CONCURRENCY = 8
ROUNDS = 3


def _race_once(tracking_no, pickup_code, barrier):
    close_old_connections()
    barrier.wait()  # 所有线程同时进入临界区
    try:
        package = services.pickup_package(tracking_no, pickup_code)
        return ('ok', package.picked_at)
    except BusinessError as exc:
        return ('error', exc.err_code)
    finally:
        close_old_connections()


class ConcurrentPickupTests(TransactionTestCase):
    reset_sequences = True

    def test_only_one_pickup_succeeds_under_contention(self):
        for round_no in range(ROUNDS):
            tracking_no = f'RACE-{round_no}'
            create_stored(tracking_no, pickup_code='246810')
            barrier = Barrier(CONCURRENCY)

            with ThreadPoolExecutor(max_workers=CONCURRENCY) as pool:
                results = list(pool.map(
                    lambda _: _race_once(tracking_no, '246810', barrier),
                    range(CONCURRENCY),
                ))

            successes = [r for r in results if r[0] == 'ok']
            failures = [r for r in results if r[0] == 'error']

            # 恰好一次成功，其余全部是“重复取件”
            self.assertEqual(len(successes), 1, results)
            self.assertEqual(len(failures), CONCURRENCY - 1)
            self.assertTrue(all(code == 'PACKAGE_ALREADY_PICKED' for _, code in failures), results)

            # 最终状态与取件时间唯一、与胜出者一致，记录未被重复创建
            package = Package.objects.get(tracking_no=tracking_no)
            self.assertEqual(package.status, PACKAGE_STATUS_PICKED)
            self.assertIsNotNone(package.picked_at)
            self.assertEqual(package.picked_at, successes[0][1])

        self.assertEqual(Package.objects.count(), ROUNDS)
