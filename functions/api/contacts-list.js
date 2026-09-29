/**
 * API endpoint to list all contacts from D1 database
 * Used by the admin panel
 */

export async function onRequestGet(context) {
  const { request, env } = context;

  // Check authentication
  const adminPassword = env.ADMIN_PASSWORD;
  const authHeader = request.headers.get('Authorization');
  if (!adminPassword || !authHeader || authHeader !== `Bearer ${adminPassword}`) {
    return new Response(JSON.stringify({ 
      error: 'Unauthorized' 
    }), {
      status: 401,
      headers: { 'Content-Type': 'application/json' }
    });
  }
  
  try {
    if (!env.DB) {
      return new Response(JSON.stringify({ 
        error: 'Database not configured' 
      }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    // Get query parameters
    const url = new URL(request.url);
    const limit = parseInt(url.searchParams.get('limit') || '50');
    const offset = parseInt(url.searchParams.get('offset') || '0');
    const status = url.searchParams.get('status') || null;
    const search = url.searchParams.get('search') || null;
    
    let where = ' WHERE 1=1';
    const params = [];
    if (status) {
      where += ' AND status = ?';
      params.push(status);
    }
    if (search) {
      where += ' AND (name LIKE ? OR email LIKE ? OR pharmacy LIKE ? OR location LIKE ? OR notes LIKE ?)';
      const p = `%${search}%`;
      params.push(p, p, p, p, p);
    }

    const { results } = await env.DB.prepare(`SELECT * FROM audit_requests${where} ORDER BY created_at DESC LIMIT ? OFFSET ?`)
      .bind(...params, limit, offset).all();
    const { results: countResults } = await env.DB.prepare(`SELECT COUNT(*) as total FROM audit_requests${where}`)
      .bind(...params).all();
    const total = countResults[0]?.total || 0;
    
    return new Response(JSON.stringify({ 
      success: true,
      contacts: results,
      total,
      limit,
      offset
    }), {
      status: 200,
      headers: { 
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      }
    });
    
  } catch (error) {
    console.error('Error fetching contacts:', error);
    return new Response(JSON.stringify({ 
      error: 'Failed to fetch contacts',
      details: error.message 
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

// Handle OPTIONS for CORS
export async function onRequestOptions() {
  return new Response(null, {
    status: 204,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  });
}

