#!/usr/bin/env python3
"""
Telegram Bot for Kernel Builder Workflow
This bot allows users to trigger kernel builds via GitHub Actions workflow.
"""

import os
import logging
import json
import requests
from typing import Dict, Any, Optional
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ConversationHandler, ContextTypes, filters
)
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_OWNER = os.getenv('GITHUB_OWNER', 'zyexro')
GITHUB_REPO = os.getenv('GITHUB_REPO', 'kernel_builder')
GITHUB_WORKFLOW = os.getenv('GITHUB_WORKFLOW', 'main.yml')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Conversation states
(COMPILER, KREPO, KBRANCH, NOTES, SUFFIX, ZREPO, ZBRANCH, KSU, 
 TG_RECIPIENT, CONTAINER, CONFIRM) = range(11)

# Default values for workflow inputs
DEFAULT_VALUES = {
    'COMPILER': 'Geopelia-Clang-20',
    'KREPO': 'https://github.com/TelegramAt25/niigo_kernel_xiaomi_blossom',
    'KBRANCH': 'yoka',
    'NOTES': '',
    'SUFFIX': '',
    'ZREPO': '',
    'ZBRANCH': '',
    'KSU': '',
    'TG_RECIPIENT': '',
    'CONTAINER': 'fedora:40'
}

