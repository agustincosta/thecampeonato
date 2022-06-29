import pytest
from ..db_funcs import DBFunctions

class TestDBFunctions:
    def test_analyseUserMonthlyPurchases(self, user_id:int, month:int, year:int, plot:bool=False):
        db = DBFunctions()
        try:
            db.analyseUserMonthlyPurchases(3, 6, 2021, False)
        except:
            pytest.fail("Unexpected error")