/**
 * Cloudflare Pages Function to handle contact form submissions
 * Sends email notifications using MailChannels (free on Cloudflare)
 */

export async function onRequestPost(context) {
  const { request, env } = context;
  
  try {
    // Parse the form data
    const data = await request.json();
    
    // Validate required fields
    if (!data.name || !data.email || !data.message) {
      return new Response(JSON.stringify({ 
        error: 'Missing required fields' 
      }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    // Prepare email content
    const emailContent = `
New Contact Form Submission - Practical Data Work
=================================================

From: ${data.name}
Email: ${data.email}
Company: ${data.company || 'Not provided'}
Service Interest: ${data.service || 'Not specified'}
Budget Range: ${data.budget || 'Not specified'}

Message:
${data.message}

---
Submitted: ${new Date().toLocaleString('en-US', { timeZone: 'America/Chicago' })}
IP: ${request.headers.get('CF-Connecting-IP') || 'Unknown'}
    `.trim();
    
    // Send email using MailChannels (free email service for Cloudflare)
    const emailResponse = await fetch('https://api.mailchannels.net/tx/v1/send', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        personalizations: [
          {
            to: [{ email: 'junaid.athar@gmail.com', name: 'Junaid Athar' }],
            reply_to: { email: data.email, name: data.name },
          },
        ],
        from: {
          email: 'noreply@practicaldatawork.com',
          name: 'Practical Data Work Contact Form',
        },
        subject: `New Lead: ${data.name} - ${data.service || 'Contact Form'}`,
        content: [
          {
            type: 'text/plain',
            value: emailContent,
          },
          {
            type: 'text/html',
            value: `
<!DOCTYPE html>
<html>
<head>
  <style>
    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
    .header { background: #2563eb; color: white; padding: 20px; border-radius: 5px 5px 0 0; }
    .content { background: #f9fafb; padding: 20px; border: 1px solid #e5e7eb; }
    .field { margin-bottom: 15px; }
    .label { font-weight: bold; color: #1f2937; }
    .value { color: #4b5563; margin-top: 5px; }
    .message-box { background: white; padding: 15px; border-left: 4px solid #2563eb; margin-top: 15px; }
    .footer { text-align: center; color: #6b7280; font-size: 12px; margin-top: 20px; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h2 style="margin: 0;">🎉 New Contact Form Submission</h2>
      <p style="margin: 5px 0 0 0;">Practical Data Work</p>
    </div>
    <div class="content">
      <div class="field">
        <div class="label">👤 Name:</div>
        <div class="value">${data.name}</div>
      </div>
      <div class="field">
        <div class="label">📧 Email:</div>
        <div class="value"><a href="mailto:${data.email}">${data.email}</a></div>
      </div>
      <div class="field">
        <div class="label">🏢 Company:</div>
        <div class="value">${data.company || 'Not provided'}</div>
      </div>
      <div class="field">
        <div class="label">🎯 Service Interest:</div>
        <div class="value">${data.service || 'Not specified'}</div>
      </div>
      <div class="field">
        <div class="label">💰 Budget Range:</div>
        <div class="value">${data.budget || 'Not specified'}</div>
      </div>
      <div class="message-box">
        <div class="label">📝 Message:</div>
        <div class="value" style="white-space: pre-wrap;">${data.message}</div>
      </div>
      <div class="footer">
        <p>Submitted: ${new Date().toLocaleString('en-US', { timeZone: 'America/Chicago' })}</p>
        <p>Reply directly to this email to respond to ${data.name}</p>
      </div>
    </div>
  </div>
</body>
</html>
            `.trim(),
          },
        ],
      }),
    });
    
    if (!emailResponse.ok) {
      console.error('MailChannels error:', await emailResponse.text());
      throw new Error('Failed to send email');
    }
    
    return new Response(JSON.stringify({ 
      success: true,
      message: 'Message sent successfully' 
    }), {
      status: 200,
      headers: { 
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      }
    });
    
  } catch (error) {
    console.error('Contact form error:', error);
    
    return new Response(JSON.stringify({ 
      error: 'Failed to send message',
      details: error.message 
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

// Handle OPTIONS request for CORS
export async function onRequestOptions() {
  return new Response(null, {
    status: 204,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    },
  });
}

