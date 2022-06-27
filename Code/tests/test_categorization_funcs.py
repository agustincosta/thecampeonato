from ..categorization_funcs import Categorization

class TestCategorization:
    def test_getCloseMatches(self):
        cat = Categorization("Dataset/categorias.csv") 
        matches, indexes = cat.getCloseMatches("AGUA", 3, 0.8) 
        assert matches == ['AGUA', 'AGUJA']
        assert indexes[0][0] == [1]
        assert indexes[1][0] == [895]

        matches, indexes = cat.getCloseMatches("JANE", 3, 0.8)
        assert matches == ['JANE']
        assert indexes[0][0] == [508]

        matches, indexes = cat.getCloseMatches("LAVAR", 3, 0.8)
        assert matches == []
        assert indexes == []
