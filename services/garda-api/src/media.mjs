export function createMediaClient(baseUrl, username, password) {
  const base = new URL(baseUrl);
  if (!['http:', 'https:'].includes(base.protocol)) throw new Error('Invalid MediaMTX URL');
  const authorization = 'Basic ' + Buffer.from(username + ':' + password).toString('base64');
  async function request(method, path, payload) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 6000);
    try {
      const response = await fetch(new URL(path, base), {
        method,
        headers: { Authorization: authorization, ...(payload ? { 'Content-Type': 'application/json' } : {}) },
        body: payload ? JSON.stringify(payload) : undefined,
        signal: controller.signal
      });
      if (!response.ok) {
        const error = new Error('Media gateway unavailable (' + response.status + ')');
        error.status = response.status;
        throw error;
      }
      return response.status === 204 ? {} : await response.json();
    } finally {
      clearTimeout(timer);
    }
  }
  const path = value => encodeURIComponent(value);
  return {
    getConfig: name => request('GET', '/v3/config/paths/get/' + path(name)),
    addCamera: (name, source) => request('POST', '/v3/config/paths/add/' + path(name), {
      source, sourceOnDemand: false, rtspTransport: 'tcp', record: true
    }),
    cameraStatus: name => request('GET', '/v3/paths/get/' + path(name)),
    recordings: name => request('GET', '/v3/recordings/get/' + path(name))
  };
}
