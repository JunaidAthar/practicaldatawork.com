/**
 * Cloudflare Pages Function to handle contact form submissions
 * Version 2: With D1 Database Storage
 * 
 * This version stores all submissions in D1 database AND sends emails via MailChannels
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
    
    // Get visitor info
    const ipAddress = request.headers.get('CF-Connecting-IP') || 'Unknown';
    const userAgent = request.headers.get('User-Agent') || 'Unknown';
    const timestamp = new Date().toISOString();
    
    // Store in D1 Database FIRST (so we never lose a submission)
    let dbSaved = false;
    if (env.DB) {
      try {
        const stmt = env.DB.prepare(
          `INSERT INTO contacts (name, email, company, service, budget, message, ip_address, user_agent, created_at, status)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`
        );
        
        await stmt.bind(
          data.name,
          data.email,
          data.company || null,
          data.service || null,
          data.budget || null,
          data.message,
          ipAddress,
          userAgent,
          timestamp,
          'new'
        ).run();
        
        dbSaved = true;
        console.log('✅ Contact saved to D1 database:', data.email);
      } catch (dbError) {
        console.error('❌ Failed to save to database:', dbError);
        // Continue anyway - try to send email
      }
    } else {
      console.warn('⚠️ D1 database not bound - submissions will not be stored');
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
IP: ${ipAddress}
User Agent: ${userAgent}
    `.trim();
    
    const htmlContent = `
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
    .cta { background: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block; margin-top: 20px; }
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
      <div style="text-align: center;">
        <a href="mailto:${data.email}" class="cta">Reply to ${data.name}</a>
      </div>
      <div class="footer">
        <p>Submitted: ${new Date().toLocaleString('en-US', { timeZone: 'America/Chicago' })}</p>
        <p>View all contacts: <a href="https://practicaldatawork.com/admin/contacts.html">Admin Panel</a></p>
      </div>
    </div>
  </div>
</body>
</html>
    `.trim();
    
    // Try sending email via MailChannels
    let emailSent = false;
    try {
      const emailResponse = await fetch('https://api.mailchannels.net/tx/v1/send', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          personalizations: [
            {
              to: [{ email: 'junaid.athar@gmail.com', name: 'Junaid Athar' }],
              dkim_domain: 'practicaldatawork.com',
              dkim_selector: 'mailchannels',
            },
          ],
          from: {
            email: 'noreply@practicaldatawork.com',
            name: 'Practical Data Work Contact Form',
          },
          reply_to: {
            email: data.email,
            name: data.name,
          },
          subject: `New Lead: ${data.name} - ${data.service || 'Contact Form'}`,
          content: [
            {
              type: 'text/plain',
              value: emailContent,
            },
            {
              type: 'text/html',
              value: htmlContent,
            },
          ],
        }),
      });
      
      if (emailResponse.ok) {
        emailSent = true;
        console.log('✅ Email sent via MailChannels');
      } else {
        const errorText = await emailResponse.text();
        console.error('❌ MailChannels error:', errorText);
      }
      
    } catch (mailchannelsError) {
      console.error('❌ MailChannels exception:', mailchannelsError);
    }
    
    // Return success response
    const responseMessage = [];
    if (dbSaved) {
      responseMessage.push('✅ Contact saved to database');
    }
    if (emailSent) {
      responseMessage.push('✅ Email notification sent');
    }
    
    return new Response(JSON.stringify({ 
      success: true,
      message: 'Thank you for your message! I\'ll get back to you within 24 hours.',
      debug: {
        database: dbSaved ? 'saved' : 'failed',
        email: emailSent ? 'sent' : 'failed',
        details: responseMessage.join(', ')
      }
    }), {
      status: 200,
      headers: { 
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      }
    });
    
  } catch (error) {
    console.error('❌ Contact form error:', error);
    
    return new Response(JSON.stringify({ 
      error: 'Failed to process message',
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

