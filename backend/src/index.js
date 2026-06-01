export default {
  async fetch(request) {
    const { searchParams } = new URL(request.url);
    const videoUrl = searchParams.get('url');
    if (!videoUrl) return new Response('URL missing', { status: 400 });
    
    const apiRes = await fetch('https://api.cobalt.tools/api/json', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      body: JSON.stringify({ url: videoUrl })
    });
    const data = await apiRes.json();
    return Response.json(data, {
      headers: { 'Access-Control-Allow-Origin': '*' }
    });
  }
}
