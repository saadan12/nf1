const label_list = JSON.parse(document.getElementById('label_list').textContent);
const color_list = JSON.parse(document.getElementById('color_list').textContent);
const item_percentages = JSON.parse(document.getElementById('item_percentages').textContent);

const date_dict = JSON.parse(document.getElementById('date_dict').textContent);
const balances_dict = JSON.parse(document.getElementById('balances_dict').textContent);

eval('var labels='+label_list);
eval('var colors='+color_list);
eval('var percentages='+item_percentages);

eval('var graph_dates='+date_dict);
eval('var graph_bal='+balances_dict);

console.log(graph_bal);

(function ($) {
    var options = {
        series: percentages,
        chart: {
            height: 220,
            type: 'donut',
        },
        dataLabels: {
            enabled: true,
            style: {
                  fontSize: '10.5px',
                  fontWeight: 'bold',
                  colors: ['#fff',],
             },
        },
//        ['Bitcoin', 'Tether', 'Tezos', 'Monero']
        labels: labels,
        fill: {
//            colors: ['#2CA07A', '#F7931A', '#386cac', '#323232', '#2CA07A', '#386cac', '#A6DF00', '#FF6600']
            colors: colors
        },
        responsive: [{
            breakpoint: 480,
            options: {
                chart: {
                    width: 200
                },
                legend: {
                    show: false
                }
            }
        }],
        legend: {
            show: false,
            position: 'right',
            offsetY: 0,
            height: 150,
        },
        plotOptions: {
        pie: {
          customScale: 1.05,
          donut: {
            size: '55%'
          }
        }
      }
    };

    var chart = new ApexCharts(document.querySelector("#balance-chart"), options);
    chart.render();

})(jQuery);


(function ($) {
    $('#report-select').on('change', function () {
        drawChart();
    });

    function getSeries() {
        var symbol = $('#report-select').val();
        console.log(graph_bal[symbol])
        return series(symbol);
    }
    //graph_bal = {"BTC": [9.17, 9.18, 9.18, 9.17, 9.17], "USDT": [11.95, 11.95, 11.95, 12.95]}

    function series(symbol) {
        var asd = [{
              name: symbol,
              data: graph_bal[symbol]
//            data: [110, 41, 120, 51, 49, 160, 69, 91, 148]
        }]
        return asd
    }

    function get_dates() {
        var symbol = $('#report-select').val();
        dates = graph_dates[symbol];
        return dates
    }

    var options = {
        series: getSeries(),
        chart: {
            height: 300,
            type: "area",
            animations: {
                enabled: false
            },
            toolbar: {
                show: false
            },
            zoom: {
            enabled: true
          }
        },
        colors: ["#2F2CD8"],
        labels: ['azzz', 'bzzzz'],
        dataLabels: {
            enabled: false
        },
        grid: {
            show: true,
            borderColor: '#F1F1F1',
        },
        xaxis: {
            // categories: graph_dates,
               categories: get_dates(),
            // categories: ['Jan 01', 'Jan 02', 'Jan 03', 'Jan 04', 'Jan 05', 'Jan 06', 'Jan 07', 'Jan 08', 'Jan 09'],
            axisBorder: {
                show: false
            },
        },
        yaxis: {
          opposite: true,
        },
    };
    var chart = new ApexCharts(document.querySelector("#chartx"), options);

    chart.render();

    function drawChart() {
        chart.updateSeries(getSeries())
    }

})(jQuery);