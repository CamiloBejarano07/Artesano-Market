document.addEventListener('DOMContentLoaded', function() {
  const data = window.DASHBOARD_DATA || {};

  const charts = {};

  function hideAll() {
    document.querySelectorAll('.chart-panel').forEach(el => {
      el.style.display = 'none';
      el.classList.remove('active');
    });
  }

  function showChart(name) {
    hideAll();
    const panel = document.getElementById('panel-' + name);
    if (!panel) return;
    panel.style.display = 'block';
    panel.classList.add('active');
    // inicializar chart si no existe
    if (!charts[name]) {
      initChart(name);
    }
  }

  function initChart(name) {
    if (name === 'users') {
      const ctx = document.getElementById('chart-users').getContext('2d');
      charts.users = new Chart(ctx, {
        type: 'line',
        data: {
          labels: data.monthly_labels || [],
          datasets: [{
            label: 'Usuarios registrados',
            data: data.monthly_users || [],
            backgroundColor: 'rgba(52,152,219,0.15)',
            borderColor: 'rgba(52,152,219,1)',
            fill: true,
            tension: 0.3
          }]
        },
        options: { responsive: true, plugins: { legend: { display: true } }, scales: { y: { beginAtZero: true } } }
      });
    }

    if (name === 'ventas') {
      const ctx = document.getElementById('chart-ventas').getContext('2d');
      charts.ventas = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: data.monthly_labels || [],
          datasets: [{
            label: 'Total ventas',
            data: data.monthly_ventas || [],
            backgroundColor: 'rgba(243,156,18,0.6)'
          }]
        },
        options: { responsive: true, scales: { y: { beginAtZero: true } } }
      });
    }

    if (name === 'productos') {
      const ctx = document.getElementById('chart-productos').getContext('2d');
      charts.productos = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: data.productos_labels || [],
          datasets: [{ data: data.productos_counts || [], backgroundColor: ['#3498db','#2ecc71','#e74c3c','#9b59b6','#f1c40f'] }]
        },
        options: { responsive: true }
      });
    }

    if (name === 'vendedores') {
      const ctx = document.getElementById('chart-vendedores').getContext('2d');
      charts.vendedores = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: data.vendedores_labels || [],
          datasets: [{ label: 'Ventas', data: data.vendedores_totals || [], backgroundColor: 'rgba(155,89,182,0.7)' }]
        },
        options: { responsive: true, indexAxis: 'y', scales: { x: { beginAtZero: true } } }
      });
    }

    if (name === 'visitors') {
      // Inicializar mapa (Leaflet)
      try {
        const mapEl = document.getElementById('map-visitors');
        if (mapEl && !mapEl.dataset.inited) {
          const map = L.map('map-visitors').setView([20,0], 2);
          L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 18,
            attribution: '© OpenStreetMap'
          }).addTo(map);
          mapEl.dataset.inited = '1';
        }
      } catch (e) {
        console.warn('Leaflet no disponible', e);
      }
    }
  }

  // Inicializar mini-gráficas dentro de las tarjetas (sparklines)
  function initMiniCharts() {
    try {
      // Usuarios mini
      const mu = document.getElementById('mini-users');
      if (mu) {
        new Chart(mu.getContext('2d'), {
          type: 'line', data: { labels: data.monthly_labels || [], datasets: [{ data: data.monthly_users || [], borderColor: 'rgba(255,255,255,0.9)', backgroundColor: 'rgba(255,255,255,0.15)', fill:true, tension:0.3 }] }, options: { responsive: true, maintainAspectRatio: false, plugins:{legend:{display:false}}, elements:{point:{radius:0}}, scales:{x:{display:false}, y:{display:false}} }
        });
      }

      const mv = document.getElementById('mini-ventas');
      if (mv) {
        new Chart(mv.getContext('2d'), {
          type: 'line', data: { labels: data.monthly_labels || [], datasets: [{ data: data.monthly_ventas || [], borderColor: 'rgba(255,255,255,0.9)', backgroundColor: 'rgba(255,255,255,0.15)', fill:true, tension:0.3 }] }, options: { responsive: true, maintainAspectRatio: false, plugins:{legend:{display:false}}, elements:{point:{radius:0}}, scales:{x:{display:false}, y:{display:false}} }
        });
      }

      const mp = document.getElementById('mini-productos');
      if (mp) {
        new Chart(mp.getContext('2d'), {
          type: 'doughnut', data: { labels: data.productos_labels || [], datasets: [{ data: (data.productos_counts||[]).slice(0,3), backgroundColor:['rgba(255,255,255,0.9)','rgba(255,255,255,0.7)','rgba(255,255,255,0.5)'] }] }, options: { responsive:true, maintainAspectRatio:false, plugins:{legend:{display:false}} }
        });
      }

      const mvend = document.getElementById('mini-vendedores');
      if (mvend) {
        new Chart(mvend.getContext('2d'), {
          type: 'bar', data: { labels: (data.vendedores_labels||[]).slice(0,6), datasets: [{ data: (data.vendedores_totals||[]).slice(0,6), backgroundColor: 'rgba(255,255,255,0.85)'}] }, options:{responsive:true, maintainAspectRatio:false, plugins:{legend:{display:false}}, scales:{x:{display:false}, y:{display:false}} }
        });
      }
    } catch (e) {
      console.warn('Error inicializando mini-gráficas', e);
    }
  }

  // Botones
  document.querySelectorAll('.detail-btn').forEach(btn => {
    btn.addEventListener('click', function(e){
      e.preventDefault();
      const target = this.dataset.target;
      showChart(target);
      // marcar visualmente
      document.querySelectorAll('.detail-btn').forEach(b=>b.classList.remove('active'));
      this.classList.add('active');
    });
  });

  // Mostrar la gráfica por defecto (ventas)
  const defaultBtn = document.querySelector('.detail-btn[data-target="ventas"]');
  if (defaultBtn) defaultBtn.click();
  // Inicializar mini-gráficas al cargar
  initMiniCharts();
});
