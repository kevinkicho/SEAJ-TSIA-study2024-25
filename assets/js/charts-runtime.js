/* =====================================================================
   Charts runtime — FX conversion (Frankfurter), table/chart toggle,
   filter UI, and ECharts rendering.

   Expected page markup per chart:

     <div class="view-toggle" data-target="KEY">
       <button class="active" data-view="table">Table</button>
       <button data-view="chart">Chart</button>
     </div>
     <div class="chart-view"
          data-chart="KEY"
          data-metric="revenue"
          data-currency="USD"
          data-scale="log"></div>
     <table class="chartable" data-chart-ref="KEY"> ... </table>

   The runtime:
   1. Wires toggle clicks to show/hide the table vs the chart container.
   2. On first chart activation, loads FX rates from Frankfurter (fallback
      to a hardcoded table), builds filter UI inside the .chart-view, and
      renders the ECharts instance in a sub-div.
   3. Filter changes re-project the data and call setOption with merge.
   ===================================================================== */

(function () {
  'use strict';

  const LAYERS = ['Materials','Equipment','EDA/IP','Fabless','IDM','Foundry','OSAT','Distribution','Research'];
  const REGIONS = ['TW','JP','US','EU','Other'];
  const METRICS = [
    { key: 'revenue',      label: 'Revenue',              type: 'money' },
    { key: 'opIncome',     label: 'Operating Income',     type: 'money' },
    { key: 'netIncome',    label: 'Net Income',           type: 'money' },
    { key: 'totalAssets',  label: 'Total Assets',         type: 'money' },
    { key: 'totalEquity',  label: 'Total Equity',         type: 'money' },
    { key: 'revenueYoy',   label: 'Revenue YoY %',        type: 'pct'   },
    { key: 'grossMargin',  label: 'Gross Margin %',       type: 'pct'   },
    { key: 'opMargin',     label: 'Operating Margin %',   type: 'pct'   },
    { key: 'netMargin',    label: 'Net Margin %',         type: 'pct'   }
  ];
  const CURRENCIES = ['USD', 'JPY', 'EUR', 'TWD', 'GBP', 'KRW', 'CNY'];
  const LAYER_COLORS = {
    'Foundry':       '#e63946',
    'Equipment':     '#6a4c93',
    'Fabless':       '#2a9d8f',
    'OSAT':          '#fb8500',
    'IDM':           '#d62828',
    'EDA/IP':        '#457b9d',
    'Materials':     '#606c38',
    'Distribution':  '#8d99ae',
    'Research':      '#495057'
  };

  const fxState = {
    rates: null,             // {CUR: units-of-CUR per 1 USD}
    asOf: null,
    source: null,
    loading: null
  };
  const chartInstances = {};

  function loadFXOnce() {
    if (fxState.loading) return fxState.loading;
    fxState.loading = fetch('https://api.frankfurter.dev/v1/latest?base=USD')
      .then(r => r.ok ? r.json() : Promise.reject())
      .then(d => {
        fxState.rates = Object.assign({ USD: 1 }, window.FX_FALLBACK.rates, d.rates);
        // TWD is NOT in ECB daily reference rates — always use fallback
        fxState.rates.TWD = window.FX_FALLBACK.rates.TWD;
        fxState.asOf = d.date;
        fxState.source = 'frankfurter.dev (ECB) ' + d.date + ' + TWD hardcoded (' + window.FX_FALLBACK.asOf + ')';
      })
      .catch(() => {
        fxState.rates = Object.assign({}, window.FX_FALLBACK.rates);
        fxState.asOf = window.FX_FALLBACK.asOf;
        fxState.source = 'fallback table (' + window.FX_FALLBACK.asOf + ', Frankfurter unreachable)';
      });
    return fxState.loading;
  }

  function convert(value, srcCur, tgtCur) {
    if (value == null || !fxState.rates) return null;
    if (srcCur === tgtCur) return value;
    const srcPerUSD = fxState.rates[srcCur];
    const tgtPerUSD = fxState.rates[tgtCur];
    if (!srcPerUSD || !tgtPerUSD) return null;
    return (value / srcPerUSD) * tgtPerUSD;
  }

  const CUR_SYMBOL = { USD: '$', TWD: 'NT$', JPY: '¥', EUR: '€', GBP: '£', KRW: '₩', CNY: '¥' };

  function fmtMoney(value, cur) {
    if (value == null || isNaN(value)) return '—';
    const abs = Math.abs(value);
    const sign = value < 0 ? '-' : '';
    const sym = CUR_SYMBOL[cur] || '';
    // value is in millions; scale to B or T
    let scaled, suffix;
    if (abs >= 1000000) { scaled = abs / 1000000; suffix = 'T'; }
    else if (abs >= 1000) { scaled = abs / 1000; suffix = 'B'; }
    else { scaled = abs; suffix = 'M'; }
    const precision = scaled >= 100 ? 0 : scaled >= 10 ? 1 : 2;
    return sign + sym + scaled.toFixed(precision) + suffix;
  }

  function fmtPct(v) {
    if (v == null || isNaN(v)) return '—';
    return (v >= 0 ? '+' : '') + v.toFixed(1) + '%';
  }

  function buildFilterUI(container, chartId, defaults) {
    const opt = (value, label, sel) =>
      `<option value="${value}"${sel === value ? ' selected' : ''}>${label}</option>`;
    const layerOptions = ['All', ...LAYERS].map(l => opt(l, l, defaults.layer || 'All')).join('');
    const regionOptions = ['All', ...REGIONS].map(r => opt(r, r, defaults.region || 'All')).join('');
    const metricOptions = METRICS.map(m => opt(m.key, m.label, defaults.metric || 'revenue')).join('');
    const curOptions = CURRENCIES.map(c => opt(c, c, defaults.currency || 'USD')).join('');

    container.innerHTML = `
      <div class="chart-filters">
        <label>Layer
          <select data-f="layer">${layerOptions}</select>
        </label>
        <label>Region
          <select data-f="region">${regionOptions}</select>
        </label>
        <label>Metric
          <select data-f="metric">${metricOptions}</select>
        </label>
        <label>Display currency
          <select data-f="currency">${curOptions}</select>
        </label>
        <label>Sort
          <select data-f="sort">
            <option value="desc">High → Low</option>
            <option value="asc">Low → High</option>
            <option value="alpha">A → Z</option>
            <option value="layer">By layer then size</option>
          </select>
        </label>
        <label>Scale
          <select data-f="scale">
            <option value="log"${defaults.scale === 'log' ? ' selected' : ''}>Log scale</option>
            <option value="linear"${defaults.scale !== 'log' ? ' selected' : ''}>Linear</option>
          </select>
        </label>
        <div class="chart-fx-status">
          <b>FX source:</b> <code data-fx-source>loading…</code>
          &nbsp;·&nbsp; Companies with data for the selected metric: <b data-count>0</b>
        </div>
      </div>
      <div class="chart-surface" style="width:100%;height:680px"></div>
    `;
  }

  function readFilters(filtersRoot) {
    const q = (k) => filtersRoot.querySelector(`[data-f="${k}"]`).value;
    return {
      layer: q('layer'),
      region: q('region'),
      metric: q('metric'),
      currency: q('currency'),
      sort: q('sort'),
      scale: q('scale')
    };
  }

  function projectData(filters) {
    const metric = METRICS.find(m => m.key === filters.metric) || METRICS[0];
    const isPct = metric.type === 'pct';
    let rows = (window.COMPANIES || []).filter(c => {
      if (filters.layer !== 'All' && c.layer !== filters.layer) return false;
      if (filters.region !== 'All' && c.hq !== filters.region) return false;
      const raw = c[metric.key];
      return raw !== null && raw !== undefined && !isNaN(raw);
    }).map(c => {
      const raw = c[metric.key];
      const displayValue = isPct ? raw : convert(raw, c.cur, filters.currency);
      return {
        name: c.name, ticker: c.ticker, layer: c.layer, hq: c.hq,
        fyEnd: c.fyEnd, note: c.note,
        native: raw, nativeCur: c.cur,
        value: displayValue
      };
    }).filter(r => r.value !== null);

    if (filters.sort === 'desc') rows.sort((a, b) => b.value - a.value);
    else if (filters.sort === 'asc') rows.sort((a, b) => a.value - b.value);
    else if (filters.sort === 'alpha') rows.sort((a, b) => a.name.localeCompare(b.name));
    else if (filters.sort === 'layer') rows.sort((a, b) => {
      if (a.layer === b.layer) return b.value - a.value;
      return a.layer.localeCompare(b.layer);
    });
    return { rows, isPct, metric };
  }

  function renderChart(chart, filters) {
    const { rows, isPct, metric } = projectData(filters);
    const count = rows.length;

    if (count === 0) {
      chart.clear();
      chart.setOption({
        title: { text: 'No companies match the current filters', left: 'center', top: 'middle', textStyle: { fontSize: 14, color: '#6a737d' } }
      });
      return count;
    }

    const height = Math.max(400, 32 + count * 28);
    chart.getDom().style.height = height + 'px';
    chart.resize();

    const title = metric.label + (isPct ? ' — percent' : ' — displayed in ' + filters.currency);
    const subtext = count + ' companies · latest disclosed fiscal year per company';

    chart.setOption({
      backgroundColor: 'transparent',
      title: {
        text: title,
        subtext: subtext,
        left: 'center',
        textStyle: { fontSize: 15 },
        subtextStyle: { fontSize: 11, color: '#6a737d' }
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
        formatter: function (params) {
          const p = params[0];
          const d = rows[p.dataIndex];
          const nativeStr = isPct ? fmtPct(d.native) : fmtMoney(d.native, d.nativeCur);
          const convStr   = isPct ? fmtPct(d.value) : fmtMoney(d.value, filters.currency);
          const tickerStr = d.ticker ? ' · ' + d.ticker : '';
          return (
            '<b>' + d.name + '</b> <span style="color:#888">(' + d.hq + tickerStr + ')</span><br/>' +
            '<span style="color:#888">Layer:</span> ' + d.layer + '<br/>' +
            '<span style="color:#888">FY end:</span> ' + d.fyEnd + '<br/>' +
            '<span style="color:#888">' + metric.label + ':</span> <b>' + convStr + '</b>' +
            (isPct || d.nativeCur === filters.currency ? '' : ' <span style="color:#888">(native ' + nativeStr + ')</span>') +
            (d.note ? '<br/><span style="color:#888">' + d.note + '</span>' : '')
          );
        }
      },
      legend: {
        data: LAYERS,
        top: 42,
        textStyle: { fontSize: 11 },
        icon: 'rect'
      },
      grid: { left: 150, right: 80, top: 80, bottom: 50, containLabel: false },
      xAxis: {
        type: (filters.scale === 'log' && !isPct) ? 'log' : 'value',
        name: isPct ? '%' : filters.currency,
        nameLocation: 'middle',
        nameGap: 30,
        axisLabel: {
          formatter: function (v) {
            if (isPct) return v.toFixed(0) + '%';
            return fmtMoney(v, filters.currency);
          }
        },
        splitLine: { lineStyle: { type: 'dashed', color: '#e1e4e8' } }
      },
      yAxis: {
        type: 'category',
        data: rows.map(r => r.name),
        inverse: true,
        axisLabel: { fontSize: 11, color: '#24292e' },
        axisTick: { show: false }
      },
      series: LAYERS.map(function (layerName) {
        return {
          name: layerName,
          type: 'bar',
          stack: 'stack',
          data: rows.map(function (r) {
            return r.layer === layerName
              ? { value: r.value, itemStyle: { color: LAYER_COLORS[layerName] } }
              : { value: '-' };
          }),
          label: {
            show: true,
            position: 'right',
            fontSize: 10,
            color: '#24292e',
            formatter: function (p) {
              if (p.value === '-' || p.value == null) return '';
              const d = rows[p.dataIndex];
              return isPct ? fmtPct(d.value) : fmtMoney(d.value, filters.currency);
            }
          },
          barMaxWidth: 22
        };
      })
    }, true);

    return count;
  }

  async function activateChart(chartKey, container) {
    if (chartInstances[chartKey]) return chartInstances[chartKey];

    const defaults = {
      metric:    container.getAttribute('data-metric')    || 'revenue',
      currency:  container.getAttribute('data-currency')  || 'USD',
      scale:     container.getAttribute('data-scale')     || 'log',
      layer:     container.getAttribute('data-layer')     || 'All',
      region:    container.getAttribute('data-region')    || 'All'
    };

    buildFilterUI(container, chartKey, defaults);
    await loadFXOnce();

    const filtersRoot = container.querySelector('.chart-filters');
    const chartEl = container.querySelector('.chart-surface');
    const chart = echarts.init(chartEl);
    chartInstances[chartKey] = chart;

    filtersRoot.querySelector('[data-fx-source]').textContent = fxState.source || 'unknown';

    function rerender() {
      const count = renderChart(chart, readFilters(filtersRoot));
      filtersRoot.querySelector('[data-count]').textContent = count;
    }
    filtersRoot.querySelectorAll('select').forEach(sel => sel.addEventListener('change', rerender));
    window.addEventListener('resize', () => chart.resize());
    rerender();
    return chart;
  }

  // Wire up all toggles on the page
  function wireToggles() {
    document.querySelectorAll('.view-toggle').forEach(function (toggle) {
      const target = toggle.getAttribute('data-target');
      toggle.querySelectorAll('button').forEach(function (btn) {
        btn.addEventListener('click', function () {
          const view = btn.getAttribute('data-view');
          toggle.querySelectorAll('button').forEach(b => b.classList.toggle('active', b === btn));
          const chartDiv = document.querySelector('.chart-view[data-chart="' + target + '"]');
          const tableEl = document.querySelector('table.chartable[data-chart-ref="' + target + '"]');
          if (!chartDiv) return;
          if (view === 'chart') {
            chartDiv.classList.add('active');
            if (tableEl) tableEl.classList.add('hidden');
            activateChart(target, chartDiv);
          } else {
            chartDiv.classList.remove('active');
            if (tableEl) tableEl.classList.remove('hidden');
          }
        });
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', wireToggles);
  } else {
    wireToggles();
  }

  /* ==============================================================
     TIME-SERIES CHART (multi-year, multi-company line chart)
     ============================================================== */

  const TS_METRICS = [
    { key: 'revenue',     label: 'Revenue',           type: 'money' },
    { key: 'opIncome',    label: 'Operating Income',  type: 'money' },
    { key: 'netIncome',   label: 'Net Income',        type: 'money' },
    { key: 'totalAssets', label: 'Total Assets',      type: 'money' },
    { key: 'totalEquity', label: 'Total Equity',      type: 'money' },
    { key: 'opMargin',    label: 'Operating Margin %', type: 'pct' },
    { key: 'grossMargin', label: 'Gross Margin %',    type: 'pct' },
    { key: 'netMargin',   label: 'Net Margin %',      type: 'pct' }
  ];

  function buildTimeSeriesFilterUI(container, defaults) {
    const companies = Object.keys(window.TIMESERIES || {}).sort();
    const defaultCompanies = defaults.companies || companies.slice(0, 6);
    const companyOptions = companies.map(c => {
      const depth = window.TIMESERIES[c].fiscal.length;
      const sel = defaultCompanies.includes(c) ? ' selected' : '';
      return `<option value="${c}"${sel}>${c} (${depth}y)</option>`;
    }).join('');
    const metricOptions = TS_METRICS.map(m => {
      const sel = (defaults.metric || 'revenue') === m.key ? ' selected' : '';
      return `<option value="${m.key}"${sel}>${m.label}</option>`;
    }).join('');
    const curOptions = CURRENCIES.map(c => {
      const sel = (defaults.currency || 'USD') === c ? ' selected' : '';
      return `<option value="${c}"${sel}>${c}</option>`;
    }).join('');
    container.innerHTML = `
      <div class="chart-filters">
        <label style="grid-column: span 2">Companies (ctrl/cmd + click to multi-select)
          <select data-f="companies" multiple size="7">${companyOptions}</select>
        </label>
        <label>Metric
          <select data-f="metric">${metricOptions}</select>
        </label>
        <label>Display currency
          <select data-f="currency">${curOptions}</select>
        </label>
        <label>Scale
          <select data-f="scale">
            <option value="linear">Linear</option>
            <option value="log"${defaults.scale === 'log' ? ' selected' : ''}>Log</option>
          </select>
        </label>
        <label>Normalize
          <select data-f="normalize">
            <option value="none">Absolute values</option>
            <option value="index">Indexed (first year = 100)</option>
          </select>
        </label>
        <div class="chart-fx-status">
          <b>FX source:</b> <code data-fx-source>loading…</code>
          &nbsp;·&nbsp; Series shown: <b data-count>0</b>
        </div>
      </div>
      <div class="chart-surface" style="width:100%;height:600px"></div>
    `;
  }

  function readTSFilters(root) {
    const sel = root.querySelector('[data-f="companies"]');
    const selected = Array.from(sel.selectedOptions).map(o => o.value);
    return {
      companies: selected,
      metric:     root.querySelector('[data-f="metric"]').value,
      currency:   root.querySelector('[data-f="currency"]').value,
      scale:      root.querySelector('[data-f="scale"]').value,
      normalize:  root.querySelector('[data-f="normalize"]').value
    };
  }

  function renderTimeSeries(chart, filters) {
    const metric = TS_METRICS.find(m => m.key === filters.metric) || TS_METRICS[0];
    const isPct = metric.type === 'pct';
    const palette = ['#e63946','#6a4c93','#2a9d8f','#fb8500','#0b5394','#606c38','#d62828','#457b9d','#8d99ae','#495057','#b5179e','#f77f00'];

    const xAll = new Set();
    const series = [];
    filters.companies.forEach((name, idx) => {
      const c = window.TIMESERIES[name];
      if (!c) return;
      const points = c.fiscal
        .filter(p => p[metric.key] != null && !isNaN(p[metric.key]))
        .map(p => ({ fy: p.fy, raw: p[metric.key], endDate: p.endDate }));
      if (!points.length) return;

      let baseValue = null;
      const data = points.map((p, i) => {
        let v = isPct ? p.raw : convert(p.raw, c.cur, filters.currency);
        if (v == null) return null;
        if (filters.normalize === 'index') {
          if (i === 0) baseValue = v;
          v = baseValue ? (v / baseValue) * 100 : null;
        }
        xAll.add(p.fy);
        return [p.fy, v];
      }).filter(Boolean);

      if (!data.length) return;
      series.push({
        name: name,
        type: 'line',
        data: data,
        smooth: false,
        symbol: 'circle',
        symbolSize: 7,
        lineStyle: { width: 2, color: palette[idx % palette.length] },
        itemStyle: { color: palette[idx % palette.length] },
        emphasis: { focus: 'series' }
      });
    });

    const xYears = Array.from(xAll).sort((a,b) => a - b);
    chart.setOption({
      backgroundColor: 'transparent',
      title: {
        text: metric.label + (filters.normalize === 'index' ? ' — indexed (first year = 100)' : isPct ? ' — percent' : ' — ' + filters.currency),
        subtext: series.length + ' companies · fiscal-year end varies · click legend to toggle',
        left: 'center',
        textStyle: { fontSize: 15 },
        subtextStyle: { fontSize: 11, color: '#6a737d' }
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'line' },
        formatter: function (params) {
          let s = '<b>FY' + params[0].axisValue + '</b><br/>';
          params.sort((a,b) => b.value[1] - a.value[1]);
          params.forEach(p => {
            if (p.value && p.value[1] != null) {
              const v = p.value[1];
              let display;
              if (filters.normalize === 'index') display = v.toFixed(1);
              else if (isPct) display = fmtPct(v);
              else display = fmtMoney(v, filters.currency);
              s += p.marker + ' ' + p.seriesName + ': <b>' + display + '</b><br/>';
            }
          });
          return s;
        }
      },
      legend: {
        data: series.map(s => s.name),
        top: 42,
        textStyle: { fontSize: 11 },
        type: 'scroll'
      },
      grid: { left: 70, right: 40, top: 90, bottom: 50 },
      xAxis: {
        type: 'category',
        data: xYears,
        name: 'Fiscal year',
        nameLocation: 'middle',
        nameGap: 30,
        axisLabel: { fontSize: 11 }
      },
      yAxis: {
        type: (filters.scale === 'log' && !isPct && filters.normalize !== 'index') ? 'log' : 'value',
        name: filters.normalize === 'index' ? 'Indexed' : isPct ? '%' : filters.currency,
        nameLocation: 'middle',
        nameGap: 55,
        axisLabel: {
          formatter: function (v) {
            if (filters.normalize === 'index') return v.toFixed(0);
            if (isPct) return v.toFixed(0) + '%';
            return fmtMoney(v, filters.currency);
          }
        }
      },
      series: series
    }, true);

    return series.length;
  }

  async function activateTimeSeries(chartKey, container) {
    if (chartInstances[chartKey]) return chartInstances[chartKey];
    const defaults = {
      companies: (container.getAttribute('data-companies') || '').split(',').filter(Boolean),
      metric:    container.getAttribute('data-metric')   || 'revenue',
      currency:  container.getAttribute('data-currency') || 'USD',
      scale:     container.getAttribute('data-scale')    || 'linear',
      normalize: container.getAttribute('data-normalize')|| 'none'
    };
    buildTimeSeriesFilterUI(container, defaults);
    await loadFXOnce();

    const filtersRoot = container.querySelector('.chart-filters');
    const chartEl = container.querySelector('.chart-surface');
    const chart = echarts.init(chartEl);
    chartInstances[chartKey] = chart;
    filtersRoot.querySelector('[data-fx-source]').textContent = fxState.source || 'unknown';

    function rerender() {
      const count = renderTimeSeries(chart, readTSFilters(filtersRoot));
      filtersRoot.querySelector('[data-count]').textContent = count;
    }
    filtersRoot.querySelectorAll('select').forEach(sel => sel.addEventListener('change', rerender));
    window.addEventListener('resize', () => chart.resize());
    rerender();
    return chart;
  }

  // Wire time-series toggles (data-type="timeseries" marker)
  function wireTimeSeries() {
    document.querySelectorAll('.chart-view[data-type="timeseries"]').forEach(function (cv) {
      const key = cv.getAttribute('data-chart') || 'ts-default';
      // Activate immediately — no table to compare against
      cv.classList.add('active');
      activateTimeSeries(key, cv);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', wireTimeSeries);
  } else {
    wireTimeSeries();
  }

  window.CompanyChart = {
    activate: activateChart,
    activateTimeSeries: activateTimeSeries,
    reload: () => Object.values(chartInstances).forEach(c => c.resize()),
    fxState: fxState
  };
})();
