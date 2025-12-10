![license: GPLv3](https://img.shields.io/badge/License-GPLv3-blue.svg)
![Status: Alpha](https://img.shields.io/badge/status-alpha-yellow)
![platform-windows](https://img.shields.io/badge/platform-windows-blue)

# Zorya Seraph Interface
**Version 0.5.0 Alpha**

A voice-enabled AI assistant with personality, mood tracking, and autonomous learning capabilities.

---

## Table of Contents
- [Overview](#overview)
- [Key Features](#key-features)
- [Requirements](#requirements)
- [Usage](#usage)
- [Architecture](#architecture)
- [How It Works](#how-it-works)
- [Configuration](#configuration)
- [Logging & Debugging](#logging--debugging)
- [Known Limitations](#known-limitations)
- [Development Notes](#development-notes)
- [Version History](#version-history)
- [Contributing](#contributing)
- [License](#license)
- [Author](#author)

---

## Overview

Zorya is an intelligent command-line interface assistant that combines natural language processing, voice responses, and adaptive learning. She features a dynamic mood system, learns from user interactions, and can autonomously manage programs and routines.

---

## Key Features

### Core Capabilities
- **Natural Language Understanding**: Token-based intent recognition system with expandable vocabulary
- **Voice Responses**: Context-aware audio playback with 140+ voice lines across multiple categories
- **Mood Engine**: Dynamic emotional state tracking that responds to interactions and events
- **Autonomous Learning**: Automatically learns frequently used applications and suggests routines
- **Memory Management**: Persistent storage of vocabulary, intents, program paths, and user preferences
- **Pattern Recognition**: Tracks application usage and identifies patterns for optimization
- **SSH Profile Management**: Store and manage remote connection profiles via PuTTY
- **Routine Builder**: Create custom command sequences and automation workflows
- **Batch Script Execution**: Build and execute custom batch files
- **System Control**: Launch programs, open folders, and execute system commands

### Personality Features
- Sassy and sarcastic responses
- Context-aware reactions (greetings, errors, jokes, alerts)
- Mood-based dialogue selection
- Failed/successful shutdown detection and response
- User interaction tracking with emotional feedback

---

## Requirements

### System Requirements
- **OS**: Windows (uses Windows-specific APIs)
- **Python**: 3.7 or higher
- **RAM**: Minimal (typically <50MB)

### Python Dependencies
- `psutil` - Process and system monitoring
- `pygame` - Audio playback (auto-installed on first run)
- `tkinter` - File/folder selection dialogs (usually included with Python)

### Installation

1. **Install Python**:
   - Press `Win + R`, type `cmd`, press Enter
   - Type `python` and press Enter
   - Windows Store will open - click Install
   - Double-click install_dependencies.bat before first run, or Zorya wont work.

2. **Run Zorya**:
   - Double-click `Zorya.bat` in the project root

---

## Usage

### Starting Zorya
```batch
Zorya.bat
```

### Basic Commands
Zorya uses natural language processing. Examples:

- **Opening Programs**: "open chrome", "launch discord"
- **System Control**: "shutdown", "close program"
- **Information**: "what time is it", "status report", "tell me a joke"
- **Configuration**: "set new program", "set folder path", "save new word"
- **Routines**: "build routine", "execute batch script"
- **Mood**: "how are you feeling"

**Important**: Always include "Zorya" in your goodbye commands (e.g., "goodbye Zorya") for proper shutdown.

---

## Architecture

### Project Structure
```
Zorya_Seraph_interface/
├── Zorya.py                    # Main application loop
├── Zorya.bat                   # Windows launcher
├── Data/
│   ├── Audio_lines/            # 140+ voice response files
│   ├── Long_term_memory/       # Persistent JSON storage
│   │   ├── audio_dictionary.json
│   │   ├── intent_map.json
│   │   ├── known_vocabulary.json
│   │   ├── program_path.json
│   │   ├── folder_path.json
│   │   ├── routine_buffer.json
│   │   └── flag_dictionary.json
│   ├── Logs/                   # System logs
│   ├── Built_Batches/          # Custom batch scripts
│   └── [modules].py            # Core functionality modules
```

### Core Modules

| Module | Purpose |
|--------|---------|
| `interpretation_engine.py` | Tokenization, intent matching, vocabulary management |
| `audio_play_module.py` | Voice line playback and audio management |
| `mood_engine_module.py` | Emotional state tracking and mood alterations |
| `system_control_module.py` | Program launching, path management |
| `pattern_recognition_module.py` | Application usage tracking and analysis |
| `autonomus_actions_module.py` | Routine suggestions and autonomous behaviors |
| `routine_builder_module.py` | Custom routine creation and management |
| `memory_flags_loader.py` | Persistent flag and configuration management |
| `log_handler.py` | Logging and session tracking |
| `putty_manager_module.py` | SSH profile management |
| `batch_builder.py` | Batch script generation |
| `command_runner.py` | System command execution |

---

## How It Works

### Intent Recognition System
1. User input is tokenized using vocabulary dictionary
2. Tokens are matched against intent map patterns
3. Best matching intent triggers associated action
4. Unrecognized patterns can be taught as new routines

### Mood System
Zorya maintains three mood states (happy, neutral, sad) that shift based on:
- Successful/failed command interpretation
- User interaction frequency
- Proper/improper shutdown
- Learning new vocabulary or intents
- Being silenced/unsilenced

### Autonomous Learning
- Tracks frequently used applications
- Suggests routine creation for repeated patterns
- Auto-discovers program paths for running applications
- Degrades unused application scores over time

### Memory Backup
- Automatic backup to `%APPDATA%\Zorya\Memory_backup\`
- Restore capability for configuration recovery
- Session-based tracking with hexadecimal IDs

---

## Configuration

### Adding New Programs
```
You: "set new program"
Zorya: "Tell me the name of the program..."
[Follow prompts to select executable]
```

### Teaching New Vocabulary
```
You: "set a new word"
[Zorya will guide you through category selection]
```

### Building Custom Routines
Use the routine builder module to create multi-step automation sequences.

---

## Logging & Debugging

- **Log Location**: `Data/Logs/general_system_log.txt`
- **Session IDs**: Hexadecimal format (e.g., $1A3F)
- **Log Rotation**: Auto-cleans at 15,000 lines
- **Debug Mode**: Available via debug module commands

### Viewing Recent Logs
```
You: "show recent logs"
```

---

## Known Limitations

- Windows-only (uses `os.startfile`, `taskkill`, etc.)
- Requires explicit "Zorya" mention in shutdown commands
- Intent recognition requires exact token matches
- Audio playback requires pygame library
- File dialogs may appear behind other windows

---

## Development Notes

### Testing
Run unit tests:
```bash
python unitary_tests.py
```

### Extending Functionality
1. Add new intents to `intent_map.json`
2. Expand vocabulary in `known_vocabulary.json`
3. Create new modules following existing patterns
4. Update audio responses in `Audio_lines/`

---

## Version History

**v0.5.0 Alpha** (Current)
- Full mood engine implementation
- Autonomous learning system
- Pattern recognition for app usage
- SSH profile management
- Routine builder functionality
- Memory backup/restore
- Enhanced logging system

---

## Contributing

When testing, please:
1. Monitor `general_system_log.txt` for errors
2. Note any unrecognized commands
3. Report mood system anomalies
4. Share your session logs for analysis

---

## License

Zorya Serapth Interface - Copyright (C) 2025 Mendoukusai ByteLabs

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.


---

## Author

Made By Masked Musketeer under the Mendoukusai ByteLabs brand
github: github.com/MasquedMusketeer
contact email: Mendoukusai.ByteLabs@outlook.com

---

**Note**: Zorya is in active alpha development. Features and behaviors may change. Always backup your `Long_term_memory` folder before major updates.
