# 📱 WhatsApp Integration Guide for NTRIA

This guide explains how to connect your NTRIA bot to WhatsApp using Twilio.

## Prerequisites

1.  **Twilio Account**: Sign up at [twilio.com](https://www.twilio.com/).
2.  **Twilio Sandbox for WhatsApp**: Activate it in your Twilio Console.

## Setup Steps

### 1. Configure Environment Variables

Open your `.env` file and update the following lines with your Twilio credentials:

```env
TWILIO_ACCOUNT_SID=AC... (Your Account SID)
TWILIO_AUTH_TOKEN=... (Your Auth Token)
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886 (Twilio Sandbox Number)
```

### 2. Expose Your Local Server (Tunneling)

Since Twilio needs to send a webhook to your local server, you need to expose it to the internet. You can use **ngrok** or **VS Code Port Forwarding**.

**Option A: VS Code Port Forwarding (Recommended for Codespaces)**
1.  Go to the "Ports" tab in VS Code.
2.  Right-click on Port `8000` and select **Port Visibility > Public**.
3.  Copy the "Forwarded Address" (e.g., `https://your-codespace-name-8000.githubpreview.dev`).

**Option B: Ngrok**
1.  Install ngrok.
2.  Run `ngrok http 8000`.
3.  Copy the HTTPS URL (e.g., `https://random-id.ngrok-free.app`).

### 3. Configure Twilio Webhook

1.  Go to the [Twilio Console > Messaging > Try it out > Send a WhatsApp message](https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn).
2.  Go to **Sandbox Settings**.
3.  In the **"When a message comes in"** field, enter your public URL followed by `/api/v1/whatsapp/webhook`.
    *   Example: `https://your-codespace-name-8000.githubpreview.dev/api/v1/whatsapp/webhook`
4.  Set the method to **POST**.
5.  Click **Save**.

## Testing

1.  Join the Twilio Sandbox by sending the code (e.g., `join random-word`) to the Twilio WhatsApp number from your phone.
2.  Once joined, send a message like:
    > "What is the VAT rate in Nigeria?"
3.  The bot should reply with the answer sourced from the Tax Act!

## Troubleshooting

*   **"Service disabled"**: Check your `.env` file to ensure `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN` are set.
*   **No response**: Check the backend logs (`docker logs` or terminal output) for errors. Ensure the webhook URL is correct and publicly accessible.
