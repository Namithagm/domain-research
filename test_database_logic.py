import unittest
from unittest.mock import MagicMock, patch


class FakeResult:
    def __init__(self, data=None, count=None):
        self.data = data
        self.count = count


class TestDatabaseLogic(unittest.TestCase):
    def _query_mock(self, result=None, error=None):
        q = MagicMock()
        q.select.return_value = q
        q.gte.return_value = q
        q.eq.return_value = q
        q.neq.return_value = q
        q.or_.return_value = q
        q.order.return_value = q
        q.limit.return_value = q
        q.lte.return_value = q
        q.in_.return_value = q
        q.upsert.return_value = q
        q.insert.return_value = q
        if error:
            q.execute.side_effect = error
        else:
            q.execute.return_value = result or FakeResult()
        return q

    @patch("db.database.supabase")
    def test_get_fresh_domains_falls_back_and_validates_rows(self, mock_supabase):
        from db.database import get_fresh_domains

        mock_supabase.rpc.return_value.execute.side_effect = Exception("rpc missing")
        fallback_query = self._query_mock(
            result=FakeResult(data=[{"domain_name": "ok.com"}, {"bad": "row"}, "bad"])
        )
        mock_supabase.table.return_value = fallback_query

        rows = get_fresh_domains(count=5, min_score=70, cooldown=30, max_age_years=7)

        self.assertEqual(rows, [{"domain_name": "ok.com"}])
        mock_supabase.rpc.assert_called_once()
        mock_supabase.table.assert_called_once_with("domains")

    @patch("db.database.supabase")
    def test_mark_as_served_batches_updates(self, mock_supabase):
        from db.database import mark_as_served

        select_query = self._query_mock(
            result=FakeResult(data=[{"domain_name": "a.com", "times_served": 2}])
        )
        upsert_query = self._query_mock(result=FakeResult(data=[]))
        insert_query = self._query_mock(result=FakeResult(data=[]))

        mock_supabase.table.side_effect = [select_query, upsert_query, insert_query]

        mark_as_served(["a.com", "b.com", "a.com"], "batch-1")

        select_query.in_.assert_called_once()

        updates = upsert_query.upsert.call_args.args[0]
        updates_map = {row["domain_name"]: row["times_served"] for row in updates}
        self.assertEqual(updates_map["a.com"], 3)
        self.assertEqual(updates_map["b.com"], 1)

        served_logs = insert_query.insert.call_args.args[0]
        self.assertEqual({row["domain_name"] for row in served_logs}, {"a.com", "b.com"})

    @patch("db.database.supabase")
    def test_get_stats_handles_partial_query_failures(self, mock_supabase):
        from db.database import get_stats

        q_total = self._query_mock(result=FakeResult(count=10))
        q_high = self._query_mock(error=Exception("high failed"))
        q_available = self._query_mock(result=FakeResult(count=4))
        q_served = self._query_mock(result=FakeResult(count=2))
        q_old = self._query_mock(result=FakeResult(count=3))
        q_last = self._query_mock(result=FakeResult(data=[{"scrape_date": "2026-08-01"}]))

        mock_supabase.table.side_effect = [q_total, q_high, q_available, q_served, q_old, q_last]

        stats = get_stats()

        self.assertEqual(stats["total"], 10)
        self.assertEqual(stats["high_score"], 0)
        self.assertEqual(stats["available"], 4)
        self.assertEqual(stats["served_today"], 2)
        self.assertEqual(stats["old_domains"], 3)
        self.assertEqual(stats["last_scrape"], "2026-08-01")


if __name__ == "__main__":
    unittest.main()
