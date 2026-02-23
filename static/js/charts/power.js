var PowerCharts = (function () {
    var voltageChart = null;
    var currentChart = null;
    var powerChart = null;

    var CH_COLORS = ['#00b4d8', '#06d6a0', '#ffd166'];
    var CH_NAMES = ['CH0', 'CH1', 'CH2'];

    function makeOption(yName) {
        return {
            tooltip: { trigger: 'axis' },
            legend: {
                data: CH_NAMES,
                textStyle: { fontSize: 11 },
                top: 0,
            },
            xAxis: { type: 'time' },
            yAxis: { type: 'value', name: yName },
            dataZoom: [
                { type: 'inside', xAxisIndex: 0 },
                { type: 'slider', xAxisIndex: 0, height: 20, bottom: 5 },
            ],
            series: CH_NAMES.map(function (name, i) {
                return {
                    name: name,
                    type: 'line',
                    smooth: true,
                    symbol: 'none',
                    lineStyle: { width: 2, color: CH_COLORS[i] },
                    itemStyle: { color: CH_COLORS[i] },
                    data: [],
                };
            }),
            grid: { left: 50, right: 16, top: 30, bottom: 50 },
        };
    }

    function init(voltageEl, currentEl, powerEl, theme) {
        voltageChart = echarts.init(voltageEl, theme);
        currentChart = echarts.init(currentEl, theme);
        powerChart = echarts.init(powerEl, theme);
        voltageChart.setOption(makeOption('V'));
        currentChart.setOption(makeOption('mA'));
        powerChart.setOption(makeOption('mW'));
    }

    function update(data) {
        if (!voltageChart) return;

        var hasData = data.timestamps.length > 0;
        var hasExtpower = hasData && data.ch0_voltage.some(function (v) { return v !== null; });

        // Toggle visibility of INA3221 cards
        ['card-voltage', 'card-current', 'card-power'].forEach(function (id) {
            var el = document.getElementById(id);
            if (el) {
                el.classList.toggle('hidden', !hasExtpower);
            }
        });

        if (!hasExtpower) return;

        var voltageSeries = [[], [], []];
        var currentSeries = [[], [], []];
        var powerSeries = [[], [], []];

        for (var i = 0; i < data.timestamps.length; i++) {
            var t = data.timestamps[i] * 1000;
            voltageSeries[0].push([t, data.ch0_voltage[i]]);
            voltageSeries[1].push([t, data.ch1_voltage[i]]);
            voltageSeries[2].push([t, data.ch2_voltage[i]]);
            currentSeries[0].push([t, data.ch0_current[i]]);
            currentSeries[1].push([t, data.ch1_current[i]]);
            currentSeries[2].push([t, data.ch2_current[i]]);
            powerSeries[0].push([t, data.ch0_power[i]]);
            powerSeries[1].push([t, data.ch1_power[i]]);
            powerSeries[2].push([t, data.ch2_power[i]]);
        }

        voltageChart.setOption({
            series: voltageSeries.map(function (d) { return { data: d }; }),
        });
        currentChart.setOption({
            series: currentSeries.map(function (d) { return { data: d }; }),
        });
        powerChart.setOption({
            series: powerSeries.map(function (d) { return { data: d }; }),
        });
    }

    function resize() {
        if (voltageChart) voltageChart.resize();
        if (currentChart) currentChart.resize();
        if (powerChart) powerChart.resize();
    }

    return { init: init, update: update, resize: resize };
})();
