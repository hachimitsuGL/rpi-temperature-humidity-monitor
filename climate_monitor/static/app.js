const statusText = {
    cold: ["低温", "cold"],
    hot: ["高温", "warning"],
    comfortable: ["快適", "comfort"],
    dry: ["乾燥", "warning"],
    humid: ["高湿度", "warning"],
    unknown: ["未取得", ""]
};

let historyData = [];

function niceRange(values, minimumPadding) {
    if (!values.length) return [0, 1];
    let min = Math.min(...values);
    let max = Math.max(...values);
    if (min === max) {
        min -= minimumPadding;
        max += minimumPadding;
    } else {
        const pad = Math.max((max - min) * 0.15, minimumPadding);
        min -= pad;
        max += pad;
    }
    return [min, max];
}

function drawHistoryChart() {
    const canvas = document.getElementById('history-chart');
    const rect = canvas.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    const width = Math.max(320, rect.width);
    const height = Math.max(200, rect.height);

    canvas.width = Math.round(width * dpr);
    canvas.height = Math.round(height * dpr);

    const ctx = canvas.getContext('2d');
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, width, height);

    const left = 45;
    const right = 45;
    const top = 14;
    const bottom = 32;
    const plotW = width - left - right;
    const plotH = height - top - bottom;

    ctx.font = '11px -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif';
    ctx.lineWidth = 1;

    if (historyData.length < 2) {
        ctx.fillStyle = '#6b7280';
        ctx.textAlign = 'center';
        ctx.fillText('データを蓄積中...', width / 2, height / 2);
        return;
    }

    const temps = historyData.map(p => p.temperature);
    const hums = historyData.map(p => p.humidity);
    const [tMin, tMax] = niceRange(temps, 1);
    const [hMin, hMax] = niceRange(hums, 5);

    const x = i => left + (i / (historyData.length - 1)) * plotW;
    const yTemp = v => top + (1 - (v - tMin) / (tMax - tMin)) * plotH;
    const yHum = v => top + (1 - (v - hMin) / (hMax - hMin)) * plotH;

    // 横グリッドと左右の目盛
    for (let i = 0; i <= 4; i++) {
        const yy = top + (i / 4) * plotH;
        ctx.strokeStyle = '#e5e7eb';
        ctx.beginPath();
        ctx.moveTo(left, yy);
        ctx.lineTo(width - right, yy);
        ctx.stroke();

        const tv = tMax - (i / 4) * (tMax - tMin);
        const hv = hMax - (i / 4) * (hMax - hMin);

        ctx.fillStyle = '#9a3412';
        ctx.textAlign = 'right';
        ctx.textBaseline = 'middle';
        ctx.fillText(tv.toFixed(1), left - 7, yy);

        ctx.fillStyle = '#1d4ed8';
        ctx.textAlign = 'left';
        ctx.fillText(hv.toFixed(0), width - right + 7, yy);
    }

    function drawLine(key, mapY, color) {
        ctx.strokeStyle = color;
        ctx.lineWidth = 2;
        ctx.lineJoin = 'round';
        ctx.lineCap = 'round';
        ctx.beginPath();
        historyData.forEach((p, i) => {
            const xx = x(i);
            const yy = mapY(p[key]);
            if (i === 0) ctx.moveTo(xx, yy);
            else ctx.lineTo(xx, yy);
        });
        ctx.stroke();
    }

    drawLine('temperature', yTemp, '#e76f51');
    drawLine('humidity', yHum, '#3b82f6');

    // X軸の時刻（開始・中央・現在）
    const first = historyData[0].time;
    const mid = historyData[Math.floor((historyData.length - 1) / 2)].time;
    const last = historyData[historyData.length - 1].time;
    ctx.fillStyle = '#6b7280';
    ctx.textBaseline = 'top';

    ctx.textAlign = 'left';
    ctx.fillText(first, left, height - bottom + 8);
    ctx.textAlign = 'center';
    ctx.fillText(mid, left + plotW / 2, height - bottom + 8);
    ctx.textAlign = 'right';
    ctx.fillText(last, width - right, height - bottom + 8);
}

async function refresh() {
    try {
        const [statusResponse, historyResponse] = await Promise.all([
            fetch('/api/status', {cache: 'no-store'}),
            fetch('/api/history', {cache: 'no-store'})
        ]);
        const d = await statusResponse.json();
        historyData = await historyResponse.json();

        document.getElementById('temperature').textContent =
            d.temperature === null ? '--.-℃' : d.temperature.toFixed(1) + '℃';
        document.getElementById('humidity').textContent =
            d.humidity === null ? '--.-%' : d.humidity.toFixed(1) + '%';

        const ts = statusText[d.temp_status] || statusText.unknown;
        const hs = statusText[d.hum_status] || statusText.unknown;

        const te = document.getElementById('temp-status');
        te.textContent = ts[0];
        te.className = 'status ' + ts[1];

        const he = document.getElementById('hum-status');
        he.textContent = hs[0];
        he.className = 'status ' + hs[1];

        document.getElementById('comfort-range').textContent =
            `温度 ${d.min_t}～${d.max_t}℃ / 湿度 ${d.min_h}～${d.max_h}%`;
        document.getElementById('updated-at').textContent = d.updated_at || '--:--:--';
        drawHistoryChart();
    } catch (e) {
        document.getElementById('updated-at').textContent = '接続エラー';
    }
}

window.addEventListener('resize', drawHistoryChart);
refresh();
setInterval(refresh, 2000);