class KernelBuilderBot:
    def __init__(self):
        self.github_api_base = "https://api.github.com"
        self.active_builds = {}  # Store active build information
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a message when the command /start is issued."""
        welcome_message = (
            "🔧 *Kernel Builder Bot*\n\n"
            "Welcome! This bot helps you build custom kernels using GitHub Actions.\n\n"
            "Available commands:\n"
            "• `/build` - Start a new kernel build\n"
            "• `/status` - Check build status\n"
            "• `/help` - Show this help message\n\n"
            "To get started, use `/build` to configure and start a new kernel build."
        )
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a message when the command /help is issued."""
        help_message = (
            "🔧 *Kernel Builder Bot Help*\n\n"
            "*Commands:*\n"
            "• `/start` - Welcome message and overview\n"
            "• `/build` - Start a new kernel build process\n"
            "• `/status` - Check the status of your last build\n"
            "• `/help` - Show this help message\n\n"
            "*Build Process:*\n"
            "1. Use `/build` to start\n"
            "2. Configure build parameters (compiler, repo, branch, etc.)\n"
            "3. Confirm your settings\n"
            "4. Monitor the build progress\n\n"
            "*Required Setup:*\n"
            "• GitHub repository with kernel builder workflow\n"
            "• Valid GitHub token with repo access\n"
            "• Telegram bot token from @BotFather\n\n"
            "For more information about the kernel builder workflow, "
            "visit: https://github.com/zyexro/kernel_builder"
        )
        await update.message.reply_text(help_message, parse_mode='Markdown')
    
    async def build_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start the build configuration process."""
        user_id = update.effective_user.id
        context.user_data['build_config'] = DEFAULT_VALUES.copy()
        context.user_data['build_config']['user_id'] = user_id
        
        message = (
            "🔧 *Starting Kernel Build Configuration*\n\n"
            "I'll guide you through setting up your kernel build. "
            "You can use default values or customize them.\n\n"
            f"**Compiler** (current: `{DEFAULT_VALUES['COMPILER']}`)\n"
            "Enter the compiler to use, or send 'default' to use the current value:"
        )
        await update.message.reply_text(message, parse_mode='Markdown')
        return COMPILER
    
    async def get_compiler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Get compiler input."""
        text = update.message.text.strip()
        if text.lower() != 'default':
            context.user_data['build_config']['COMPILER'] = text
        
        message = (
            f"✅ Compiler: `{context.user_data['build_config']['COMPILER']}`\n\n"
            f"**Kernel Repository** (current: `{context.user_data['build_config']['KREPO']}`)\n"
            "Enter the kernel repository URL, or send 'default':"
        )
        await update.message.reply_text(message, parse_mode='Markdown')
        return KREPO
    
    async def get_krepo(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Get kernel repository input."""
        text = update.message.text.strip()
        if text.lower() != 'default':
            context.user_data['build_config']['KREPO'] = text
        
        message = (
            f"✅ Repository: `{context.user_data['build_config']['KREPO']}`\n\n"
            f"**Kernel Branch** (current: `{context.user_data['build_config']['KBRANCH']}`)\n"
            "Enter the kernel branch, or send 'default':"
        )
        await update.message.reply_text(message, parse_mode='Markdown')
        return KBRANCH
    
    async def get_kbranch(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Get kernel branch input."""
        text = update.message.text.strip()
        if text.lower() != 'default':
            context.user_data['build_config']['KBRANCH'] = text
        
        message = (
            f"✅ Branch: `{context.user_data['build_config']['KBRANCH']}`\n\n"
            f"**Container Image** (current: `{context.user_data['build_config']['CONTAINER']}`)\n"
            "Enter the container image, or send 'default':"
        )
        await update.message.reply_text(message, parse_mode='Markdown')
        return CONTAINER
    
    async def get_container(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Get container input."""
        text = update.message.text.strip()
        if text.lower() != 'default':
            context.user_data['build_config']['CONTAINER'] = text
        
        message = (
            f"✅ Container: `{context.user_data['build_config']['CONTAINER']}`\n\n"
            "**Optional Parameters**\n"
            "You can configure additional optional parameters or skip to confirmation.\n\n"
            "**Notes** (optional build notes)\n"
            "Enter notes for this build, or send 'skip':"
        )
        await update.message.reply_text(message, parse_mode='Markdown')
        return NOTES
    
    async def get_notes(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Get notes input."""
        text = update.message.text.strip()
        if text.lower() != 'skip':
            context.user_data['build_config']['NOTES'] = text
        
        message = (
            "**KernelSU Patching** (optional)\n"
            "Options:\n"
            "• `both` - Build without and with KernelSU\n"
            "• `sus` - Apply KernelSU and SuSFS patches\n"
            "• `ksu` - Apply only KernelSU patches\n"
            "• `skip` - No KernelSU patching\n\n"
            "Enter your choice:"
        )
        await update.message.reply_text(message, parse_mode='Markdown')
        return KSU
    
    async def get_ksu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Get KSU input."""
        text = update.message.text.strip()
        if text.lower() not in ['skip', '']:
            context.user_data['build_config']['KSU'] = text
        
        # Show confirmation
        config = context.user_data['build_config']
        confirmation_message = (
            "🔍 *Build Configuration Summary*\n\n"
            f"**Compiler:** `{config['COMPILER']}`\n"
            f"**Repository:** `{config['KREPO']}`\n"
            f"**Branch:** `{config['KBRANCH']}`\n"
            f"**Container:** `{config['CONTAINER']}`\n"
            f"**Notes:** `{config['NOTES'] or 'None'}`\n"
            f"**KernelSU:** `{config['KSU'] or 'None'}`\n\n"
            "Is this configuration correct?"
        )
        
        keyboard = [
            [InlineKeyboardButton("✅ Confirm & Start Build", callback_data="confirm_build")],
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel_build")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            confirmation_message, 
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        return CONFIRM
    
    async def handle_confirmation(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle build confirmation."""
        query = update.callback_query
        await query.answer()
        
        if query.data == "confirm_build":
            # Trigger the GitHub Actions workflow
            success, message = await self.trigger_github_workflow(context.user_data['build_config'])
            
            if success:
                await query.edit_message_text(
                    f"🚀 *Build Started Successfully!*\n\n{message}",
                    parse_mode='Markdown'
                )
                # Store build info for status tracking
                user_id = context.user_data['build_config']['user_id']
                self.active_builds[user_id] = {
                    'config': context.user_data['build_config'],
                    'started_at': datetime.now(),
                    'status': 'running'
                }
            else:
                await query.edit_message_text(
                    f"❌ *Build Failed to Start*\n\n{message}",
                    parse_mode='Markdown'
                )
        else:
            await query.edit_message_text("❌ Build cancelled.")
        
        return ConversationHandler.END
    
    async def trigger_github_workflow(self, config: Dict[str, Any]) -> tuple[bool, str]:
        """Trigger the GitHub Actions workflow."""
        url = f"{self.github_api_base}/repos/{GITHUB_OWNER}/{GITHUB_REPO}/actions/workflows/{GITHUB_WORKFLOW}/dispatches"
        
        headers = {
            'Authorization': f'token {GITHUB_TOKEN}',
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json'
        }
        
        # Prepare workflow inputs
        inputs = {
            'COMPILER': config['COMPILER'],
            'KREPO': config['KREPO'],
            'KBRANCH': config['KBRANCH'],
            'CONTAINER': config['CONTAINER']
        }
        
        # Add optional parameters if they exist
        if config['NOTES']:
            inputs['NOTES'] = config['NOTES']
        if config['KSU']:
            inputs['KSU'] = config['KSU']
        if config['SUFFIX']:
            inputs['SUFFIX'] = config['SUFFIX']
        if config['ZREPO']:
            inputs['ZREPO'] = config['ZREPO']
        if config['ZBRANCH']:
            inputs['ZBRANCH'] = config['ZBRANCH']
        if TELEGRAM_CHAT_ID:
            inputs['TG_RECIPIENT'] = TELEGRAM_CHAT_ID
        
        payload = {
            'ref': 'enanan',  # Use the enanan branch as seen in the repository
            'inputs': inputs
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 204:
                # Get the latest workflow run
                runs_url = f"{self.github_api_base}/repos/{GITHUB_OWNER}/{GITHUB_REPO}/actions/runs"
                runs_response = requests.get(runs_url, headers=headers)
                
                if runs_response.status_code == 200:
                    runs_data = runs_response.json()
                    if runs_data['workflow_runs']:
                        latest_run = runs_data['workflow_runs'][0]
                        run_url = latest_run['html_url']
                        return True, f"Monitor your build progress at:\n{run_url}"
                
                return True, "Workflow triggered successfully! Check the Actions tab in the GitHub repository."
            else:
                return False, f"GitHub API error: {response.status_code} - {response.text}"
                
        except Exception as e:
            return False, f"Error triggering workflow: {str(e)}"
    
    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Check build status."""
        user_id = update.effective_user.id
        
        if user_id not in self.active_builds:
            await update.message.reply_text(
                "❌ No active builds found. Use `/build` to start a new build.",
                parse_mode='Markdown'
            )
            return
        
        build_info = self.active_builds[user_id]
        started_at = build_info['started_at'].strftime('%Y-%m-%d %H:%M:%S UTC')
        
        # Get latest workflow runs from GitHub
        url = f"{self.github_api_base}/repos/{GITHUB_OWNER}/{GITHUB_REPO}/actions/runs"
        headers = {
            'Authorization': f'token {GITHUB_TOKEN}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                runs_data = response.json()
                if runs_data['workflow_runs']:
                    latest_run = runs_data['workflow_runs'][0]
                    status = latest_run['status']
                    conclusion = latest_run['conclusion']
                    run_url = latest_run['html_url']
                    
                    status_message = (
                        f"📊 *Build Status*\n\n"
                        f"**Started:** {started_at}\n"
                        f"**Status:** {status.title()}\n"
                        f"**Conclusion:** {conclusion.title() if conclusion else 'In Progress'}\n\n"
                        f"[View on GitHub]({run_url})"
                    )
                else:
                    status_message = "❌ No workflow runs found."
            else:
                status_message = f"❌ Error fetching status: {response.status_code}"
                
        except Exception as e:
            status_message = f"❌ Error checking status: {str(e)}"
        
        await update.message.reply_text(status_message, parse_mode='Markdown')
    
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancel the conversation."""
        await update.message.reply_text("❌ Build configuration cancelled.")
        return ConversationHandler.END
    
    def run(self):
        """Run the bot."""
        if not TELEGRAM_BOT_TOKEN:
            logger.error("TELEGRAM_BOT_TOKEN not found in environment variables")
            return
        
        if not GITHUB_TOKEN:
            logger.error("GITHUB_TOKEN not found in environment variables")
            return
        
        # Create the Application
        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        
        # Add conversation handler for build process
        build_conv_handler = ConversationHandler(
            entry_points=[CommandHandler('build', self.build_start)],
            states={
                COMPILER: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_compiler)],
                KREPO: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_krepo)],
                KBRANCH: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_kbranch)],
                CONTAINER: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_container)],
                NOTES: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_notes)],
                KSU: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_ksu)],
                CONFIRM: [CallbackQueryHandler(self.handle_confirmation)]
            },
            fallbacks=[CommandHandler('cancel', self.cancel)]
        )
        
        # Add handlers
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("status", self.status))
        application.add_handler(build_conv_handler)
        
        # Start the bot
        logger.info("Starting Kernel Builder Bot...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)

def main():
    """Main function."""
    bot = KernelBuilderBot()
    bot.run()

if __name__ == '__main__':
    main()

