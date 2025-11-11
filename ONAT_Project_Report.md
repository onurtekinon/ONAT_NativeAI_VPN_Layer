# Network Automation Portal (ONAT) - Project Report

## Executive Summary

The **Orchestration of Network Automation Portal (ONAT)** is a comprehensive web-based automation system designed to streamline VPN configuration management for Cisco/juniper/Arista routers. This project automates the creation, modification, and deletion of IPSec VPN configurations through an intuitive web interface, eliminating manual configuration errors and reducing deployment time from hours to minutes.

## Project Overview

### Project Name
**ONAT** - Orchestration of Network Automation Portal

### Objective
Develop an intelligent automation platform that:
- Automates VPN lifecycle management (Create/Modify/Delete)
- Provides real-time CLI command generation
- Maintains comprehensive audit trails
- Ensures configuration consistency across network devices
- Reduces human error through intelligent validation

### Technology Stack
- **Backend**: Python 3.9, Flask Framework
- **Frontend**: HTML5, CSS3, JavaScript
- **Data Format**: YAML, CSV
- **Configuration Management**: Cisco IOS CLI
- **File Processing**: PyYAML, CSV libraries

## System Architecture

### Core Components

#### 1. Web Interface (server.py)
- Flask-based web application
- RESTful API endpoints
- Real-time form validation
- Responsive UI with modern styling
- File upload capabilities

#### 2. Configuration Generator (config_generator.py)
- Intelligent CLI command generation
- Existing policy detection and reuse
- Transform set optimization
- Crypto map sequence management
- Interface configuration automation

#### 3. CSV Processor (csv_processor.py)
- Multi-format CSV parsing
- Data validation and sanitization
- Partner configuration mapping
- YAML structure generation

#### 4. Modification Engine (modify_generator.py)
- Incremental configuration updates
- Change tracking and history
- Conflict detection and resolution
- Non-disruptive modification implementation

#### 5. Delete Manager (delete_generator.py)
- Comprehensive configuration cleanup
- Dependency management
- Cascade deletion handling
- Router configuration parsing

#### 6. Audit System (logger.py)
- Complete action logging
- CLI and YAML output recording
- Timestamp tracking
- Compliance reporting

#### 7. Conflict Checker (conflict_checker.py)
- Interface conflict detection
- Resource allocation validation
- Pre-deployment verification

## Key Features

### 1. Intelligent VPN Creation
```bash
Command: create crypto isakmp sa
Input: CSV file with VPN parameters
Output: Complete Cisco CLI configuration