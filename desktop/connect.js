document.getElementById('connection').addEventListener('submit', async event => {
  event.preventDefault();
  const status = document.getElementById('status');
  try {
    await window.garda.connect(document.getElementById('url').value);
    status.textContent = 'Menghubungkan…';
  } catch {
    status.textContent = 'Alamat tidak valid. Gunakan HTTPS atau localhost untuk pengujian.';
  }
});
