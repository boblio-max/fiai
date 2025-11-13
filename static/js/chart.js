/**
 * Quantum Quant - chart.js
 * Handles all Chart.js rendering for the application.
 */

// --- Global Chart.js Defaults ---
Chart.defaults.color = '#e0e0e0';
Chart.defaults.borderColor = 'rgba(255, 215, 0, 0.1)';
Chart.defaults.font.family = "'Exo 2', sans-serif";
Chart.defaults.plugins.legend.labels.boxWidth = 12;
Chart.defaults.plugins.tooltip.backgroundColor = '#0a0a0a';
Chart.defaults.plugins.tooltip.titleColor = '#FFD700';
Chart.defaults.plugins.tooltip.borderColor = '#FFD700';
Chart.defaults.plugins.tooltip.borderWidth = 1;
Chart.defaults.plugins.tooltip.padding = 10;
Chart.defaults.plugins.tooltip.cornerRadius = 8;
Chart.defaults.plugins.tooltip.displayColors = false;


// --- 1. Homepage Chart ---

/**
 * Initializes the homepage chart when the page loads.
 */
function initHomeChart() {
    const canvas = document.getElementById('homeStockChart');
    if (!canvas) {
        // Not on the home page, do nothing
        return;
    }

    // Data is embedded in home.html via Jinja
    const chartData = window.homeChartData;
    const peaksData = window.homePeaksData;

    if (!chartData) {
        console.error("Homepage chart data not found.");
        return;
    }

    const ctx = canvas.getContext('2d');
    
    // Create a gold gradient
    const gradient = ctx.createLinearGradient(0, 0, 0, 450);
    gradient.addColorStop(0, 'rgba(255, 215, 0, 0.6)');
    gradient.addColorStop(0.5, 'rgba(255, 215, 0, 0.1)');
    gradient.addColorStop(1, 'rgba(255, 215, 0, 0)');

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: chartData.labels,
            datasets: [{
                label: 'Close Price',
                data: chartData.prices,
                borderColor: '#FFD700',
                borderWidth: 2,
                pointRadius: 0,
                pointHitRadius: 10, // Makes line easier to click
                tension: 0.3, // Smooth curve
                fill: {
                    target: 'origin',
                    above: gradient,
                },
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'month',
                        tooltipFormat: 'MMM dd, yyyy',
                    },
                    ticks: {
                        color: '#888',
                    },
                    grid: {
                        display: false,
                    }
                },
                y: {
                    ticks: {
                        color: '#888',
                        callback: (value) => `$${value.toFixed(2)}`
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)',
                        drawBorder: false,
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                }
            },
            // --- Click-a-Peak Logic ---
            onClick: (event, elements, chart) => {
                if (elements.length > 0) {
                    const clickedIndex = elements[0].index;
                    
                    // Check if this index matches one of our peaks
                    const matchedPeak = peaksData.find(peak => peak.index === clickedIndex);
                    
                    if (matchedPeak) {
                        // Found a peak! Redirect.
                        console.log('Peak clicked:', matchedPeak);
                        window.location.href = `/algorithm/${matchedPeak.strategy}`;
                    }
                }
            },
            onHover: (event, elements, chart) => {
                // Change cursor to pointer if hovering over a peak
                const canvas = chart.canvas;
                if (elements.length > 0) {
                    const hoverIndex = elements[0].index;
                    const isPeak = peaksData.some(peak => peak.index === hoverIndex);
                    canvas.style.cursor = isPeak ? 'pointer' : 'default';
                } else {
                    canvas.style.cursor = 'default';
                }
            }
        }
    });
}

// Run the home chart init on load
document.addEventListener('DOMContentLoaded', initHomeChart);


// --- 2. Algorithm Page Charts ---

// Store active chart instance to destroy it before re-rendering
let currentAlgorithmChart = null;

/**
 * Renders a chart on the algorithm page.
 * This function is exposed globally so main.js can call it.
 * @param {HTMLCanvasElement} canvas - The canvas element to draw on.
 * @param {object} apiData - The full API response object.
 */
window.renderAlgorithmChart = function(canvas, apiData) {
    if (!canvas) {
        console.error("Algorithm chart canvas not found.");
        return;
    }
    
    // Destroy previous chart instance if it exists
    if (currentAlgorithmChart) {
        currentAlgorithmChart.destroy();
    }
    
    const chartType = apiData.chart_type || 'line'; // Default to line
    const chartData = apiData.chart_data;
    
    let chartConfig;
    
    // --- Chart Config Switch ---
    // Dynamically build the chart config based on strategy
    
    switch (apiData.recommendation) {
        // This is a naive switch based on the *recommendation*.
        // A better way is to use the strategy_name, but this is simpler.
        // Let's refine: check for known data keys.
        
        case (chartData.sma_short ? apiData.recommendation : null): // Momentum
            chartConfig = getMomentumChartConfig(chartData);
            break;
            
        case (chartData.upper_band ? apiData.recommendation : null): // Mean Reversion
            chartConfig = getBollingerChartConfig(chartData);
            break;
            
        case (chartData.z_score ? apiData.recommendation : null): // Stat Arb
            chartConfig = getStatArbChartConfig(chartData);
            break;
            
        case (chartData.volatility ? apiData.recommendation : null): // Volatility
            chartConfig = getVolatilityChartConfig(chartData);
            break;
            
        case (chartData.importance ? apiData.recommendation : null): // ML
            chartConfig = getMLChartConfig(chartData);
            break;

        default: // Default price chart if unknown
            chartConfig = getDefaultPriceChartConfig(chartData);
            break;
    }

    currentAlgorithmChart = new Chart(canvas, chartConfig);
}

