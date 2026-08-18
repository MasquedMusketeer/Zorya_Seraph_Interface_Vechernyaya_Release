![license: GPLv3](https://img.shields.io/badge/License-GPLv3-blue.svg)
![Status: Beta](https://img.shields.io/badge/status-beta-yellow)
![platform-windows](https://img.shields.io/badge/platform-windows-blue)

# Zorya vigil Protocol | Designation: M.I.D.A.S.
   Mood-Intent Daemon & Autonomous Scheduler
**Version 0.6.9 Beta**

A voice-enabled AI assistant with personality, mood tracking, autonomous learning capabilities,
real-time self system monitoring dashboard, and task scheduling with automated reminders.

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

Zorya is an intelligent command-line interface assistant that combines natural language processing,
voice responses, and adaptive learning. She features a dynamic mood system, learns from user interactions,
and can autonomously manage programs and routines.
The system includes a real-time status dashboard displaying session information, mood states, and system alerts.

---

## Key Features

### Core Capabilities
- **Natural Language Understanding**: Token-based intent recognition system with expandable vocabulary
- **Voice Responses**: Context-aware audio playback with 150+ voice lines across multiple categories
- **Mood Engine**: Dynamic emotional state tracking that responds to interactions and events
- **Autonomous Learning**: Automatically learns frequently used applications and suggests routines
- **Memory Management**: Persistent storage of vocabulary, intents, program paths, and user preferences
- **Pattern Recognition**: Tracks application usage and identifies patterns for optimization
- **Real-Time Dashboard**: Tkinter-based status display showing session info, mood, tracked apps, and system alerts
- **Routine Builder**: Create and correct custom command sequences and automation workflows
- **Batch Script Execution**: Build and execute custom batch files
- **Task Scheduler**: Create, manage, and track scheduled tasks with automated reminders and repeat options
- **System Control**: Launch programs via async queue, open folders, execute system commands, and monitor startup applications
- **Resource Monitoring**: Real-time CPU, RAM, disk, network, trash bin, and downloads folder monitoring with configurable alerts
- **Windows Notifications**: Toast notifications for system errors and resource alerts
- **Data Sanitization**: Startup self-healing pass that removes stale program paths, memory entries, and orphaned intents
- **MQTT Integration**: Heartbeat listener and message manager for external API connectivity monitoring (in development)

### Personality Features
- Sassy and sarcastic responses
- Context-aware reactions (greetings, errors, jokes, alerts, banter)
- Mood-based dialogue selection
- Failed/successful shutdown detection and response
- User interaction tracking with emotional feedback
- Autonomous banter system (fires randomly every 30-60 minutes)

### API Integration
- Command queue system for external interface integration
- Returns structured intent, response category/index, and mood state per command
- Enables GUI or web interface development
- Separate API startup sequence with dedicated command processor thread

---

## Requirements

### System Requirements
- **OS**: Windows (uses Windows-specific APIs)
- **Python**: 3.7 or higher
- **RAM**: Minimal (typically <50MB)

### Python Dependencies
- `psutil` - Process and system monitoring
- `pygame` - Audio playback
- `winotify` - Windows toast notifications
- `pywin32` - Windows API access (win32gui, win32process)
- `paho-mqtt` - MQTT client for external API communication
- `tkinter` - GUI components and dashboard (usually included with Python)

### Installation

1. **Install Dependencies**:
   - Double-click `install_dependencies.bat` before first run
   - This will automatically install Python (if needed) and all required packages
   - Restart the script if Python was just installed

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

- **Opening Programs**: "open chrome", "launch discord", "open spotify"
- **Opening Folders**: "open documents", "open downloads"
- **System Control**: "shutdown", "close program", "kill program"
- **Information**: "what time is it", "status report", "show recent logs", "how many intents"
- **Configuration**: "set new program", "set folder path", "save new word", "set startup app", "delete startup app"
- **Routines**: "build routine", "correct routine", "execute batch script"
- **Task Scheduling**: "add schedule", "remove schedule"
- **Mood**: "how are you today"
- **System**: "backup memory", "restore backup", "change alert parameter"
- **Debug**: Invoke system override via debug vocabulary (refer to intent map)

**Important**: Always include "Zorya" in your goodbye commands (e.g., "goodbye Zorya") for proper shutdown.

---

## Architecture

### Architecture Philosophy

Zorya is designed with explicit state transitions and deterministic flow.
Each module acts as a functional unit with clear inputs/outputs.
Extensive logging provides runtime execution traces.

This design prioritizes:
- Debuggability over abstraction
- Explicit state over implicit behavior
- Observable flow over clever code


### Project Structure
```
Zorya_Seraph_interface/
├── Zorya.py                    # Main application loop and entry point
├── Zorya.bat                   # Windows launcher
├── install_dependencies.bat    # Dependency installer
├── unitary_tests.py            # Unit test suite
├── Data/
│   ├── Audio_lines/            # 150+ voice response MP3 files
│   ├── sprites/                # Visual assets for future GUI
│   ├── icon/                   # Application icons
│   ├── Long_term_memory/       # Persistent JSON storage
│   │   ├── response_library.json      # Unified response data (text, audio, line mood)
│   │   ├── intent_map.json            # All known intents and their dispatch contracts
│   │   ├── known_vocabulary.json      # Tokenization vocabulary
│   │   ├── program_path.json          # Permanent program executable paths
│   │   ├── program_path_temp.json     # Auto-discovered program paths (staging)
│   │   ├── folder_path.json           # Registered folder paths
│   │   ├── routine_buffer.json        # Short-term intent staging buffer
│   │   ├── schedule_library.json      # Task scheduler entries
│   │   ├── flag_dictionary.json       # All runtime flags and configuration
│   │   └── app_white_grey_blacklist.json  # App classification lists
│   ├── Logs/                   # System logs
│   ├── Built_Batches/          # Custom batch scripts
│   └── [modules].py            # Core functionality modules (21 total)
```

### Core Modules (21 modules)
___________________________________________________________________________________________
| Module                           | Purpose                                              |
|----------------------------------|------------------------------------------------------|
| `interpretation_engine.py`       | Tokenization, intent matching, vocabulary management |
| `response_handler.py`            | Unified response management (text, audio, mood)      |
| `audio_play_module.py`           | Audio file playback engine                           |
| `text_processing_module.py`      | Text formatting and header display                   |
| `mood_engine_module.py`          | Emotional state tracking and mood alterations        |
| `system_control_module.py`       | Program/folder launching, path management            |
| `pattern_recognition_module.py`  | Application usage tracking and analysis              |
| `autonomus_actions_module.py`    | Routine suggestions, resource alerts, banter         |
| `routine_builder_module.py`      | Custom routine creation, correction, and management  |
| `task_scheduler_module.py`       | Task scheduling with reminders and repeat options    |
| `memory_flags_loader.py`         | Thread-safe flag and configuration management        |
| `log_handler.py`                 | Logging, session tracking, and toast notifications   |
| `batch_builder.py`               | Batch script generation                              |
| `command_runner.py`              | System command and ping execution                    |
| `system_watcher_module.py`       | Real-time system resource monitoring                 |
| `debug_module.py`                | Debug utilities and arbitrary function execution     |
| `backup_manager_module.py`       | Memory backup and restore via robocopy               |
| `bootstrapper.py`                | Asset loading, startup health check, sanitization    |
| `self_info_report_module.py`     | Status reporting and system information              |
| `status_dashboard_module.py`     | Real-time Tkinter dashboard display                  |
| `mqtt_manager_module.py`         | MQTT client, heartbeat monitoring (in development)   |
|----------------------------------|------------------------------------------------------|

### Threading Architecture

Zorya uses multiple daemon threads for concurrent operations:

**System Reader Threads:**
- `update_frequently_used_apps` - Tracks application usage patterns (every 5 min)
- `self_user_tracking_decrement_thread` - Degrades mood based on lack of interaction (every 2 hours)
- `watch_resource_high_usage` - Monitors CPU, RAM, disk, network, trash, and downloads (every 10 sec)
- `launch_dashboard` - Runs the real-time status dashboard (refreshes every 30 sec)
- `degrade_joke_counter` - Degrades joke saturation counter over time (every 5 min)

**System Writer Threads:**
- `system_info_updater` - Updates system resource state (every 10 sec)
- `periodic_save_ram_flags_to_disk` - Flushes flags to disk (every 5 min)

**System Execution Threads:**
- `kill_unwanted_running_apps` - Manages blacklisted applications (every 60 sec)
- `autonomus_banter_handler` - Generates autonomous personality responses (every 30-60 min)
- `notify_due_schedules` - Checks and fires schedule notifications (every hour)
- `run_program_from_queue` - Dequeues and launches programs asynchronously (every 5 sec)

**API Mode Threads:**
- `_api_command_processor` - Processes commands from external interfaces via queue

**MQTT Threads (in development):**
- `mqtt_heartbeat_listener` - Monitors external API connection status via heartbeat topic

All threads use a shared `stop_event` for graceful shutdown coordination.

### Memory Architecture

**Load-Once Pattern:**
```
Startup:
  Load all JSONs → RAM (bootstrapper)
  Run sanitization pass (stale paths, memory entries, intents)

Runtime:
  All operations on RAM dicts (fast, thread-safe with locks)

Every 5 min:
  Flush state flags to disk (mfl.save_ram_flags)

Shutdown:
  Save everything, sanitize schedule library (clean exit)
```

**Thread Safety:**
- `memory_flags_loader` uses a single lock (`_flag_lock`) for all flag operations
- Deep copy on reads prevents external mutation
- `system_watcher_module` uses a dedicated lock for system info updates
- `log_handler` uses a write lock for log file access
- Other JSONs are read-once at startup (no contention)
- Response library loaded once, read-only during runtime

---

## How It Works

### Startup Sequence (bootstrapper)
On every startup, the bootstrapper runs a full health check in order:
1. Load all JSON assets into RAM
2. Set session ID (hexadecimal, incremented each session)
3. Count log lines and flag for cleanup if needed
4. **Sanitization pass**:
   - Remove stale program paths (executables that no longer exist on disk)
   - Remove stale memory entries (silenced, startup apps referencing deleted programs)
   - Remove stale program intents (intents pointing to deleted programs, identified by `call_program` action)
5. Report startup errors - critical errors abort execution, non-critical errors are logged

### Response System

Zorya uses a unified response library (`response_library.json`) that combines:
- Text dialogue
- Audio file references
- Mood scores for selection

**Structure:**
```json
{
  "GREETING": {
    "10": {
      "text": "Good morning!",
      "audio_file": "GREETING_10.mp3",
      "mood_score": 2
    }
  }
}
```

**Selection Flow:**
1. Category requested (e.g., "GREETING")
2. Filter out last-used line (prevent repetition)
3. For mood-based categories: calculate compressed mood score
4. Select random line matching mood score
5. For exception categories (BANTER, SASS, etc.): random selection
6. Return text + audio file

### Intent Recognition System
1. User input is tokenized using vocabulary dictionary
2. Tokens are matched against intent map patterns (prefix-based matching)
3. Best matching intent triggers associated action (module + function + parameters)
4. Unrecognized patterns can be taught as new routines via routine builder
5. Failed interpretations affect mood state negatively

### Mood System
Zorya maintains three mood states (happy, neutral, sad) that shift based on:
- Successful/failed command interpretation
- User interaction frequency
- Proper/improper shutdown
- Learning new vocabulary or intents
- Being silenced/unsilenced
- Telling jokes
- System errors
- Completing useful actions (usefulness score accumulates, raises mood every 4 useful actions)

**Mood Calculation:**
```python
# Compressed score: (happy * 1.5) + neutral + (sad * 0.5)
# Range: 1.0 (very sad) to 3.0 (very happy)
# Stochastic selection picks between floor and ceil based on decimal
```

Mood influences dialogue selection for categories like GREETING, BYE, and ERROR.
Exception categories (BANTER, SASS, JOKE) use random selection regardless of mood.

### Autonomous Learning
- Tracks frequently used applications with a scoring system
- Suggests routine creation for repeated patterns (configurable threshold)
- Auto-discovers program paths for running applications
- Degrades unused application scores over time (every 15 minutes, every 3 cycles)
- Apps already mapped to intents are automatically moved to silenced list
- Maintains white/grey/blacklist for application management
- Ignored apps are permanently excluded from tracking and sanitization

### Data Sanitization
Runs automatically at every startup via bootstrapper:
- **Path sanitization** (`system_control_module`): Checks all known program paths against disk, removes entries where the executable no longer exists
- **Memory sanitization** (`memory_flags_loader`): Removes deleted programs from `silenced_apps`, and `apps_expected_at_start`
- **Intent sanitization** (`interpretation_engine`): Removes `INTENT_OPEN_*` intents whose `call_program` parameter no longer exists in known programs

### Status Dashboard
Real-time Tkinter window displaying:
- Current session ID (hexadecimal format)
- Last backup session ID
- Startup errors count
- Execution mode (CLI/API)
- Current mood state with score
- Startup applications list
- Tracked applications with usage scores
- System alert thresholds and mute status per resource
- Auto-refreshes every 30 seconds

### Routine Builder
Interactive CLI tool for creating and managing custom intents:
- Tokenizes user-provided command phrases automatically
- Suggests similar existing intents as templates
- Supports correction and deletion of existing folder/program/other intents
- Cleanup on correction removes associated vocabulary and path entries
- New routines are staged in `routine_buffer.json` and committed to `intent_map.json` on shutdown

### Task Scheduler
Create and manage scheduled tasks with automated reminders:
- Add tasks with name, description, category, and due date
- Repeat options: none, daily, weekly, monthly, yearly
- Configurable reminder threshold (days in advance)
- Custom notification time (HH:MM:SS format)
- Automatic status tracking (waiting → due → completed)
- Popup notifications at specified times
- Auto-cleanup of completed non-repeating tasks on shutdown
- Persistent storage in `schedule_library.json`

### Resource Monitoring
Continuous background monitoring with smart alerting:
- CPU alerts require sustained high usage (>6 ticks at 10 sec intervals) before firing
- RAM alerts use the same sustained threshold to avoid false positives
- Disk alerts fire immediately per-drive and reset when usage drops
- Trash bin alerts fire every 2 hours if size exceeds configured threshold; above 10GB triggers a voice line instead
- Downloads folder alerts fire once when file count exceeds configured threshold, reset when it drops
- All alerts respect per-resource mute flags and are dispatched via a notification queue
- Resource usage logged every 90 ticks (~15 minutes)

### Memory Backup
- Manual backup to `%APPDATA%\Zorya\Memory_backup\` via command
- Uses `robocopy` for reliable file transfer
- Restore capability for configuration recovery
- Session-based tracking with hexadecimal IDs (e.g., $128)
- Backup/restore flags are set at command time and executed at shutdown

### MQTT Integration (In Development)
- Connects to local MQTT broker on startup
- Subscribes to `zorya/heartbeat` and `zorya/whatsapp_messenger`
- Heartbeat listener monitors API status: `up_ok`, `up_relogin`, `up_navclosed`, or `down` (10 min timeout)
- Status changes trigger desktop notifications
- Designed to run as a daemon thread from main startup sequence

---

## Configuration

### Adding New Responses
Edit `response_library.json`:
```json
"GREETING": {
  "99": {
    "text": "Your new greeting here",
    "audio_file": "GREETING_99.mp3",
    "mood_score": 2
  }
}
```
Place audio file in `Data/Audio_lines/` and restart Zorya.

### Adding New Programs
```
You: "set new program"
Zorya: "Tell me the name of the program..."
[Follow prompts to select executable]
```

### Setting Startup Applications
```
You: "set startup app"
[Enter program name - will auto-register if not found]
```

### Teaching New Vocabulary
```
You: "set a new word"
[Zorya will guide you through category selection]
```

### Building Custom Routines
```
You: "build routine"
[Zorya will guide you through naming, command phrase, and module/function selection]
```

### Correcting or Deleting Routines
```
You: "correct routine"
[Choose type: folder, program, or other - then correct or delete]
```

### Configuring System Alerts
```
You: "change alert parameter"
[Choose value limit or mute/unmute, then select cpu/ram/disk/trash/download]
```

### Dashboard Styling
Dashboard appearance is configured via `dashboard_config` in `flag_dictionary.json`:
- Background color
- Font types and sizes
- Title, label, and footer colors
- Subtext sizing

---

## Logging & Debugging

- **Log Location**: `Data/Logs/general_system_log.txt`
- **Log Format**: `[timestamp] [sessionID] [module] [action] [details]`
- **Session IDs**: Hexadecimal format (e.g., $1A3F), incremented each session
- **Log Rotation**: Auto-cleans at 15,000 lines, preserves header
- **Error Notifications**: All ERROR-level log entries automatically fire a toast notification
- **Debug Mode**: Available via debug module - arbitrary function execution through override intents

### Viewing Recent Logs
```
You: "show recent logs"
```
Returns last 20 lines of the log file.

---

## Known Limitations

- Windows-only (uses `os.startfile`, `taskkill`, `win32gui`, `win32process`, `robocopy`)
- Requires explicit "Zorya" mention in shutdown commands
- Intent recognition requires exact token prefix matches - no fuzzy matching
- Audio playback requires pygame library
- File dialogs may appear behind other windows
- System watcher thread updates every 10 seconds
- Dashboard updates every 30 seconds
- Schedule notifications check every hour - sub-hour precision not supported
- Dashboard require tkinter (usually bundled with Python)
- MQTT module requires a running local broker on port 1883
- Routine builder "correct" mode for "other" type intents rebuilds from scratch

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
3. Add new responses to `response_library.json` (text + audio + mood score)
4. Record audio files and place in `Audio_lines/` (150+ lines currently)
5. Create new modules following existing patterns
6. Register new threads in `startup_threads_launcher()` in `Zorya.py`
7. Modify dashboard styling in `flag_dictionary.json`

### Rules and Invariants for Development
1. Flags must never be invalid at runtime
2. Any violation is a developer error
3. Do not catch or suppress flag-related exceptions
4. All modules must use log_handler for consistent logging
5. Thread-safe operations required for shared resources (use locks)
6. She may only mutate her own data that she exclusively owns and generates
7. All daemon threads must respect the stop_event for graceful shutdown
8. Queue-based communication for API mode to prevent race conditions
9. Response library is read-only after bootstrap - no runtime modifications
10. All response data must go through response_handler module
11. Sanitization functions must return a (message, status_code) tuple for bootstrapper error handling
12. New program intents must use `call_program` as action_function to be eligible for sanitization

### Planned Features
- **Log Analyzer**: Query interface for log files + error pattern learning for self-healing
- **Windows Event Probe**: Monitor Windows Event Logs for system-level event awareness
- **ZOBEX (Zorya Behaviour Execution Language)**: Scripting language for defining complex behaviour pipelines in `.zbx` files, parsed and dispatched by a dedicated Complex Behaviour Engine without NLP overhead

---

## Contributing

When testing, please:
1. Monitor `general_system_log.txt` for errors
2. Note any unrecognized commands
3. Report mood system anomalies
4. Share your session logs for analysis
5. Test dashboard display on different screen resolutions
6. Report thread synchronization issues

---

## License

Zorya Seraph Interface - Copyright (C) 2025 Mendoukusai ByteLabs

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
- GitHub: github.com/MasquedMusketeer
- Contact: Mendoukusai.ByteLabs@outlook.com

---

**Note**: Zorya is in active development.
Features and behaviors may change.
Always backup your `Long_term_memory` folder before major updates.
