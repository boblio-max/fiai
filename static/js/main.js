/**
 * Quantum Quant - main.js
 * Handles logic for the dynamic algorithm pages.
 */

document.addEventListener('DOMContentLoaded', () => {
    const runButton = document.getElementById('runAlgorithmBtn');
    
    if (runButton) {
        runButton.addEventListener('click', handleAlgorithmRun);
    }
});

async function handleAlgorithmRun() {
    const runButton = document.getElementById('runAlgorithmBtn');
    const strategyName = runButton.dataset.strategy;
    
    // Get Tickers
    const ticker1 = document.getElementById('ticker1').value.toUpperCase();
    let ticker2 = null;
    const ticker2Input = document.getElementById('ticker2');
    if (ticker2Input) {
        ticker2 = ticker2Input.value.toUpperCase();
    }

    // Get UI elements
    const resultsArea = document.getElementById('resultsArea');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const errorMessage = document.getElementById('errorMessage');
    const resultContent = document.getElementById('resultContent');
    
    // Reset UI
    resultsArea.style.display = 'block';
    loadingSpinner.style.display = 'flex';
    errorMessage.style.display = 'none';
    resultContent.style.display = 'none';
    
    // Clear previous results
    document.getElementById('recommendationBox').textContent = '';
    document.getElementById('resultSummary').textContent = '';
    
    // --- API Call ---
    try {
        const payload = { ticker1 };
        if (ticker2) {
            payload.ticker2 = ticker2;
        }

        const response = await fetch(`/api/run_algorithm/${strategyName}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'An unknown error occurred.');
        }

        // --- Populate Results ---
        populateAlgorithmResults(data);
        
        // --- Display Content ---
        loadingSpinner.style.display = 'none';
        resultContent.style.display = 'block';

    } catch (error) {
        // --- Display Error ---
        console.error('Error running algorithm:', error);
        loadingSpinner.style.display = 'none';
        errorMessage.textContent = `Error: ${error.message}`;
        errorMessage.style.display = 'block';
    }
}

function populateAlgorithmResults(data) {
    // 1. Recommendation Box
    const recBox = document.getElementById('recommendationBox');
    const rec = data.recommendation.toLowerCase();
    recBox.textContent = data.recommendation;
    recBox.className = 'recommendation-box'; // Reset classes
    recBox.classList.add(rec); // Add 'buy', 'sell', or 'hold'

    // 2. Summary
    document.getElementById('resultSummary').textContent = data.summary;

    // 3. Chart
    const chartContainer = document.getElementById('algorithmChartContainer');
    const noChartMessage = document.getElementById('noChartMessage');
    const chartCanvas = document.getElementById('algorithmChart');
    
    if (data.chart_data) {
        chartContainer.style.display = 'block';
        noChartMessage.style.display = 'none';
        
        // Use the global 'renderAlgorithmChart' from chart.js
        // We pass the canvas *element* itself
        window.renderAlgorithmChart(chartCanvas, data);

    } else {
        // Handle placeholders with no chart
        chartContainer.style.display = 'none';
        noChartMessage.style.display = 'block';
    }
}
