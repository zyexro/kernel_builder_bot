# Kernel Builder Telegram Bot

A Telegram bot that allows users to trigger kernel builds using the GitHub Actions workflow from the [zyexro/kernel_builder](https://github.com/zyexro/kernel_builder) repository.

## Features

- 🔧 **Easy Build Configuration**: Step-by-step guided setup for kernel builds
- 🚀 **GitHub Actions Integration**: Directly triggers workflows via GitHub API
- 📊 **Build Status Tracking**: Monitor your build progress
- 🛡️ **Secure**: Uses environment variables for sensitive tokens
- 💬 **User-Friendly**: Interactive Telegram interface with inline keyboards

## Prerequisites

1. **Telegram Bot Token**: Create a bot using [@BotFather](https://t.me/BotFather)
2. **GitHub Personal Access Token**: Generate a token with `repo` scope from [GitHub Settings](https://github.com/settings/tokens)
3. **Python 3.8+**: Required for running the bot

## Installation

1. **Clone or download this bot code**:
   ```bash
   # If you have the files, navigate to the directory
   cd kernel_builder_bot
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your actual tokens and settings
   ```

4. **Edit the `.env` file** with your configuration:
   ```env
   TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
   GITHUB_TOKEN=your_github_personal_access_token
   GITHUB_OWNER=zyexro
   GITHUB_REPO=kernel_builder
   GITHUB_WORKFLOW=main.yml
   TELEGRAM_CHAT_ID=optional_chat_id_for_build_updates
   ```

## Usage

### Starting the Bot

```bash
python bot.py
```

### Bot Commands

- `/start` - Welcome message and bot overview
- `/build` - Start a new kernel build configuration
- `/status` - Check the status of your last build
- `/help` - Show help information

### Build Process

1. **Start a build**: Send `/build` to the bot
2. **Configure parameters**: The bot will guide you through setting:
   - Compiler (e.g., `Geopelia-Clang-20`)
   - Kernel repository URL
   - Kernel branch
   - Container image
   - Optional: Build notes, KernelSU options
3. **Confirm settings**: Review and confirm your configuration
4. **Monitor progress**: The bot provides a GitHub Actions link to track your build

### Build Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| **COMPILER** | Compiler to use for building | `Geopelia-Clang-20` |
| **KREPO** | Kernel repository URL | `https://github.com/TelegramAt25/niigo_kernel_xiaomi_blossom` |
| **KBRANCH** | Kernel branch to build | `yoka` |
| **CONTAINER** | Docker container for build environment | `fedora:40` |
| **NOTES** | Optional build notes | _(empty)_ |
| **KSU** | KernelSU patching options | _(empty)_ |

### KernelSU Options

- `both` - Build without and with KernelSU
- `sus` - Apply KernelSU and SuSFS patches
- `ksu` - Apply only KernelSU patches
- _(empty)_ - No KernelSU patching

## Configuration Details

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | ✅ | Bot token from @BotFather |
| `GITHUB_TOKEN` | ✅ | GitHub Personal Access Token with `repo` scope |
| `GITHUB_OWNER` | ❌ | Repository owner (default: `zyexro`) |
| `GITHUB_REPO` | ❌ | Repository name (default: `kernel_builder`) |
| `GITHUB_WORKFLOW` | ❌ | Workflow file name (default: `main.yml`) |
| `TELEGRAM_CHAT_ID` | ❌ | Chat ID for receiving build updates |

### GitHub Token Permissions

Your GitHub Personal Access Token needs the following scopes:
- `repo` - Full control of private repositories
- `workflow` - Update GitHub Action workflows

## Deployment

### Local Development
```bash
python bot.py
```

### Production Deployment

1. **Using systemd** (Linux):
   ```bash
   # Create a service file
   sudo nano /etc/systemd/system/kernel-builder-bot.service
   ```

   ```ini
   [Unit]
   Description=Kernel Builder Telegram Bot
   After=network.target

   [Service]
   Type=simple
   User=your_user
   WorkingDirectory=/path/to/kernel_builder_bot
   ExecStart=/usr/bin/python3 bot.py
   Restart=always
   RestartSec=10
   Environment=PATH=/usr/bin:/usr/local/bin
   EnvironmentFile=/path/to/kernel_builder_bot/.env

   [Install]
   WantedBy=multi-user.target
   ```

   ```bash
   sudo systemctl enable kernel-builder-bot
   sudo systemctl start kernel-builder-bot
   ```

2. **Using Docker**:
   ```dockerfile
   FROM python:3.11-slim

   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt

   COPY . .
   CMD ["python", "bot.py"]
   ```

   ```bash
   docker build -t kernel-builder-bot .
   docker run -d --env-file .env kernel-builder-bot
   ```

## Troubleshooting

### Common Issues

1. **Bot not responding**:
   - Check if `TELEGRAM_BOT_TOKEN` is correct
   - Ensure the bot is started with `/start` command

2. **GitHub workflow not triggering**:
   - Verify `GITHUB_TOKEN` has correct permissions
   - Check if repository and workflow file exist
   - Ensure the token belongs to a user with access to the repository

3. **Build status not updating**:
   - GitHub API rate limits may apply
   - Check if the workflow is actually running in the GitHub repository

### Logs

The bot logs important events to the console. For production, consider redirecting logs to a file:

```bash
python bot.py >> bot.log 2>&1
```

## Security Considerations

- **Never commit `.env` file** to version control
- **Use environment variables** for all sensitive data
- **Regularly rotate** your GitHub Personal Access Token
- **Limit bot access** to trusted users if needed

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source. Please check the original [kernel_builder repository](https://github.com/zyexro/kernel_builder) for license information.

## Support

For issues related to:
- **Bot functionality**: Create an issue in this repository
- **Kernel building**: Check the [original kernel_builder repository](https://github.com/zyexro/kernel_builder)
- **Telegram Bot API**: Refer to [Telegram Bot API documentation](https://core.telegram.org/bots/api)

