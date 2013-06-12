from io import BytesIO
import unittest

from recipebook.importexport import load_gourmet


test_file = BytesIO(b"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE gourmetDoc>
<gourmetDoc>
    <recipe id="1">
        <title>
            Example Recipe
        </title>
        <category>
            Main
        </category>
        <cuisine>
            Italian
        </cuisine>
        <rating>
            5/5 stars
        </rating>
        <yields>
            5 servings
        </yields>
        <ingredient-list>
            <inggroup>
                <groupname>
                    Ingredients
                </groupname>
                <ingredient>
                    <amount>
                        3
                    </amount>
                    <unit>
                        Tbs
                    </unit>
                    <item>
                        butter
                    </item>
                    <key>
                        butter
                    </key>
                </ingredient>
                <ingredient>
                    <amount>
                        3.25
                    </amount>
                    <unit>
                        Tbs
                    </unit>
                    <item>
                        flour
                    </item>
                    <key>
                        flour
                    </key>
                </ingredient>
            </inggroup>
            <ingredient>
                <amount>
                    300
                </amount>
                <unit>
                    g
                </unit>
                <item>
                    lasagne pasta
                </item>
                <key>
                    lasagne pasta
                </key>
            </ingredient>
        </ingredient-list>
        <instructions>
            Example instructions.
        </instructions>
    </recipe>
</gourmetDoc>
""")


class GourmetImportTestCase(unittest.TestCase):
    """Test importing Gourmet XML file"""

    def test_import(self):
        recipes = list(load_gourmet(test_file))
        assert(len(recipes) == 1)
        recipe = recipes[0]

        assert(recipe.title == "Example Recipe")
        assert(recipe.instructions.strip() == "Example instructions.")

        assert(len(recipe.ingredient_groups) == 1)
        group = recipe.ingredient_groups[0]
        assert(group.title == "Ingredients")
        assert(len(group.ingredients) == 2)
        assert(group.ingredients[0].item == "butter")
        assert(int(group.ingredients[0].amount) == 3)

        assert(len(recipe.general_ingredients) == 1)
        assert(recipe.general_ingredients[0].item == "lasagne pasta")


if __name__ == '__main__':
    unittest.main()
