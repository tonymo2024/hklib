# HK Library Book Renewal Automation

## Description
An automated Python script that helps users manage their Hong Kong Public Library borrowed books by:
- Automatically logging into the HKPL account
- Checking due dates of borrowed books
- Identifying books that are due within 5 days
- Automatically renewing books that are near their due date
- Providing detailed console output of the renewal process
- Saving error logs and screenshots if issues occur

## Features
- Automated login handling
- Multi-format date parsing
- Near-due book detection (< 5 days)
- Automatic book renewal
- Error handling with debug information
- Chrome WebDriver automation

## Technical Implementation
Built using:
- Selenium WebDriver for browser automation
- Python datetime for date handling
- Configuration file for credentials management

## Configuration Setup
1. Copy `config.template.py` to `config.py`:
```bash
cp config.template.py config.py
```

2. Edit `config.py` with your credentials:
- Library card number and password
- Gmail sender address
- Recipient email address
- Gmail app password (Generate from Google Account settings)

Note: Never commit `config.py` with your actual credentials to Git. The template file is provided as a reference only.

## Author
Developed by Tony Mok
Last Updated: 2025.07