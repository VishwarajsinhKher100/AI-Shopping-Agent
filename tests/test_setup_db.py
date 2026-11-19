import os
import tempfile
import unittest
from contextlib import closing

from shopping_agent import setup_db


class ProductDatabaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.original_db_path = setup_db.DB_PATH
        self.temp_dir = tempfile.TemporaryDirectory()
        setup_db.DB_PATH = os.path.join(self.temp_dir.name, "store.db")
        setup_db.create_database()

    def tearDown(self) -> None:
        setup_db.DB_PATH = self.original_db_path
        self.temp_dir.cleanup()

    def test_search_applies_organic_price_and_average_rating_filters(self) -> None:
        products = setup_db.search_products(
            query="honey",
            max_price=20,
            min_rating=4.5,
            organic=True,
        )

        self.assertEqual(
            {product["name"] for product in products},
            {
                "Organic Raw Honey",
                "Organic Buckwheat Honey",
                "Organic Acacia Honey",
            },
        )
        self.assertTrue(all(product["average_rating"] >= 4.5 for product in products))

    def test_order_inserts_one_record_for_the_selected_product(self) -> None:
        order_id = setup_db.create_order(1)

        self.assertIsNotNone(order_id)
        with closing(setup_db.sqlite3.connect(setup_db.DB_PATH)) as connection:
            orders = connection.execute(
                "SELECT product_id, product_name, price FROM orders WHERE id = ?",
                (order_id,),
            ).fetchall()
        self.assertEqual(orders, [(1, "Organic Raw Honey", 14.99)])

    def test_order_does_not_insert_for_an_unknown_product(self) -> None:
        self.assertIsNone(setup_db.create_order(999))

    def test_product_lookup_is_case_insensitive(self) -> None:
        product = setup_db.get_product_by_name("organic raw honey")

        self.assertIsNotNone(product)
        self.assertEqual(product["id"], 1)


if __name__ == "__main__":
    unittest.main()
