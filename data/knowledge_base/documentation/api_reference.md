# API Reference

## Authentication

All API requests require authentication using an API key. Include your API key in the header of each request:

\`\`\`
Authorization: Bearer YOUR_API_KEY
\`\`\`

## Endpoints

### GET /api/v1/status

Returns the current status of the system.

**Response:**
\`\`\`json
{
  "status": "operational",
  "version": "1.2.3",
  "uptime": "10d 4h 30m"
}
\`\`\`

### POST /api/v1/scan

Initiates a security scan on the specified target.

**Request Body:**
\`\`\`json
{
  "target": "example.com",
  "scan_type": "full",
  "options": {
    "port_scan": true,
    "vulnerability_scan": true
  }
}
\`\`\`

**Response:**
\`\`\`json
{
  "scan_id": "abc123",
  "status": "initiated",
  "estimated_completion_time": "2023-05-18T15:30:00Z"
}
\`\`\`

### GET /api/v1/scan/{scan_id}

Retrieves the results of a specific scan.

**Response:**
\`\`\`json
{
  "scan_id": "abc123",
  "status": "completed",
  "results": {
    "vulnerabilities_found": 3,
    "risk_level": "medium",
    "details": [...]
  }
}
