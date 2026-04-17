# Integrations API - Frontend Integration Guide

## Overview

The integrations API allows dynamic configuration of Twilio and HubSpot credentials from the frontend, eliminating the need for hardcoded environment variables.

## Base URL

```
http://localhost:8000/integrations
```

## Authentication

All endpoints require JWT authentication via Bearer token.

```typescript
headers: {
  'Authorization': `Bearer ${token}`,
  'Content-Type': 'application/json'
}
```

---

## Endpoints

### GET /integrations

Get current integration configurations (with masked sensitive data).

**Response**:
```json
{
  "twilio": {
    "account_sid": "AC1234567...",
    "whatsapp_number": "+1234567890",
    "configured": true
  },
  "hubspot": {
    "enabled": true,
    "configured": true
  }
}
```

### PUT /integrations/twilio

Configure Twilio credentials.

**Request**:
```json
{
  "account_sid": "<your_twilio_account_sid>",
  "auth_token": "your_auth_token_here",
  "whatsapp_number": "+1234567890"
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Twilio configuration updated successfully",
  "configured": true
}
```

### PUT /integrations/hubspot

Configure HubSpot credentials.

**Request**:
```json
{
  "access_token": "pat-na1-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "enabled": true
}
```

**Response**:
```json
{
  "status": "success",
  "message": "HubSpot configuration updated successfully",
  "enabled": true
}
```

### DELETE /integrations/twilio

Remove Twilio configuration.

**Response**:
```json
{
  "status": "success",
  "message": "Twilio configuration deleted successfully"
}
```

### DELETE /integrations/hubspot

Remove HubSpot configuration.

**Response**:
```json
{
  "status": "success",
  "message": "HubSpot configuration deleted successfully"
}
```

### POST /integrations/twilio/test

Test Twilio connection with current credentials.

**Response** (success):
```json
{
  "status": "success",
  "message": "Twilio connection successful",
  "whatsapp_number": "+1234567890"
}
```

**Response** (error):
```json
{
  "detail": "Twilio connection test failed: Invalid credentials"
}
```

### POST /integrations/hubspot/test

Test HubSpot connection with current credentials.

**Response** (success):
```json
{
  "status": "success",
  "message": "HubSpot connection successful",
  "enabled": true
}
```

**Response** (error):
```json
{
  "detail": "HubSpot connection test failed: Invalid access token"
}
```

---

## Frontend Implementation Example

### React Component

