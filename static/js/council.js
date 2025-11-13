/**
 * Quantum Quant - council.js
 * Handles logic for the Quant Council page.
 */

document.addEventListener('DOMContentLoaded', () => {
    const runButton = document.getElementById('runCouncilBtn');
    
    if (runButton) {
        runButton.addEventListener('click', handleCouncilRun);
    }
});

async function handleCouncilRun() {
    const ticker = document.getElementById('councilTicker').value.toUpperCase();
    if (!ticker) {
        alert("Please enter a ticker.");
        return;
    }

    // Get UI elements
    const resultsArea = document.getElementById('councilResultsArea');
    const loadingSpinner = document.getElementById('councilLoadingSpinner');
    const errorMessage = document.getElementById('councilErrorMessage');
    const resultContent = document.getElementById('councilResultContent');
    
    // Reset UI
    resultsArea.style.display = 'block';
    loadingSpinner.style.display = 'flex';
    errorMessage.style.display = 'none';
    resultContent.style.display = 'none';

    // --- API Call ---
    try {
        const response = await fetch(`/api/run_council/${ticker}`);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'An unknown error occurred.');
        }

        // --- Populate Results ---
        populateCouncilResults(data);
        
        // --- Display Content ---
        loadingSpinner.style.display = 'none';
        resultContent.style.display = 'block';

    } catch (error) {
        // --- Display Error ---
        console.error('Error running council:', error);
        loadingSpinner.style.display = 'none';
        errorMessage.textContent = `Error: ${error.message}`;
        errorMessage.style.display = 'block';
    }
}

function populateCouncilResults(data) {
    // 1. Council Vote
    const voteBox = document.getElementById('councilVoteBox');
    const vote = data.council_vote.toLowerCase();
    voteBox.textContent = data.council_vote;
    voteBox.className = 'recommendation-box'; // Reset
    voteBox.classList.add(vote); // 'buy', 'sell', or 'hold'

    // 2. Breakdown Lists
    const buyList = document.getElementById('buyList');
    const sellList = document.getElementById('sellList');
    const holdList = document.getElementById('holdList');
    
    // Clear old lists
    buyList.innerHTML = '';
    sellList.innerHTML = '';
    holdList.innerHTML = '';
    
    data.votes.Buy.forEach(algo => {
        buyList.innerHTML += `<li>${formatAlgoName(algo)}</li>`;
    });
    data.votes.Sell.forEach(algo => {
        sellList.innerHTML += `<li>${formatAlgoName(algo)}</li>`;
    });
    data.votes.Hold.forEach(algo => {
        holdList.innerHTML += `<li>${formatAlgoName(algo)}</li>`;
    });

    // 3. Breakdown Counts
    document.getElementById('buyCount').textContent = data.votes.Buy.length;
    document.getElementById('sellCount').textContent = data.votes.Sell.length;
    document.getElementById('holdCount').textContent = data.votes.Hold.length;

    // 4. AI Prompt
    document.getElementById('aiPromptTextarea').value = data.ai_prompt;
}

function formatAlgoName(algoKey) {
    // Converts 'ml_predictive' to 'ML Predictive'
    return algoKey.split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}
