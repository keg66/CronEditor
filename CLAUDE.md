# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**CronEditor** is a web-based GUI application designed to manage and edit existing cron jobs on Raspberry Pi via web browser. The primary goal is to eliminate the need for SSH connections and manual `crontab -e` commands for frequent cron job time adjustments.

## Target Environment

- **Server**: Raspberry Pi (Linux environment)
- **Client**: Home LAN browser access only
- **Users**: Individual/family use (trusted local network)
- **Deployment**: systemd service with configurable port

## Core Functionality

### Scope - What the Application DOES:
- Display existing crontab entries in a list format
- Edit execution times of existing cron jobs only
- Enable/disable cron jobs via checkbox
- In-line editing with save/cancel buttons
- Time selection via dropdown menus (minutes: 0-59, hours: 0-23, etc.)

### Scope - What the Application DOES NOT:
- Create new cron jobs
- Delete cron jobs
- Edit command text
- Show execution history/logs
- Backup/restore functionality

## Architecture Requirements

- Web application (frontend/backend separation or server-side rendering)
- Lightweight design for Raspberry Pi performance
- Simple, intuitive UI requiring no technical knowledge
- Responsive design (PC/tablet support)
- Minimal security (local LAN trusted environment)
- systemd service integration
- Configuration file for port settings

## Key Design Principles

1. **Simplicity over complexity** - prioritize usability over technical sophistication
2. **Maintainability** - simple, understandable codebase structure
3. **Performance** - lightweight operation suitable for Raspberry Pi
4. **Minimal viable product** - focused feature set, no feature creep

## Success Criteria

The application should enable users to modify cron job schedules faster and more intuitively than SSH + `crontab -e`, while running reliably as a systemd service on Raspberry Pi.