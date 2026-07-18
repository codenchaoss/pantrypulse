import sys
import os
import json
import unittest

class TestOpenClawFoundation(unittest.TestCase):
    
    def setUp(self):
        # Base openclaw folder is relative to this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.openclaw_dir = os.path.dirname(current_dir)

    def test_01_directory_structure(self):
        """Verify that all required subdirectories exist."""
        subdirs = ["config", "agents", "skills", "workflows", "services", "models", "tests"]
        for s in subdirs:
            path = os.path.join(self.openclaw_dir, s)
            self.assertTrue(os.path.isdir(path), f"Missing subdirectory: openclaw/{s}")
        print("✓ Test 1: Workspace directories structure - PASS")

    def test_02_config_loading(self):
        """Verify that openclaw.json is a valid JSON file and contains required keys."""
        config_path = os.path.join(self.openclaw_dir, "config", "openclaw.json")
        self.assertTrue(os.path.isfile(config_path), "Missing openclaw.json file.")
        
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            
        self.assertIn("agents", config)
        self.assertIn("models", config)
        self.assertIn("defaults", config["agents"])
        
        agents_list = config["agents"].get("list", [])
        self.assertEqual(len(agents_list), 1)
        self.assertEqual(agents_list[0]["id"], "kitchensync-manager")
        print("✓ Test 2: Configuration settings validation - PASS")

    def test_03_agent_profiles(self):
        """Verify that KitchenSync Manager Agent profile configuration files exist."""
        agent_dir = os.path.join(self.openclaw_dir, "agents", "kitchensync-manager")
        self.assertTrue(os.path.isdir(agent_dir), "Missing kitchensync-manager agent directory.")
        
        required_mds = ["AGENTS.md", "SOUL.md", "IDENTITY.md", "TOOLS.md", "USER.md"]
        for f_name in required_mds:
            path = os.path.join(agent_dir, f_name)
            self.assertTrue(os.path.isfile(path), f"Missing agent profile file: {f_name}")
        print("✓ Test 3: Agent instructions and profile markdown files - PASS")

    def test_04_skills_placeholders(self):
        """Verify that all target placeholder skills are created correctly."""
        skills_dir = os.path.join(self.openclaw_dir, "skills")
        self.assertTrue(os.path.isdir(skills_dir), "Missing skills directory.")
        
        skills = [
            "inventory_optimization",
            "recipe",
            "menu",
            "pricing",
            "description",
            "supplier"
        ]
        for skill in skills:
            path = os.path.join(skills_dir, skill, "SKILL.md")
            self.assertTrue(os.path.isfile(path), f"Missing SKILL.md for: {skill}")
        print("✓ Test 4: Placeholder skills definitions - PASS")

    def test_05_workflows_and_services(self):
        """Verify that placeholder workflows, services, and models exist."""
        workflow_path = os.path.join(self.openclaw_dir, "workflows", "restaurant_optimization.json")
        self.assertTrue(os.path.isfile(workflow_path), "Missing workflow configuration file.")
        
        gateway_path = os.path.join(self.openclaw_dir, "services", "gateway.py")
        self.assertTrue(os.path.isfile(gateway_path), "Missing gateway service file.")
        
        schema_path = os.path.join(self.openclaw_dir, "models", "schemas.py")
        self.assertTrue(os.path.isfile(schema_path), "Missing models schema file.")
        
        readme_path = os.path.join(self.openclaw_dir, "README.md")
        self.assertTrue(os.path.isfile(readme_path), "Missing README.md file.")
        print("✓ Test 5: Placeholders for workflows, services, models, and docs - PASS")

def run_tests():
    print("==================================================")
    print("KitchenSync OpenClaw Foundation Verification")
    print("==================================================")
    
    suite = unittest.TestLoader().loadTestsFromTestCase(TestOpenClawFoundation)
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
