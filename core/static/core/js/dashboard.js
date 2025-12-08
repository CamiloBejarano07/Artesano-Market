document.addEventListener('DOMContentLoaded', function () {
  const DATA = window.DASHBOARD_DATA || {};

  // Helper: hide all chart panels
  function hideAllPanels() {
    document.querySelectorAll('.chart-panel').forEach(p => p.style.display = 'none');
  }

  // Show target panel by id (without 'panel-' prefix allowed)
  function showPanel(name) {
    hideAllPanels();
    const id = name.startsWith('panel-') ? name : `panel-${name}`;
    const panel = document.getElementById(id);
    if (panel) panel.style.display = 'block';
  }

  // Initialize small mini charts in cards (if any)
  function initMiniCharts() {
    const miniUsers = document.getElementById('mini-users');
    if (miniUsers && DATA.monthly_users) {
      new Chart(miniUsers.getContext('2d'), {
        type: 'line',
        data: { labels: DATA.monthly_labels || [], datasets: [{ data: DATA.monthly_users, borderColor: '#fff', backgroundColor: 'rgba(255,255,255,0.15)', fill: true, pointRadius: 0 }] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { display: false }, y: { display: false } } }
      });
    }

    const miniVendedores = document.getElementById('mini-vendedores');
    if (miniVendedores && DATA.vendedores_totals) {
      new Chart(miniVendedores.getContext('2d'), {
        type: 'bar',
        data: { labels: DATA.vendedores_labels || [], datasets: [{ data: DATA.vendedores_totals, backgroundColor: 'rgba(255,255,255,0.35)' }] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { display: false }, y: { display: false } } }
      });
    }

    const miniProductos = document.getElementById('mini-productos');
    if (miniProductos && DATA.productos_counts) {
      new Chart(miniProductos.getContext('2d'), {
        type: 'doughnut',
        data: { labels: DATA.productos_labels || [], datasets: [{ data: DATA.productos_counts, backgroundColor: ['#ffc107','#17a2b8','#28a745','#dc3545'] }] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
      });
    }

    const miniVentas = document.getElementById('mini-ventas');
    if (miniVentas && DATA.monthly_ventas) {
      new Chart(miniVentas.getContext('2d'), {
        type: 'line',
        data: { labels: DATA.monthly_labels || [], datasets: [{ data: DATA.monthly_ventas, borderColor: '#fff', backgroundColor: 'rgba(255,255,255,0.12)', fill: true, pointRadius: 0 }] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { display: false }, y: { display: false } } }
      });
    }
  }

  // Create full charts for panels
  let charts = {};

  function createUsersChart() {
    const ctx = document.getElementById('chart-users');
    if (!ctx) return;
    charts.users = new Chart(ctx.getContext('2d'), {
      type: 'line',
      data: { labels: DATA.monthly_labels || [], datasets: [{ label: 'Usuarios', data: DATA.monthly_users || [], borderColor: '#17a2b8', backgroundColor: 'rgba(23,162,184,0.15)', fill: true }] },
      options: { responsive: true, maintainAspectRatio: false }
    });
  }

  function createVentasChart() {
    const ctx = document.getElementById('chart-ventas');
    if (!ctx) return;
    charts.ventas = new Chart(ctx.getContext('2d'), {
      type: 'bar',
      data: { labels: DATA.monthly_labels || [], datasets: [{ label: 'Ventas', data: DATA.monthly_ventas || [], backgroundColor: '#dc3545' }] },
      options: { responsive: true, maintainAspectRatio: false }
    });
  }

  function createProductosChart() {
    const ctx = document.getElementById('chart-productos');
    if (!ctx) return;
    charts.productos = new Chart(ctx.getContext('2d'), {
      type: 'pie',
      data: { labels: DATA.productos_labels || [], datasets: [{ data: DATA.productos_counts || [], backgroundColor: ['#ffc107','#17a2b8','#28a745','#6f42c1'] }] },
      options: { responsive: true, maintainAspectRatio: false }
    });
  }

  function createVendedoresChart() {
    const ctx = document.getElementById('chart-vendedores');
    if (!ctx) return;
    charts.vendedores = new Chart(ctx.getContext('2d'), {
      type: 'bar',
      data: { labels: DATA.vendedores_labels || [], datasets: [{ label: 'Total ventas', data: DATA.vendedores_totals || [], backgroundColor: '#28a745' }] },
      options: { responsive: true, maintainAspectRatio: false }
    });
  }

  function initMapVisitors() {
    const el = document.getElementById('map-visitors');
    if (!el || !window.L) return;
    // Default world view
    const map = L.map(el).setView([20,0], 2);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 18 }).addTo(map);
    // If DATA.visitors exists as array of {lat,lon,label} add markers
    if (Array.isArray(DATA.visitors)) {
      DATA.visitors.forEach(v => {
        if (v && v.lat && v.lon) L.marker([v.lat, v.lon]).addTo(map).bindPopup(v.label || 'Visitante');
      });
    }
  }

  // Attach click handlers to detail buttons
  function attachDetailHandlers() {
    document.querySelectorAll('.detail-btn').forEach(btn => {
      btn.addEventListener('click', function (ev) {
        ev.preventDefault();
        const target = btn.getAttribute('data-target');
        if (!target) return;
        showPanel(target);
        // initialize the corresponding chart lazily
        switch (target) {
          case 'users': if (!charts.users) createUsersChart(); break;
          case 'ventas': if (!charts.ventas) createVentasChart(); break;
          case 'productos': if (!charts.productos) createProductosChart(); break;
          case 'vendedores': if (!charts.vendedores) createVendedoresChart(); break;
          case 'visitors': initMapVisitors(); break;
        }
      });
    });
  }

  // Initialize everything
  initMiniCharts();
  attachDetailHandlers();

  // Optionally show users panel by default
  // showPanel('users');
});
