/**
 * Cloudflare Worker Entry Point
 * This worker acts as a proxy to Python Flask application
 * 
 * Note: Bu dosya Cloudflare Workers için hazırlanmıştır.
 * Python Flask uygulaması doğrudan Workers'ta çalışmaz.
 * 
 * Alternatif yaklaşımlar:
 * 1. Cloudflare Pages Functions kullanın (JavaScript/TypeScript)
 * 2. Flask uygulamasını ayrı bir sunucuda host edin ve Workers'tan proxy yapın
 * 3. Uygulamayı JavaScript'e port edin
 */

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    
    // Static asset handling
    if (url.pathname.startsWith('/assets/')) {
      return env.ASSETS.fetch(request);
    }

    // API endpoint'leri için proxy yapabilirsiniz
    // Örnek: Flask uygulamanız başka bir yerde çalışıyorsa
    const backendUrl = env.BACKEND_URL || 'https://your-backend-url.com';
    
    // CORS headers
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    };

    // Handle CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        headers: corsHeaders,
      });
    }

    try {
      // Proxy request to backend
      const backendRequest = new Request(backendUrl + url.pathname + url.search, {
        method: request.method,
        headers: request.headers,
        body: request.body,
      });

      const response = await fetch(backendRequest);
      
      // Add CORS headers to response
      const newResponse = new Response(response.body, response);
      Object.entries(corsHeaders).forEach(([key, value]) => {
        newResponse.headers.set(key, value);
      });

      return newResponse;
    } catch (error) {
      return new Response(
        JSON.stringify({
          error: 'Backend connection failed',
          message: error.message,
        }),
        {
          status: 502,
          headers: {
            'Content-Type': 'application/json',
            ...corsHeaders,
          },
        }
      );
    }
  },
};
