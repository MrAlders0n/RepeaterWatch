var PacketsChart = (function () {
    var chart = null;

    function init(el, theme) {
        chart = echarts.init(el, theme);
        chart.setOption({
            tooltip: { trigger: 'axis' },
            legend: {
                data: ['TX', 'RX'],
                textStyle: { fontSize: 11 },
                top: 0,
            },
            xAxis: { type: 'time' },
            yAxis: { type: 'value', name: 'Count' },
            dataZoom: [
                { type: 'inside', xAxisIndex: 0 },
                { type: 'slider', xAxisIndex: 0, height: 20, bottom: 5 },
            ],
            series: [
                {
                    name: 'TX',
                    type: 'bar',
                    stack: 'packets',
                    itemStyle: { color: '#00b4d8' },
                    data: [],
                },
                {
                    name: 'RX',
                    type: 'bar',
                    stack: 'packets',
                    itemStyle: { color: '#06d6a0' },
                    data: [],
                },
            ],
            grid: { left: 50, right: 16, top: 30, bottom: 50 },
        });
        return chart;
    }

    function update(data) {
        if (!chart) return;
        var tx = [], rx = [];
        for (var i = 0; i < data.timestamps.length; i++) {
            var t = data.timestamps[i] * 1000;
            tx.push([t, data.tx_count[i]]);
            rx.push([t, data.rx_count[i]]);
        }
        chart.setOption({
            series: [{ data: tx }, { data: rx }],
        });
    }

    return { init: init, update: update, resize: function () { if (chart) chart.resize(); } };
})();

var AirtimeChart = (function () {
    var chart = null;

    function init(el, theme) {
        chart = echarts.init(el, theme);
        chart.setOption({
            tooltip: { trigger: 'axis', valueFormatter: function (v) { return v + '%'; } },
            legend: {
                data: ['TX %', 'RX %'],
                textStyle: { fontSize: 11 },
                top: 0,
            },
            xAxis: { type: 'time' },
            yAxis: { type: 'value', name: '%', max: 100 },
            dataZoom: [
                { type: 'inside', xAxisIndex: 0 },
                { type: 'slider', xAxisIndex: 0, height: 20, bottom: 5 },
            ],
            series: [
                {
                    name: 'TX %',
                    type: 'line',
                    smooth: true,
                    symbol: 'none',
                    areaStyle: { opacity: 0.3 },
                    lineStyle: { width: 2, color: '#00b4d8' },
                    itemStyle: { color: '#00b4d8' },
                    data: [],
                },
                {
                    name: 'RX %',
                    type: 'line',
                    smooth: true,
                    symbol: 'none',
                    areaStyle: { opacity: 0.3 },
                    lineStyle: { width: 2, color: '#06d6a0' },
                    itemStyle: { color: '#06d6a0' },
                    data: [],
                },
            ],
            grid: { left: 50, right: 16, top: 30, bottom: 50 },
        });
        return chart;
    }

    function update(data) {
        if (!chart) return;
        var tx = [], rx = [];
        for (var i = 0; i < data.timestamps.length; i++) {
            var t = data.timestamps[i] * 1000;
            tx.push([t, data.tx_pct[i]]);
            rx.push([t, data.rx_pct[i]]);
        }
        chart.setOption({
            series: [{ data: tx }, { data: rx }],
        });
    }

    return { init: init, update: update, resize: function () { if (chart) chart.resize(); } };
})();
