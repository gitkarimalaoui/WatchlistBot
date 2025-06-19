const API_URL = '/watchlist/live';
const tableBody = document.querySelector('#tickersTable tbody');
const pumpCount = document.getElementById('pumpCount');
const scoreCount = document.getElementById('scoreCount');
const totalCount = document.getElementById('totalCount');
const modal = document.getElementById('detailModal');
const modalText = document.getElementById('detailText');
const closeBtn = document.querySelector('.close');

closeBtn.onclick = () => { modal.style.display = 'none'; };
window.onclick = (e) => { if (e.target === modal) modal.style.display = 'none'; };

function updateTable(data) {
  tableBody.innerHTML = '';
  let pumps = 0;
  let score60 = 0;
  data.forEach(item => {
    if (item.isPump) pumps += 1;
    if (item.score >= 60) score60 += 1;
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${item.ticker}</td>
      <td>${item.price}</td>
      <td>${item.changePercent}</td>
      <td>${item.volumeRatio}</td>
      <td>${item.rsi}</td>
      <td class="${item.emaSignal === 'bullish' ? 'badge-bullish' : 'badge-bearish'}">${item.emaSignal}</td>
      <td class="${item.score >= 80 ? 'score-high' : item.score >= 60 ? 'score-mid' : 'score-low'}">${item.score}</td>
      <td>${item.isPump ? '<span class="badge-pump">PUMP</span>' : ''}</td>
      <td>${item.lastUpdate}</td>`;
    row.addEventListener('click', () => {
      modalText.textContent = JSON.stringify(item, null, 2);
      modal.style.display = 'block';
    });
    tableBody.appendChild(row);
  });
  pumpCount.textContent = `Pumps: ${pumps}`;
  scoreCount.textContent = `Score ≥ 60: ${score60}`;
  totalCount.textContent = `Total: ${data.length}`;
}

async function fetchData() {
  try {
    const res = await fetch(API_URL);
    if (!res.ok) throw new Error('Network response was not ok');
    const json = await res.json();
    updateTable(json);
  } catch (e) {
    console.error('Fetch error:', e);
  }
}

fetchData();
setInterval(fetchData, 5000);
