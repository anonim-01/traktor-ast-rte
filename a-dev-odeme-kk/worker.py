from js import Response


async def on_fetch(request, env):
    """
    Cloudflare Python Worker - Minimal Test
    GitHub: https://github.com/anonim-01/traktor-ast-rte.git
    """
    return Response.new("Worker is running! Ready for deployment.", status=200)
