/**
 * API endpoint to list all contacts from D1 database
 * Used by the admin panel
 */

// Simple authentication (you should change this password!)
const ADMIN_PASSWORD = 'practicaldatawork2024';

export async function onRequestGet(context) {
  const { request, env } = context;
  
  // Check authentication
  const authHeader = request.headers.get('Authorization');
  if (!authHeader || authHeader !== `Bearer ${ADMIN_PASSWORD}`) {
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
    
    // Build query
    let query = 'SELECT * FROM contacts WHERE 1=1';
    const params = [];
    
    if (status) {
      query += ' AND status = ?';
      params.push(status);
    }
    
    if (search) {
      query += ' AND (name LIKE ? OR email LIKE ? OR company LIKE ? OR message LIKE ?)';
      const searchPattern = `%${search}%`;
      params.push(searchPattern, searchPattern, searchPattern, searchPattern);
    }
    
    query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?';
    params.push(limit, offset);
    
    // Execute query
    const stmt = env.DB.prepare(query);
    const { results } = await stmt.bind(...params).all();
    
    // Get total count
    let countQuery = 'SELECT COUNT(*) as total FROM contacts WHERE 1=1';
    const countParams = [];
    
    if (status) {
      countQuery += ' AND status = ?';
      countParams.push(status);
    }
    
    if (search) {
      countQuery += ' AND (name LIKE ? OR email LIKE ? OR company LIKE ? OR message LIKE ?)';
      const searchPattern = `%${search}%`;
      countParams.push(searchPattern, searchPattern, searchPattern, searchPattern);
    }
    
    const countStmt = env.DB.prepare(countQuery);
    const { results: countResults } = await countStmt.bind(...countParams).all();
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

