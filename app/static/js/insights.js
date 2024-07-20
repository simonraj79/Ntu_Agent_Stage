//app\static\js\insights.js
document.addEventListener('DOMContentLoaded', function() {
    const insightsBtn = document.getElementById('generate-insights-btn');
    if (insightsBtn) {
        const insightsUrl = insightsBtn.getAttribute('data-insights-url');
        insightsBtn.addEventListener('click', () => generateInsights(insightsUrl));
    }
});

async function generateInsights(insightsUrl) {
    const insightsContent = document.getElementById('insights-content');
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    
    insightsContent.innerHTML = '<p>Generating insights...</p>';
    
    try {
        const response = await fetch(insightsUrl, { 
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        console.log('Response data:', data);  // Log the response data

        if (data.success) {
            const insights = data.insights;
            insightsContent.innerHTML = `
                <p><strong>Topics:</strong> <span id="insights-topics">${insights.topics.length > 0 ? insights.topics.join(', ') : 'No topics identified'}</span></p>
                <p><strong>Sentiment:</strong> <span id="insights-sentiment">${insights.sentiment !== null ? insights.sentiment : 'N/A'}</span></p>
                <p><strong>Summary:</strong> <span id="insights-summary">${insights.summary || 'No summary available'}</span></p>
            `;
        } else {
            insightsContent.innerHTML = `<p>Error generating insights: ${data.error || 'Unknown error'}</p>`;
        }
    } catch (error) {
        console.error('Error:', error);
        insightsContent.innerHTML = `<p>Error: ${error.message}</p>`;
    }
}
