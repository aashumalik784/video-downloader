import { serve } from "https://deno.land/std@0.224.0/http/server.ts";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "POST, OPTIONS", 
  "Access-Control-Allow-Headers": "Content-Type",
};

serve(async (req: Request) => {
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const { url } = await req.json();
    if (!url) throw new Error("URL is required");

    const command = new Deno.Command("yt-dlp", {
      args: ["-j", "--no-warnings", "-f", "best[ext=mp4]/best", url],
      stdout: "piped",
      stderr: "piped",
    });

    const { code, stdout, stderr } = await command.output();
    if (code !== 0) {
      const errorMsg = new TextDecoder().decode(stderr);
      throw new Error(`yt-dlp error: ${errorMsg}`);
    }

    const info = JSON.parse(new TextDecoder().decode(stdout));
    
    return new Response(JSON.stringify({
      success: true,
      download_url: info.url,
      title: info.title,
    }), { headers: { ...corsHeaders, "Content-Type": "application/json" } });

  } catch (e) {
    return new Response(JSON.stringify({ error: e.message }), {
      status: 500,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
});
