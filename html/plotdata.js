function update(){
    d3.csv('data.csv').then(makeCharts)
    d3.json('timestamp.json').then(updateTimestamp)
}


function updateTimestamp(data){
    var isoDateTime = new Date(data)
    document.getElementById('last-update').innerHTML = isoDateTime.toLocaleDateString('nl-NL') + " " + isoDateTime.toLocaleTimeString('nl-NL')
}

function makeCharts(data) {
    var headerNames = d3.keys(data[0])
    var xlabels = data.map(function (d) {
        return d.date
    })

    var patients_in_icu = data.map(function (d) {
        return d.intakeCount
    })

    var growth = data.map(function (d) {
        return Math.round(d.growth_intakeCount * 10000) / 100
    })

    var growth_sma5 = data.map(function (d) {
        return Math.round(d.sma5_growth_intakeCount * 10000) / 100
    })

    tooltip_config = {
        mode: 'x',
        bodyFontSize: 16
    }

    animations_config = {
        duration: 0
    }

    var icu_num_patients_chart = new Chart(document.getElementById("icu-num-patients"), {
        type: 'line',
        data: {
            labels: xlabels,
            datasets: [
                {
                    "label": "Confirmed COVID patients in ICU",
                    "data": patients_in_icu,
                    "fill": false,
                    "backgroundColor": ["rgba(75, 192, 192)"],
                    "borderColor": "rgb(75, 192, 192)",
                    "lineTension": 0.1,
                    "pointRadius": 5,
                    "pointHoverRadius": 10
                }
            ]
        },
        options: {
            tooltips: tooltip_config,
            animation: animations_config
        }
    })

    var icu_growth_chart = new Chart(document.getElementById("icu-growth"), {
        type: 'line',
        data: {
            labels: xlabels,
            datasets: [
                {
                    "label": "Growth of confirmed patients in ICU",
                    "data": growth,
                    "fill": false,
                    "backgroundColor": ["rgba(75, 192, 192)"],
                    "borderColor": "rgb(75, 192, 192)",
                    "lineTension": 0.1,
                    "pointRadius": 5,
                    "pointHoverRadius": 10
                },
                {
                    "label": "Simple Moving Average (5 days)",
                    "data": growth_sma5,
                    "fill": false,
                    "backgroundColor": ["rgba(192, 75, 192)"],
                    "borderColor": "rgb(192, 75, 192)",
                    "lineTension": 0.1,
                    "pointRadius": 5,
                    "pointHoverRadius": 10
                }
            ]
        },
        options: {
            animation: animations_config,
            tooltips: tooltip_config
        }
    })

}

document.addEventListener("DOMContentLoaded", function(e) {
    update()
    setInterval(function () {
        update()
    }, 1800 * 1000) // update every 30 min
})