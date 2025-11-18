/**
 * Cloudflare Containers Worker
 * Flask uygulaması için container yönetimi
 */

import { Container, getContainer } from "@cloudflare/containers";

/**
 * Flask Container Tanımı
 */
export class FlaskContainer extends Container {
  defaultPort = 8000; // Gunicorn port
  sleepAfter = "15m"; // 15 dakika aktivite yoksa uyut
  maxConcurrentRequests = 100; // Maksimum eşzamanlı istek
  memoryLimit = "512MB"; // Bellek limiti
  cpuLimit = 1.0; // CPU limiti (1 core)
}

/**
 * Worker Entry Point
 */
export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    
    // Health check endpoint
    if (url.pathname === "/__health") {
      return new Response("OK", {
        status: 200,
        headers: { "Content-Type": "text/plain" }
      });
    }

    try {
      // Session ID'yi cookie'den veya header'dan al
      const sessionId = request.headers.get("X-Session-ID") || 
                       getCookie(request, "session") || 
                       "default";

      // Container instance'ı al veya oluştur
      const container = getContainer(env.FLASK_CONTAINER, sessionId);

      // İsteği container'a ilet
      const response = await container.fetch(request);

      // Response headers ekle
      const newResponse = new Response(response.body, response);
      newResponse.headers.set("X-Container-ID", sessionId);
      newResponse.headers.set("X-Served-By", "Cloudflare-Containers");

      return newResponse;
    } catch (error) {
      console.error("Container error:", error);
      
      return new Response(
        JSON.stringify({
          error: "Container unavailable",
          message: error.message,
          timestamp: new Date().toISOString()
        }),
        {
          status: 503,
          headers: {
            "Content-Type": "application/json",
            "Retry-After": "5"
          }
        }
      );
    }
  },

  /**
   * Scheduled handler - container bakımı için
   */
  async scheduled(event, env, ctx) {
    // Eski container instance'larını temizle
    console.log("Running scheduled container maintenance");
  }
};

/**
 * Cookie'den değer al
 */
function getCookie(request, name) {
  const cookieHeader = request.headers.get("Cookie");
  if (!cookieHeader) return null;

  const cookies = cookieHeader.split(";").map(c => c.trim());
  const cookie = cookies.find(c => c.startsWith(`${name}=`));
  
  return cookie ? cookie.split("=")[1] : null;
}
