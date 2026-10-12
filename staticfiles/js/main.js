/* ═══════════════════════════════════════════════════════
   School Management System – Main JavaScript
   ═══════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', function () {

  // ── Sidebar Toggle (Mobile) ───────────────────────────
  const sidebar  = document.getElementById('sidebar');
  const overlay  = document.getElementById('sidebarOverlay');
  const menuBtn  = document.getElementById('menuToggle');

  if (menuBtn) {
    menuBtn.addEventListener('click', () => {
      sidebar.classList.toggle('open');
      overlay.classList.toggle('show');
    });
  }
  if (overlay) {
    overlay.addEventListener('click', () => {
      sidebar.classList.remove('open');
      overlay.classList.remove('show');
    });
  }

  // ── Active Nav Link ───────────────────────────────────
  const currentPath = window.location.pathname;
  document.querySelectorAll('.nav-link').forEach(link => {
    if (link.getAttribute('href') === currentPath ||
        (link.getAttribute('href') !== '/' && currentPath.startsWith(link.getAttribute('href')))) {
      link.classList.add('active');
    }
  });

  // ── Auto-dismiss alerts ───────────────────────────────
  document.querySelectorAll('.alert').forEach(alert => {
    setTimeout(() => {
      alert.style.transition = 'opacity 0.5s ease';
      alert.style.opacity = '0';
      setTimeout(() => alert.remove(), 500);
    }, 4000);
  });

  // ── Fade In Cards ─────────────────────────────────────
  document.querySelectorAll('.fade-in').forEach((el, i) => {
    el.style.animationDelay = (i * 0.06) + 's';
  });

  // ── Stat counter animation ────────────────────────────
  document.querySelectorAll('.stat-value-anim').forEach(el => {
    const target = parseFloat(el.dataset.target || el.textContent.replace(/[^\d.]/g, ''));
    const isFloat = el.dataset.target && el.dataset.target.includes('.');
    const prefix  = el.dataset.prefix || '';
    const suffix  = el.dataset.suffix || '';
    let current   = 0;
    const step    = target / 60;
    const timer   = setInterval(() => {
      current += step;
      if (current >= target) {
        current = target;
        clearInterval(timer);
      }
      el.textContent = prefix + (isFloat ? current.toFixed(2) : Math.floor(current).toLocaleString()) + suffix;
    }, 20);
  });

  // ── Confirm Delete ────────────────────────────────────
  document.querySelectorAll('[data-confirm]').forEach(btn => {
    btn.addEventListener('click', function (e) {
      if (!confirm(this.dataset.confirm || 'Are you sure?')) {
        e.preventDefault();
      }
    });
  });

  // ── Table Row Click Link ──────────────────────────────
  document.querySelectorAll('tr[data-href]').forEach(row => {
    row.style.cursor = 'pointer';
    row.addEventListener('click', () => {
      window.location.href = row.dataset.href;
    });
  });

  // ── Search live filter ────────────────────────────────
  const liveSearch = document.getElementById('liveSearch');
  if (liveSearch) {
    liveSearch.addEventListener('input', function () {
      const q = this.value.toLowerCase();
      document.querySelectorAll('tbody tr').forEach(row => {
        row.style.display = row.textContent.toLowerCase().includes(q) ? '' : 'none';
      });
    });
  }

  // ── Fee status auto-colour ────────────────────────────
  document.querySelectorAll('.fee-amount').forEach(el => {
    const val = parseFloat(el.dataset.paid || 0);
    const total = parseFloat(el.dataset.total || 1);
    const pct = (val / total) * 100;
    const bar = el.querySelector('.progress-bar');
    if (bar) {
      bar.style.width = Math.min(pct, 100) + '%';
      bar.style.background = pct >= 100 ? '#10B981' : pct > 0 ? '#F59E0B' : '#EF4444';
    }
  });

});

// ──  Dashboard Charts init (called from dashboard template) ──
function initDashboardCharts(classData, monthlyFees, monthsLabels) {

  // Class-wise distribution - Doughnut
  const classCtx = document.getElementById('classChart');
  if (classCtx && classData.length) {
    const colors = ['#2563EB','#06B6D4','#10B981','#F59E0B','#EF4444',
                    '#8B5CF6','#EC4899','#14B8A6','#F97316','#6366F1',
                    '#A3E635','#FB923C'];
    new Chart(classCtx, {
      type: 'doughnut',
      data: {
        labels: classData.map(d => 'Class ' + d.student_class),
        datasets: [{
          data:            classData.map(d => d.count),
          backgroundColor: colors.slice(0, classData.length),
          borderWidth: 0,
          hoverOffset: 6,
        }]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: {
          legend: { position: 'right', labels: { boxWidth: 10, font: { size: 11 } } }
        },
        cutout: '65%'
      }
    });
  }

  // Monthly fees - Bar chart
  const feeCtx = document.getElementById('feeChart');
  if (feeCtx) {
    new Chart(feeCtx, {
      type: 'bar',
      data: {
        labels: monthsLabels.map(m => m.slice(0,3)),
        datasets: [{
          label: 'Fees Collected (PKR)',
          data: monthlyFees,
          backgroundColor: 'rgba(37,99,235,0.15)',
          borderColor: '#2563EB',
          borderWidth: 2,
          borderRadius: 6,
          hoverBackgroundColor: 'rgba(37,99,235,0.3)',
        }]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: {
            beginAtZero: true,
            grid: { color: 'rgba(0,0,0,0.05)' },
            ticks: { font: { size: 11 } }
          },
          x: {
            grid: { display: false },
            ticks: { font: { size: 11 } }
          }
        }
      }
    });
  }
}
