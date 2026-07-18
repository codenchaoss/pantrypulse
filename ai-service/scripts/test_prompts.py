import sys
import os
import unittest

# Add app to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from app.prompts.system_prompt import build_system_prompt
from app.prompts.chatbot_prompt import build_chat_prompt
from app.prompts.recipe_prompt import build_recipe_prompt
from app.prompts.menu_prompt import build_menu_prompt
from app.prompts.supplier_prompt import build_supplier_prompt
from app.prompts.description_prompt import build_description_prompt
from app.prompts.pricing_prompt import build_pricing_prompt
from app.prompts.inventory_prompt import build_inventory_prompt

class TestPrompts(unittest.TestCase):
    def test_01_system_prompt(self):
        prompt = build_system_prompt()
        self.assertIsInstance(prompt, str)
        self.assertIn("KitchenSync AI", prompt)
        self.assertIn("Telugu script", prompt)
        self.assertIn("Tenglish", prompt)
        self.assertIn("hallucination", prompt.lower())
        print("✓ Test 1: system_prompt.py validation - PASS")
        
    def test_02_chatbot_prompt(self):
        prompt = build_chat_prompt("Test Question", "Test Context", "Test History")
        self.assertIsInstance(prompt, str)
        self.assertIn("Test Question", prompt)
        self.assertIn("Test Context", prompt)
        self.assertIn("Test History", prompt)
        print("✓ Test 2: chatbot_prompt.py validation - PASS")
        
    def test_03_recipe_prompt(self):
        prompt = build_recipe_prompt(["Chicken", "Rice"], "Test Recipes Context")
        self.assertIsInstance(prompt, str)
        self.assertIn("Chicken, Rice", prompt)
        self.assertIn("Test Recipes Context", prompt)
        self.assertIn("maximum of 3 recipes", prompt)
        print("✓ Test 3: recipe_prompt.py validation - PASS")
        
    def test_04_menu_prompt(self):
        inventory = [{"ingredient": "Salmon", "quantity": "2kg", "expiry_days": 1}]
        prompt = build_menu_prompt(inventory, "Test Specials Context")
        self.assertIsInstance(prompt, str)
        self.assertIn("Salmon: Quantity=2kg, Expires in=1 days", prompt)
        self.assertIn("Test Specials Context", prompt)
        self.assertIn("daily specials", prompt.lower())
        print("✓ Test 4: menu_prompt.py validation - PASS")
        
    def test_05_supplier_prompt(self):
        prompt = build_supplier_prompt("Salmon", "15kg", "Test Supplier Context")
        self.assertIsInstance(prompt, str)
        self.assertIn("Salmon", prompt)
        self.assertIn("15kg", prompt)
        self.assertIn("Test Supplier Context", prompt)
        print("✓ Test 5: supplier_prompt.py validation - PASS")
        
    def test_06_description_prompt(self):
        prompt = build_description_prompt("Chicken Curry")
        self.assertIsInstance(prompt, str)
        self.assertIn("Chicken Curry", prompt)
        self.assertIn("3 to 4 lines maximum", prompt)
        print("✓ Test 6: description_prompt.py validation - PASS")
        
    def test_07_pricing_prompt(self):
        prompt = build_pricing_prompt("Salmon Special", 12.50, "Test Financial Context")
        self.assertIsInstance(prompt, str)
        self.assertIn("Salmon Special", prompt)
        self.assertIn("12.5", prompt)
        self.assertIn("Test Financial Context", prompt)
        print("✓ Test 7: pricing_prompt.py validation - PASS")
        
    def test_08_inventory_prompt(self):
        inventory = [{"ingredient": "Onion", "quantity": "5kg", "expiry_days": 3}]
        prompt = build_inventory_prompt(inventory, "Test Optimization Context")
        self.assertIsInstance(prompt, str)
        self.assertIn("Onion: Quantity=5kg, Expiry=3 days", prompt)
        self.assertIn("Test Optimization Context", prompt)
        self.assertIn("waste reduction", prompt.lower())
        print("✓ Test 8: inventory_prompt.py validation - PASS")

def run_tests():
    print("==================================================")
    print("KitchenSync Prompt Engineering Layer Verification")
    print("==================================================")
    
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPrompts)
    runner = unittest.TextTestRunner(verbosity=0)
    result = runner.run(suite)
    
    print("==================================================")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("FINAL STATUS: PASS")
        sys.exit(0)
    else:
        print("FINAL STATUS: FAIL")
        sys.exit(1)

if __name__ == "__main__":
    run_tests()
