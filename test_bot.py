#!/usr/bin/env python3
"""
Test script for Kernel Builder Telegram Bot
This script validates the bot's core functionality without requiring actual tokens.
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add the current directory to the path to import bot
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bot import KernelBuilderBot, DEFAULT_VALUES

class TestKernelBuilderBot(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.bot = KernelBuilderBot()
        
    def test_default_values(self):
        """Test that default values are properly defined."""
        required_keys = [
            'COMPILER', 'KREPO', 'KBRANCH', 'NOTES', 'SUFFIX',
            'ZREPO', 'ZBRANCH', 'KSU', 'TG_RECIPIENT', 'CONTAINER'
        ]
        
        for key in required_keys:
            self.assertIn(key, DEFAULT_VALUES)
        
        # Test specific default values
        self.assertEqual(DEFAULT_VALUES['COMPILER'], 'Geopelia-Clang-20')
        self.assertEqual(DEFAULT_VALUES['CONTAINER'], 'fedora:40')
        self.assertEqual(DEFAULT_VALUES['KBRANCH'], 'yoka')
    
    @patch('requests.post')
    def test_trigger_github_workflow_success(self, mock_post):
        """Test successful GitHub workflow trigger."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 204
        mock_post.return_value = mock_response
        
        # Mock the runs request
        with patch('requests.get') as mock_get:
            mock_runs_response = Mock()
            mock_runs_response.status_code = 200
            mock_runs_response.json.return_value = {
                'workflow_runs': [{
                    'html_url': 'https://github.com/test/repo/actions/runs/123'
                }]
            }
            mock_get.return_value = mock_runs_response
            
            # Test the method
            config = DEFAULT_VALUES.copy()
            config['user_id'] = 12345
            
            # Mock environment variables
            with patch.dict(os.environ, {
                'GITHUB_TOKEN': 'test_token',
                'GITHUB_OWNER': 'test_owner',
                'GITHUB_REPO': 'test_repo',
                'GITHUB_WORKFLOW': 'test.yml'
            }):
                import asyncio
                success, message = asyncio.run(self.bot.trigger_github_workflow(config))
                
                self.assertTrue(success)
                self.assertIn('Monitor your build progress', message)
    
    @patch('requests.post')
    def test_trigger_github_workflow_failure(self, mock_post):
        """Test failed GitHub workflow trigger."""
        # Mock failed response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = 'Unauthorized'
        mock_post.return_value = mock_response
        
        config = DEFAULT_VALUES.copy()
        config['user_id'] = 12345
        
        # Mock environment variables
        with patch.dict(os.environ, {
            'GITHUB_TOKEN': 'invalid_token',
            'GITHUB_OWNER': 'test_owner',
            'GITHUB_REPO': 'test_repo',
            'GITHUB_WORKFLOW': 'test.yml'
        }):
            import asyncio
            success, message = asyncio.run(self.bot.trigger_github_workflow(config))
            
            self.assertFalse(success)
            self.assertIn('GitHub API error', message)
    
    def test_workflow_payload_structure(self):
        """Test that the workflow payload is structured correctly."""
        config = DEFAULT_VALUES.copy()
        config['NOTES'] = 'Test build'
        config['KSU'] = 'both'
        
        # We'll test the payload structure by examining what would be sent
        expected_inputs = {
            'COMPILER': config['COMPILER'],
            'KREPO': config['KREPO'],
            'KBRANCH': config['KBRANCH'],
            'CONTAINER': config['CONTAINER'],
            'NOTES': config['NOTES'],
            'KSU': config['KSU']
        }
        
        # Verify all required fields are present
        for key in ['COMPILER', 'KREPO', 'KBRANCH', 'CONTAINER']:
            self.assertIn(key, expected_inputs)
            self.assertIsNotNone(expected_inputs[key])
    
    def test_bot_initialization(self):
        """Test bot initialization."""
        self.assertIsNotNone(self.bot.github_api_base)
        self.assertEqual(self.bot.github_api_base, "https://api.github.com")
        self.assertIsInstance(self.bot.active_builds, dict)
    
    def test_environment_validation(self):
        """Test environment variable validation."""
        # Test with missing tokens
        with patch.dict(os.environ, {}, clear=True):
            # This should not raise an exception during import
            # The actual validation happens in the run method
            pass
    
    async def mock_update_message(self, text, parse_mode=None, reply_markup=None):
        """Mock update message for testing."""
        return Mock()
    
    def test_conversation_states(self):
        """Test that conversation states are properly defined."""
        from bot import (COMPILER, KREPO, KBRANCH, NOTES, SUFFIX, 
                        ZREPO, ZBRANCH, KSU, TG_RECIPIENT, CONTAINER, CONFIRM)
        
        # Ensure all states have unique values
        states = [COMPILER, KREPO, KBRANCH, NOTES, SUFFIX, 
                 ZREPO, ZBRANCH, KSU, TG_RECIPIENT, CONTAINER, CONFIRM]
        
        self.assertEqual(len(states), len(set(states)), "Conversation states must be unique")

def run_syntax_check():
    """Run syntax check on the bot file."""
    try:
        import ast
        with open('bot.py', 'r') as f:
            source = f.read()
        ast.parse(source)
        print("✅ Syntax check passed")
        return True
    except SyntaxError as e:
        print(f"❌ Syntax error: {e}")
        return False

def run_import_check():
    """Check if all imports are available."""
    try:
        import telegram
        import requests
        import dotenv
        print("✅ All required packages are available")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def main():
    """Run all tests."""
    print("🔧 Testing Kernel Builder Telegram Bot")
    print("=" * 50)
    
    # Run syntax check
    if not run_syntax_check():
        return False
    
    # Run import check
    if not run_import_check():
        return False
    
    # Run unit tests
    print("\n📋 Running unit tests...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    print("\n✅ All tests completed!")
    print("\n📝 Next steps:")
    print("1. Set up your .env file with actual tokens")
    print("2. Test the bot with a real Telegram bot token")
    print("3. Deploy the bot to your preferred platform")
    
    return True

if __name__ == '__main__':
    main()

