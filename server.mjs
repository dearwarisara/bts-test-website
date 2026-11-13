import http from 'node:http';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { stat } from 'node:fs/promises';
import { createReadStream } from 'node:fs';

const root = fileURLToPath(new URL('./dist/', import.meta.url));
const port = Number(process.env.PORT || 4173);
const host = process.env.HOST || '127.0.0.1';
const types = {
  '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8', '.json': 'application/json; charset=utf-8',
  '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg', '.webp': 'image/webp', '.ico': 'image/x-icon',
  '.woff': 'font/woff', '.woff2': 'font/woff2', '.mp4': 'video/mp4',
  '.pdf': 'application/pdf', '.glb': 'model/gltf-binary'
};
const reply = (res, code, message) => {
  res.writeHead(code, { 'Content-Type': 'text/plain; charset=utf-8' });
  res.end(message);
};

const server = http.createServer(async (req, res) => {
  if (!['GET', 'HEAD'].includes(req.method)) return reply(res, 405, 'Method not allowed');
  let pathname;
  try { pathname = decodeURIComponent(new URL(req.url, 'http://localhost').pathname); }
  catch { return reply(res, 400, 'Invalid URL'); }
  if (pathname.includes('\0')) return reply(res, 400, 'Invalid URL');
  let file = path.resolve(root, '.' + pathname);
  if (file !== path.resolve(root) && !file.startsWith(root)) return reply(res, 403, 'Forbidden');
  try {
    if ((await stat(file)).isDirectory()) file = path.join(file, 'index.html');
    const info = await stat(file);
    if (!info.isFile()) return reply(res, 404, 'Page not found');
    res.writeHead(200, {
      'Content-Type': types[path.extname(file).toLowerCase()] || 'application/octet-stream',
      'Content-Length': info.size,
      'Cache-Control': 'no-cache'
    });
    if (req.method === 'HEAD') return res.end();
    createReadStream(file).on('error', () => res.destroy()).pipe(res);
  } catch { reply(res, 404, 'Page not found'); }
});
server.on('error', error => {
  console.error(error.code === 'EADDRINUSE' ? `Port ${port} is in use. Set PORT to another port.` : error.message);
  process.exitCode = 1;
});
server.listen(port, host, () => {
  console.log(`BTS Group is running at http://${host}:${port}`);
  console.log(`3D history: http://${host}:${port}/th/about/our-history/`);
});
