import unittest
from app.services.analysis import analyze
class FefoTests(unittest.TestCase):
    def test_demand_is_not_duplicated_across_lots(self):
        result=analyze({'as_of':'2026-01-01','monthly_demand':{'X':30},'inventory':[
          {'sku':'X','lot':'A','quantity':30,'unit_cost':'10','expiry':'2026-01-31'},
          {'sku':'X','lot':'B','quantity':30,'unit_cost':'10','expiry':'2026-01-31'}]})
        self.assertEqual(result['metrics']['exposicion_pen'],'300.00')
    def test_blocked_does_not_consume_demand(self):
        result=analyze({'as_of':'2026-01-01','monthly_demand':{'X':30},'inventory':[
          {'sku':'X','lot':'A','quantity':30,'unit_cost':'10','expiry':'2026-01-31','status':'blocked'},
          {'sku':'X','lot':'B','quantity':30,'unit_cost':'10','expiry':'2026-01-31'}]})
        self.assertEqual(result['items'][1]['estimated_remaining'],'0.00')
