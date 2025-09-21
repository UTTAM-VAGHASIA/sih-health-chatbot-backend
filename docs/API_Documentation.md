# SIH Health Chatbot Backend - API Documentation

## Overview

This document provides comprehensive API documentation for the SIH Health Chatbot Backend, including detailed information about the alert broadcast system for frontend admin panel integration.

**Base URL**: `http://localhost:8000` (development) or your deployed URL  
**API Version**: 1.0.0  
**Framework**: FastAPI with automatic OpenAPI documentation

## Table of Contents

1. [Authentication](#authentication)
2. [Admin Alert Broadcasting API](#admin-alert-broadcasting-api)
3. [Admin Statistics API](#admin-statistics-api)
4. [Demo Management API](#demo-management-api)
5. [WhatsApp Webhook API](#whatsapp-webhook-api)
6. [Health Check Endpoints](#health-check-endpoints)
7. [Frontend Integration Guide](#frontend-integration-guide)
8. [Error Handling](#error-handling)

---

## Authentication

Currently, the API does not require authentication for demo purposes. In production, implement proper authentication mechanisms.

---

## Admin Alert Broadcasting API

### 🚨 Broadcast Alert to All Users

**Endpoint**: `POST /admin/alerts`  
**Description**: Broadcast an alert message to all registered WhatsApp users  
**Content-Type**: `application/json`

#### Request Body

```json
{
  "message": "string (required, 1-1000 characters)",
  "priority": "string (optional, enum: low|medium|high, default: medium)"
}
```

#### Request Example

```json
{
  "message": "🚨 HEALTH ALERT: Vaccination drive starting tomorrow at all government health centers. Please bring your ID and previous vaccination records.",
  "priority": "high"
}
```

#### Response (200 OK)

```json
{
  "success": true,
  "users_targeted": 25,
  "successful_deliveries": 23,
  "failed_deliveries": 2,
  "message_id": "alert_123456",
  "errors": [
    "+91****7944: Rate limit exceeded",
    "+91****8855: Invalid phone number"
  ]
}
```

#### Response Schema

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Whether the broadcast was successful |
| `users_targeted` | integer | Number of users targeted for the alert |
| `successful_deliveries` | integer | Number of successful message deliveries |
| `failed_deliveries` | integer | Number of failed message deliveries |
| `message_id` | string | Unique identifier for this alert broadcast |
| `errors` | array[string] | List of error messages if any failures occurred |

#### Frontend Integration Example

```javascript
// JavaScript/React example for frontend admin panel
async function broadcastAlert(message, priority = 'medium') {
  try {
    const response = await fetch('/admin/alerts', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: message,
        priority: priority
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    
    // Handle successful broadcast
    console.log(`Alert sent to ${result.users_targeted} users`);
    console.log(`Success: ${result.successful_deliveries}, Failed: ${result.failed_deliveries}`);
    
    if (result.errors && result.errors.length > 0) {
      console.warn('Some deliveries failed:', result.errors);
    }
    
    return result;
  } catch (error) {
    console.error('Failed to broadcast alert:', error);
    throw error;
  }
}

// Usage example
broadcastAlert(
  "🏥 Important: New COVID-19 guidelines are now in effect. Visit our website for details.",
  "high"
);
```

#### cURL Example

```bash
curl -X POST "http://localhost:8000/admin/alerts" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "🚨 URGENT: Health emergency alert - Please follow safety protocols immediately.",
    "priority": "high"
  }'
```

---

## Admin Statistics API

### 📊 Get Admin Statistics

**Endpoint**: `GET /admin/stats`  
**Description**: Get comprehensive administrative statistics for the dashboard

#### Response Example

```json
{
  "user_statistics": {
    "total_users": 150,
    "active_users": 142,
    "inactive_users": 8,
    "user_growth_rate": "Demo: +5 users/day"
  },
  "performance_metrics": {
    "total_users": 150,
    "active_users": 142,
    "total_messages": 1250,
    "avg_response_time_ms": 185.5,
    "uptime_percentage": 99.8,
    "system_status": "operational",
    "last_updated": "2025-01-21T10:30:00Z"
  },
  "engagement_statistics": {
    "total_messages": 1250,
    "avg_messages_per_user": 8.33,
    "recent_active_users_24h": 45,
    "engagement_rate": 31.69
  },
  "system_info": {
    "system_status": "operational",
    "environment": "demo",
    "uptime": "99.9%",
    "last_updated": "2025-01-21T10:30:00Z"
  },
  "demo_info": {
    "is_demo_environment": true,
    "demo_features_active": true,
    "judge_evaluation_mode": true
  }
}
```

### 👥 Get Registered Users

**Endpoint**: `GET /admin/users`  
**Description**: Get list of all registered users (anonymized for privacy)

#### Response Example

```json
{
  "users": [
    {
      "phone_number": "+91****7944",
      "first_seen": "2025-01-20T09:15:00Z",
      "last_activity": "2025-01-21T10:25:00Z",
      "message_count": 12,
      "is_active": true
    }
  ],
  "total_count": 150
}
```

---

## Demo Management API

### 🎯 Setup Demo Environment

**Endpoint**: `POST /admin/demo/setup`  
**Description**: Setup complete demo environment for judge evaluation

#### Response Example

```json
{
  "success": true,
  "message": "Demo environment setup completed successfully",
  "demo_info": {
    "demo_users_created": 10,
    "demo_phone_numbers": ["+917434017944", "+919876543210", "+919876543211"],
    "setup_timestamp": "2025-01-21T10:30:00Z"
  },
  "current_stats": {
    "total_users": 10,
    "active_users": 10
  },
  "judge_instructions": {
    "test_numbers": ["+917434017944", "+919876543210", "+919876543211"],
    "test_commands": ["hello", "demo", "judges", "health", "broadcast"],
    "admin_endpoints": ["/admin/alerts", "/admin/stats", "/admin/demo/broadcast"]
  }
}
```

### 📢 Send Demo Broadcast

**Endpoint**: `POST /admin/demo/broadcast`  
**Description**: Send a pre-configured demo alert to showcase the system

#### Response

Same as the main broadcast alert endpoint, but uses pre-configured demo messages.

### 📈 Get Demo Metrics

**Endpoint**: `GET /admin/demo/metrics`  
**Description**: Get comprehensive demo metrics for evaluation

### 🔄 Reset Demo Data

**Endpoint**: `DELETE /admin/demo/reset`  
**Description**: Reset demo data for fresh demonstration

---

## WhatsApp Webhook API

### 📱 Webhook Verification

**Endpoint**: `GET /webhook/whatsapp`  
**Description**: WhatsApp webhook verification endpoint

### 💬 Receive Messages

**Endpoint**: `POST /webhook/whatsapp`  
**Description**: Receive and process WhatsApp messages

---

## Health Check Endpoints

### 🏥 Basic Health Check

**Endpoint**: `GET /ping`  
**Description**: Basic health check for monitoring

#### Response Example

```json
{
  "status": "ok",
  "message": "Backend is running 🚀",
  "environment": "development",
  "configuration_valid": true,
  "warnings": null
}
```

### 🔍 Detailed Health Check

**Endpoint**: `GET /health`  
**Description**: Comprehensive health check with detailed system information

---

## Frontend Integration Guide

### React Admin Panel Example

```jsx
import React, { useState, useEffect } from 'react';

const AdminPanel = () => {
  const [stats, setStats] = useState(null);
  const [alertMessage, setAlertMessage] = useState('');
  const [alertPriority, setAlertPriority] = useState('medium');
  const [loading, setLoading] = useState(false);

  // Fetch admin statistics
  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await fetch('/admin/stats');
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  const handleBroadcast = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch('/admin/alerts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: alertMessage,
          priority: alertPriority
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      alert(`Alert sent successfully!\nTargeted: ${result.users_targeted} users\nSuccessful: ${result.successful_deliveries}\nFailed: ${result.failed_deliveries}`);
      
      setAlertMessage('');
      fetchStats(); // Refresh stats
    } catch (error) {
      alert(`Failed to send alert: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="admin-panel">
      <h1>Health Chatbot Admin Panel</h1>
      
      {/* Statistics Dashboard */}
      {stats && (
        <div className="stats-section">
          <h2>System Statistics</h2>
          <div className="stats-grid">
            <div className="stat-card">
              <h3>Total Users</h3>
              <p>{stats.user_statistics.total_users}</p>
            </div>
            <div className="stat-card">
              <h3>Active Users</h3>
              <p>{stats.user_statistics.active_users}</p>
            </div>
            <div className="stat-card">
              <h3>Total Messages</h3>
              <p>{stats.performance_metrics.total_messages}</p>
            </div>
            <div className="stat-card">
              <h3>Avg Response Time</h3>
              <p>{stats.performance_metrics.avg_response_time_ms}ms</p>
            </div>
          </div>
        </div>
      )}

      {/* Alert Broadcast Form */}
      <div className="broadcast-section">
        <h2>Broadcast Alert</h2>
        <form onSubmit={handleBroadcast}>
          <div className="form-group">
            <label htmlFor="message">Alert Message:</label>
            <textarea
              id="message"
              value={alertMessage}
              onChange={(e) => setAlertMessage(e.target.value)}
              placeholder="Enter your health alert message..."
              required
              maxLength={1000}
              rows={4}
            />
            <small>{alertMessage.length}/1000 characters</small>
          </div>
          
          <div className="form-group">
            <label htmlFor="priority">Priority Level:</label>
            <select
              id="priority"
              value={alertPriority}
              onChange={(e) => setAlertPriority(e.target.value)}
            >
              <option value="low">Low (ℹ️ INFO)</option>
              <option value="medium">Medium (⚠️ ALERT)</option>
              <option value="high">High (🚨 URGENT)</option>
            </select>
          </div>
          
          <button type="submit" disabled={loading || !alertMessage.trim()}>
            {loading ? 'Sending...' : 'Broadcast Alert'}
          </button>
        </form>
      </div>

      {/* Quick Demo Actions */}
      <div className="demo-section">
        <h2>Demo Actions</h2>
        <button onClick={() => fetch('/admin/demo/setup', { method: 'POST' })}>
          Setup Demo Environment
        </button>
        <button onClick={() => fetch('/admin/demo/broadcast', { method: 'POST' })}>
          Send Demo Alert
        </button>
        <button onClick={() => fetch('/admin/demo/reset', { method: 'DELETE' })}>
          Reset Demo Data
        </button>
      </div>
    </div>
  );
};

export default AdminPanel;
```

### Vue.js Example

```vue
<template>
  <div class="admin-panel">
    <h1>Health Chatbot Admin Panel</h1>
    
    <!-- Alert Broadcast Form -->
    <form @submit.prevent="broadcastAlert" class="broadcast-form">
      <div class="form-group">
        <label for="message">Alert Message:</label>
        <textarea
          id="message"
          v-model="alertMessage"
          placeholder="Enter your health alert message..."
          required
          maxlength="1000"
          rows="4"
        ></textarea>
        <small>{{ alertMessage.length }}/1000 characters</small>
      </div>
      
      <div class="form-group">
        <label for="priority">Priority Level:</label>
        <select id="priority" v-model="alertPriority">
          <option value="low">Low (ℹ️ INFO)</option>
          <option value="medium">Medium (⚠️ ALERT)</option>
          <option value="high">High (🚨 URGENT)</option>
        </select>
      </div>
      
      <button type="submit" :disabled="loading || !alertMessage.trim()">
        {{ loading ? 'Sending...' : 'Broadcast Alert' }}
      </button>
    </form>
  </div>
</template>

<script>
export default {
  name: 'AdminPanel',
  data() {
    return {
      alertMessage: '',
      alertPriority: 'medium',
      loading: false
    }
  },
  methods: {
    async broadcastAlert() {
      this.loading = true;
      
      try {
        const response = await fetch('/admin/alerts', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            message: this.alertMessage,
            priority: this.alertPriority
          })
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        
        alert(`Alert sent successfully!\nTargeted: ${result.users_targeted} users\nSuccessful: ${result.successful_deliveries}\nFailed: ${result.failed_deliveries}`);
        
        this.alertMessage = '';
      } catch (error) {
        alert(`Failed to send alert: ${error.message}`);
      } finally {
        this.loading = false;
      }
    }
  }
}
</script>
```

---

## Error Handling

### Common Error Responses

#### 400 Bad Request
```json
{
  "error_code": "VALIDATION_ERROR",
  "message": "Invalid request data",
  "details": {
    "field": "message",
    "error": "Message cannot be empty"
  },
  "request_id": "req_123456"
}
```

#### 500 Internal Server Error
```json
{
  "error_code": "INTERNAL_SERVER_ERROR",
  "message": "Internal server error during alert broadcast",
  "request_id": "req_123456"
}
```

### Error Handling in Frontend

```javascript
async function handleApiCall(url, options) {
  try {
    const response = await fetch(url, options);
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || `HTTP ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('API call failed:', error);
    
    // Show user-friendly error message
    if (error.message.includes('network') || error.message.includes('fetch')) {
      alert('Network error. Please check your connection and try again.');
    } else {
      alert(`Error: ${error.message}`);
    }
    
    throw error;
  }
}
```

---

## Testing the API

### Using Postman

1. **Import Collection**: Create a Postman collection with the endpoints above
2. **Set Base URL**: Configure `{{baseUrl}}` variable to your server URL
3. **Test Broadcast**: Use the POST `/admin/alerts` endpoint with sample data

### Using curl

```bash
# Test broadcast alert
curl -X POST "http://localhost:8000/admin/alerts" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "🏥 Test health alert from admin panel",
    "priority": "medium"
  }'

# Get admin statistics
curl -X GET "http://localhost:8000/admin/stats"

# Setup demo environment
curl -X POST "http://localhost:8000/admin/demo/setup"
```

---

## Interactive API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

These interfaces allow you to test all endpoints directly from your browser.

---

## Production Considerations

1. **Authentication**: Implement proper authentication (JWT, OAuth2, etc.)
2. **Rate Limiting**: Add rate limiting to prevent abuse
3. **Input Validation**: Enhanced validation for production use
4. **Logging**: Comprehensive logging for monitoring and debugging
5. **Error Handling**: More detailed error responses and handling
6. **CORS**: Configure CORS settings for frontend integration
7. **HTTPS**: Use HTTPS in production
8. **Database**: Replace in-memory storage with persistent database

---

## Support

For technical support or questions about the API:
- Check the interactive documentation at `/docs`
- Review the source code in the repository
- Contact the development team

---

**Last Updated**: January 21, 2025  
**API Version**: 1.0.0  
**Framework**: FastAPI 0.115.13