```typescript
import { useState, useEffect } from 'react';
import { api } from '@/lib/api';

interface TwilioConfig {
  account_sid: string;
  auth_token: string;
  whatsapp_number: string;
}

interface HubSpotConfig {
  access_token: string;
  enabled: boolean;
}

export function IntegrationsPanel() {
  const [twilioConfig, setTwilioConfig] = useState<TwilioConfig>({
    account_sid: '',
    auth_token: '',
    whatsapp_number: ''
  });
  
  const [hubspotConfig, setHubSpotConfig] = useState<HubSpotConfig>({
    access_token: '',
    enabled: true
  });
  
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<{twilio: boolean, hubspot: boolean}>({
    twilio: false,
    hubspot: false
  });

  // Load current configuration
  useEffect(() => {
    loadIntegrations();
  }, []);

  const loadIntegrations = async () => {
    try {
      const response = await api.get('/integrations');
      setStatus({
        twilio: response.data.twilio?.configured || false,
        hubspot: response.data.hubspot?.configured || false
      });
    } catch (error) {
      console.error('Failed to load integrations:', error);
    }
  };

  const saveTwilioConfig = async () => {
    setLoading(true);
    try {
      await api.put('/integrations/twilio', twilioConfig);
      alert('Twilio configuration saved successfully!');
      await loadIntegrations();
    } catch (error) {
      alert('Failed to save Twilio configuration');
    } finally {
      setLoading(false);
    }
  };

  const testTwilioConnection = async () => {
    setLoading(true);
    try {
      const response = await api.post('/integrations/twilio/test');
      alert(response.data.message);
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Connection test failed');
    } finally {
      setLoading(false);
    }
  };

  const saveHubSpotConfig = async () => {
    setLoading(true);
    try {
      await api.put('/integrations/hubspot', hubspotConfig);
      alert('HubSpot configuration saved successfully!');
      await loadIntegrations();
    } catch (error) {
      alert('Failed to save HubSpot configuration');
    } finally {
      setLoading(false);
    }
  };

  const testHubSpotConnection = async () => {
    setLoading(true);
    try {
      const response = await api.post('/integrations/hubspot/test');
      alert(response.data.message);
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Connection test failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Twilio Configuration */}
      <div className="border rounded-lg p-6">
        <h2 className="text-xl font-bold mb-4">
          Twilio WhatsApp
          {status.twilio && <span className="ml-2 text-green-600">✓ Configured</span>}
        </h2>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Account SID</label>
            <input
              type="text"
              value={twilioConfig.account_sid}
              onChange={(e) => setTwilioConfig({...twilioConfig, account_sid: e.target.value})}
              className="w-full border rounded px-3 py-2"
              placeholder="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">Auth Token</label>
            <input
              type="password"
              value={twilioConfig.auth_token}
              onChange={(e) => setTwilioConfig({...twilioConfig, auth_token: e.target.value})}
              className="w-full border rounded px-3 py-2"
              placeholder="Your auth token"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">WhatsApp Number</label>
            <input
              type="text"
              value={twilioConfig.whatsapp_number}
              onChange={(e) => setTwilioConfig({...twilioConfig, whatsapp_number: e.target.value})}
              className="w-full border rounded px-3 py-2"
              placeholder="+1234567890"
            />
          </div>
          
          <div className="flex gap-2">
            <button
              onClick={saveTwilioConfig}
              disabled={loading}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
            >
              Save Twilio Config
            </button>
            
            <button
              onClick={testTwilioConnection}
              disabled={loading || !status.twilio}
              className="px-4 py-2 border rounded hover:bg-gray-50 disabled:opacity-50"
            >
              Test Connection
            </button>
          </div>
        </div>
      </div>

      {/* HubSpot Configuration */}
      <div className="border rounded-lg p-6">
        <h2 className="text-xl font-bold mb-4">
          HubSpot CRM
          {status.hubspot && <span className="ml-2 text-green-600">✓ Configured</span>}
        </h2>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Access Token</label>
            <input
              type="password"
              value={hubspotConfig.access_token}
              onChange={(e) => setHubSpotConfig({...hubspotConfig, access_token: e.target.value})}
              className="w-full border rounded px-3 py-2"
              placeholder="pat-na1-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
            />
          </div>
          
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={hubspotConfig.enabled}
              onChange={(e) => setHubSpotConfig({...hubspotConfig, enabled: e.target.checked})}
              className="rounded"
            />
            <label className="text-sm font-medium">Enable HubSpot Sync</label>
          </div>
          
          <div className="flex gap-2">
            <button
              onClick={saveHubSpotConfig}
              disabled={loading}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
            >
              Save HubSpot Config
            </button>
            
            <button
              onClick={testHubSpotConnection}
              disabled={loading || !status.hubspot}
              className="px-4 py-2 border rounded hover:bg-gray-50 disabled:opacity-50"
            >
              Test Connection
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
```

---

## Configuration Priority

The system loads credentials in the following order:

1. **Direct parameters** (when initializing services programmatically)
2. **Database configuration** (set via API endpoints)
3. **Environment variables** (fallback for backward compatibility)

This ensures backward compatibility while enabling dynamic configuration from the frontend.

---

## Security Notes

- All credentials are stored encrypted in the database
- Sensitive data is masked when retrieved via GET endpoint
- Test endpoints validate credentials without exposing them
- Authentication is required for all endpoints

---

## Error Handling

All endpoints return standard HTTP status codes:

- `200 OK`: Success
- `400 Bad Request`: Invalid input or configuration not set
- `401 Unauthorized`: Missing or invalid authentication
- `500 Internal Server Error`: Server error

Error response format:
```json
{
  "detail": "Error message describing what went wrong"
}
```
