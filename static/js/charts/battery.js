var BatteryChart = (function () {
    var chart = null;

    function init(el, theme) {
        chart = echarts.init(el, theme);
        chart.setOption({
            tooltip: { trigger: 'axis' },
            xAxis: { type: 'time' },
            yAxis: {
                type: 'value',
                name: 'V',
                min: function (v) { return Math.floor(v.min * 10) / 10; },
            },
            dataZoom: [
                { type: 'inside', xAxisIndex: 0 },
                { type: 'slider', xAxisIndex: 0, height: 20, bottom: 5 },
            ],
            series: [{
                name: 'Repeater Voltage',
                type: 'line',
                smooth: true,
                symbol: 'none',
                lineStyle: { width: 2 },
                areaStyle: { opacity: 0.15 },
                data: [],
            }],
            grid: { left: 50, right: 16, top: 20, bottom: 50 },
        });
        return chart;
    }

    function update(data) {
        if (!chart) return;
        var series = [];
        for (var i = 0; i < data.timestamps.length; i++) {
            series.push([data.timestamps[i] * 1000, data.ch2_voltage[i]]);
        }
        chart.setOption({ series: [{ data: series }] });
    }

    return { init: init, update: update, resize: function () { if (chart) chart.resize(); } };
})();
