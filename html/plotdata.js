function update(){
    d3.csv('data.csv').then(makeCharts)
    d3.csv('demographics.csv').then(makeDemographics)
    d3.json('timestamp.json').then(updateTimestamp)
}

tooltip_config = {
    mode: 'x',
    bodyFontSize: 16
}

animations_config = {
    duration: 0
}

function updateTimestamp(data){
    var isoDateTime = new Date(data)
    document.getElementById('last-update').innerHTML = isoDateTime.toLocaleDateString('nl-NL') + " " + isoDateTime.toLocaleTimeString('nl-NL')
}

function makeDemographics(data) {
    var xlabels = data.map(function (d) {
        return d.age_group
    })

    var demographics = data.map(function(d) {
        return d.all_patients == 0 ? null : d.all_patients
    })

    var demographics_deaths = data.map(function(d) {
        return d.died == 0 ? null : d.died
    })

    var icu_demographics_chart = new Chart(document.getElementById("icu-demographics"), {
        type: 'bar',
        data: {
            labels: xlabels,
            datasets: [
                {
                    label: "Demographics of patients in ICU",
                    data: demographics,
                    fill: false,
                    backgroundColor: "rgba(75, 192, 192)",
                    borderColor: "rgb(75, 192, 192)",
                    lineTension: 0.1,
                    pointRadius: 5,
                    pointHoverRadius: 10
                },

            ]
        },
        options: {
            scales: {
                xAxes: [{
                    stacked: true
                }],
                yAxes: [{
                    scaleLabel: {
                        display: true,
                        labelString: 'percentage of patients',
                        stacked: true
                    }
                }]
            },
            tooltips: tooltip_config,
            animation: animations_config
        }
    })

    var icu_death_demographics_chart = new Chart(document.getElementById("icu-demographics-death"), {
        type: 'bar',
        data: {
            labels: xlabels,
            datasets: [
                {
                    label: "Demographics of deaths in ICU",
                    data: demographics_deaths,
                    fill: false,
                    backgroundColor: "rgba(192, 75, 75)",
                    borderColor: "rgb(192, 75, 75)",
                    lineTension: 0.1,
                    pointRadius: 5,
                    pointHoverRadius: 10
                },
            ]
        },
        options: {
            scales: {
                xAxes: [{
                    stacked: true
                }],
                yAxes: [{
                    scaleLabel: {
                        display: true,
                        labelString: 'percentage of patients',
                        stacked: true
                    }
                }]
            },
            tooltips: tooltip_config,
            animation: animations_config
        }
    })
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

    var mortality_rate = data.map(function(d) {
        return d.mortality_rate != '' ? Math.round(d.mortality_rate * 100) : null
    })

    var recovered = data.map(function(d) {
        return d.survivors != '' ? d.survivors : null
    })

    var deaths = data.map(function(d) {
        return d.died != '' ? d.died : null
    })

    var growth_trend = Math.round(data[data.length - 1].sma5_growth_intakeCount * 10000) / 100
    document.getElementById('growth-trend').innerHTML = growth_trend

    var els = document.getElementsByClassName('red-green-swap')

    if (growth_trend < 0) {
        var newcolor = 'green'
    } else {
        var newcolor = 'red'
    }

    Array.prototype.forEach.call(els, function(el) {
        if (newcolor == 'red') {
            el.className = el.className.replace(/\btext-green\b/g, 'text-red')
            el.className = el.className.replace(/\bbg-green\b/g, 'bg-red')
            el.className = el.className.replace(/\bborder-green\b/g, 'border-red')
        } else {
            el.className = el.className.replace(/\btext-red\b/g, 'text-green')
            el.className = el.className.replace(/\bbg-red\b/g, 'bg-green')
            el.className = el.className.replace(/\bborder-red\b/g, 'border-green')
        }
    })

    var doubling_rate = Math.round(1 / Math.log(1 + growth_trend / 100, 2))

    if (doubling_rate < 0) {
        document.getElementById('doubling-rate').innerText = 'half life'
    } else {
        document.getElementById('doubling-rate').innerText = 'doubling rate'
    }
    document.getElementById('doubling-rate-val').innerHTML = doubling_rate

    var icu_num_patients_chart = new Chart(document.getElementById("icu-num-patients"), {
        type: 'line',
        data: {
            labels: xlabels,
            datasets: [
                {
                    label: "Confirmed COVID patients in ICU",
                    data: patients_in_icu,
                    fill: false,
                    backgroundColor: ["rgba(75, 192, 192)"],
                    borderColor: "rgb(75, 192, 192)",
                    lineTension: 0.1,
                    pointRadius: 5,
                    pointHoverRadius: 10
                }
            ]
        },
        options: {
            scales: {
                yAxes: [{
                    scaleLabel: {
                        display: true,
                        labelString: 'number of patients'
                    }
                }]
            },
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
                    label: "Growth of confirmed patients in ICU",
                    data: growth,
                    fill: false,
                    backgroundColor: "rgba(75, 192, 192, .3)",
                    borderColor: "rgb(75, 192, 192, .3)",
                    lineTension: 0.1,
                    pointRadius: 5,
                    pointHoverRadius: 10
                },
                {
                    label: "Simple Moving Average (5 days)",
                    data: growth_sma5,
                    fill: false,
                    backgroundColor: "rgba(192, 75, 192)",
                    borderColor: "rgb(192, 75, 192)",
                    lineTension: 0.1,
                    pointRadius: 5,
                    pointHoverRadius: 10
                }
            ]
        },
        options: {
            scales: {
                yAxes: [{
                    scaleLabel: {
                        display: true,
                        labelString: 'percentage change'
                    }
                }]
            },
            animation: animations_config,
            tooltips: tooltip_config
        }
    })

    var icu_mortality_chart = new Chart(document.getElementById("icu-mortality-rate"), {
        type: 'line',
        data: {
            labels: xlabels,
            datasets: [
                {
                    label: "Evolution of mortality rate in ICU",
                    data: mortality_rate,
                    fill: false,
                    backgroundColor: "rgba(192, 75, 75)",
                    borderColor: "rgb(192, 75, 75)",
                    lineTension: 0.1,
                    pointRadius: 5,
                    pointHoverRadius: 10
                },
            ]
        },
        options: {
            scales: {
                yAxes: [{
                    scaleLabel: {
                        display: true,
                        labelString: 'percentage of patients'
                    }
                }]
            },
            animation: animations_config,
            tooltips: tooltip_config
        }
    })

    var icu_recover_vs_death_chart = new Chart(document.getElementById("icu-recovery-vs-death"), {
        type: 'line',
        data: {
            labels: xlabels,
            datasets: [
                {
                    label: "Patients recovered from ICU",
                    data: recovered,
                    fill: false,
                    backgroundColor: "rgba(75, 192, 75)",
                    borderColor: "rgb(75, 192, 75)",
                    lineTension: 0.1,
                    pointRadius: 5,
                    pointHoverRadius: 10
                },
                {
                    label: "Patients died in ICU",
                    data: deaths,
                    fill: false,
                    backgroundColor: "rgba(192, 75, 75)",
                    borderColor: "rgb(192, 75, 75)",
                    lineTension: 0.1,
                    pointRadius: 5,
                    pointHoverRadius: 10
                },
            ]
        },
        options: {
            scales: {
                yAxes: [{
                    scaleLabel: {
                        display: true,
                        labelString: 'number of patients'
                    }
                }]
            },
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