# Getting Started with NetGuardian

This guide will help you get started with NetGuardian, our comprehensive cybersecurity platform.

## Installation

### System Requirements

- Operating System: Linux (Ubuntu 20.04+, CentOS 8+), Windows 10/11, macOS 11+
- CPU: 4+ cores
- RAM: 8GB minimum, 16GB recommended
- Storage: 20GB free space
- Python: 3.9 or higher

### Installation Steps

1. Clone the repository:
   \`\`\`
   git clone https://github.com/netguardian/netguardian.git
   cd netguardian
   \`\`\`

2. Create a virtual environment:
   \`\`\`
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   \`\`\`

3. Install dependencies:
   \`\`\`
   pip install -r requirements.txt
   \`\`\`

4. Set up environment variables:
   \`\`\`
   cp .env.example .env
   # Edit .env with your configuration
   \`\`\`

5. Initialize the database:
   \`\`\`
   python scripts/init_db.py
   \`\`\`

## First Steps

### Running a Basic Scan

1. Start the NetGuardian service:
   \`\`\`
   python main.py
   \`\`\`

2. Open your browser and navigate to:
   \`\`\`
   http://localhost:8000
   \`\`\`

3. Log in with the default credentials:
   - Username: admin
   - Password: netguardian123
   (Remember to change these immediately!)

4. Navigate to "New Scan" and enter a target URL or IP address.

5. Select "Quick Scan" and click "Start Scan".

### Understanding Scan Results

After the scan completes, you'll see a summary of findings categorized by severity:

- **Critical**: Vulnerabilities that require immediate attention
- **High**: Serious vulnerabilities that should be addressed soon
- **Medium**: Moderate risk issues
- **Low**: Minor issues with limited risk
- **Info**: Informational findings with no security risk

Click on any finding to see detailed information and remediation steps.

## Next Steps

- Configure scheduled scans
- Set up alerts and notifications
- Integrate with your CI/CD pipeline
- Explore advanced scanning options