// --- Chart Config Helper Functions ---

function getMomentumChartConfig(data) {
    // Helper to map buy/sell signal dates to chart data points
    const buySignals = data.labels.map(label => data.buy_signals.includes(label) ? data.price[data.labels.indexOf(label)] : null);
    const sellSignals = data.labels.map(label => data.sell_signals.includes(label) ? data.price[data.labels.indexOf(label)] : null);
    
    return {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [
                {
                    label: 'Price',
                    data: data.price,
                    borderColor: '#e0e0e0',
                    borderWidth: 2,
                    pointRadius: 0,
                    yAxisID: 'y'
                },
                {
                    label: '50-Day SMA',
                    data: data.sma_short,
                    borderColor: '#FFD700',
                    borderWidth: 1.5,
                    pointRadius: 0,
                    yAxisID: 'y'
                },
                {
                    label: '200-Day SMA',
                    data: data.sma_long,
                    borderColor: '#636e72',
                    borderWidth: 1.5,
                    borderDash: [5, 5],
                    pointRadius: 0,
                    yAxisID: 'y'
                },
                {
                    type: 'scatter',
                    label: 'Buy Signal',
                    data: buySignals,
                    backgroundColor: '#00b894',
                    radius: 6,
                    yAxisID: 'y'
                },
                {
                    type: 'scatter',
                    label: 'Sell Signal',
                    data: sellSignals,
                    backgroundColor: '#d63031',
                    pointStyle: 'triangle',
                    rotation: 180,
                    radius: 6,
                    yAxisID: 'y'
                }
            ]
        },
        options: commonLineChartOptions('y')
    };
}

function getBollingerChartConfig(data) {
    return {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [
                {
                    label: 'Price',
                    data: data.price,
                    borderColor: '#e0e0e0',
                    borderWidth: 2,
                    pointRadius: 0,
                },
                {
                    label: '20-Day SMA',
                    data: data.sma,
                    borderColor: '#FFD700',
                    borderWidth: 1.5,
                    pointRadius: 0,
                },
                {
                    label: 'Upper Band',
                    data: data.upper_band,
                    borderColor: 'rgba(212, 175, 55, 0.5)',
                    borderWidth: 1,
                    pointRadius: 0,
                    borderDash: [5, 5],
                    fill: false,
                },
                {
                    label: 'Lower Band',
                    data: data.lower_band,
                    borderColor: 'rgba(212, 175, 55, 0.5)',
                    borderWidth: 1,
                    pointRadius: 0,
                    borderDash: [5, 5],
                    fill: '+1' // Fill area between lower and upper band
                }
            ]
        },
        options: commonLineChartOptions()
    };
}

function getStatArbChartConfig(data) {
    return {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [
                {
                    label: 'Z-Score',
                    data: data.z_score,
                    borderColor: '#e0e0e0',
                    borderWidth: 2,
                    pointRadius: 0,
                },
                {
                    label: 'Upper Threshold (+2.0)',
                    data: data.upper_band,
                    borderColor: '#d63031',
                    borderWidth: 2,
                    pointRadius: 0,
                    borderDash: [5, 5],
                },
                {
                    label: 'Lower Threshold (-2.0)',
                    data: data.lower_band,
                    borderColor: '#00b894',
                    borderWidth: 2,
                    pointRadius: 0,
                    borderDash: [5, 5],
                }
            ]
        },
        options: commonLineChartOptions()
    };
}

function getVolatilityChartConfig(data) {
    return {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [
                {
                    label: 'Annualized Volatility',
                    data: data.volatility,
                    borderColor: '#FFD700',
                    borderWidth: 2,
                    pointRadius: 0,
                    fill: true,
                    backgroundColor: 'rgba(255, 215, 0, 0.1)'
                }
            ]
        },
        options: commonLineChartOptions('y', (val) => `${(val * 100).toFixed(1)}%`) // Format as percentage
    };
}

function getMLChartConfig(data) {
    return {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Feature Importance',
                data: data.importance,
                backgroundColor: [
                    'rgba(255, 215, 0, 0.8)',
                    'rgba(255, 215, 0, 0.6)',
                    'rgba(255, 215, 0, 0.4)',
                ],
                borderColor: '#FFD700',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y', // Horizontal bar chart
            scales: {
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' }
                },
                y: {
                    grid: { display: false }
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    };
}

function getDefaultPriceChartConfig(data) {
    // Fallback for simple price
    return {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Price',
                data: data.price,
                borderColor: '#FFD700',
                borderWidth: 2,
                pointRadius: 0
            }]
        },
        options: commonLineChartOptions()
    };
}

// Common options for time-series line charts
function commonLineChartOptions(yAxisID = 'y', yTicksCallback = null) {
    const yTickOptions = {
        color: '#888',
    };
    if (yTicksCallback) {
        yTickOptions.callback = yTicksCallback;
    }

    return {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            x: {
                type: 'time',
                time: {
                    unit: 'month',
                    tooltipFormat: 'MMM dd, yyyy',
                },
                ticks: { color: '#888' },
                grid: { display: false }
            },
            [yAxisID]: {
                ticks: yTickOptions,
                grid: {
                    color: 'rgba(255, 255, 255, 0.05)',
                    drawBorder: false,
                }
            }
        },
        plugins: {
            legend: {
                position: 'bottom',
                labels: {
                    usePointStyle: true,
                }
            },
            tooltip: {
                mode: 'index',
                intersect: false,
            }
        },
        interaction: {
            mode: 'index',
            intersect: false
        }
    };
}
