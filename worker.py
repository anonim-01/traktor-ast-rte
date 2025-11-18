from workers import WorkerEntrypoint, Response


class Default(WorkerEntrypoint):
    async def fetch(self, request):
        url = request.url

        # Static asset handling
        if url.pathname.startswith('/assets/'):
            return await self.env.ASSETS.fetch(request)

        # API endpoint'leri için proxy yapabilirsiniz
        # Örnek: Flask uygulamanız başka bir yerde çalışıyorsa
        backend_url = self.env.BACKEND_URL or 'https://your-backend-url.com'

        # CORS headers
        cors_headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        }

        # Handle CORS preflight
        if request.method == 'OPTIONS':
            return Response(None, headers=cors_headers)

        try:
            # Proxy request to backend
            backend_request = Request(
                backend_url + url.pathname + url.search,
                method=request.method,
                headers=request.headers,
                body=request.body,
            )

            response = await fetch(backend_request)

            # Add CORS headers to response
            new_response = Response(response.body, response)
            for key, value in cors_headers.items():
                new_response.headers.set(key, value)

            return new_response
        except Exception as error:
            return Response(
                '{"error": "Backend connection failed", "message": "' + str(error) + '"}',
                status=502,
                headers={
                    'Content-Type': 'application/json',
                    **cors_headers,
                },
            )
