let currentData = null;
let currentFilename = null;

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('searchForm').addEventListener('submit', handleSearch);
    document.getElementById('downloadCsv').addEventListener('click', downloadCsv);
});

async function handleSearch(e) {
    e.preventDefault();
    
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '<div class="loading">Searching Reddit...</div>';
    resultsDiv.style.display = 'block';
    
    const formData = new FormData(e.target);
    
    try {
        const response = await fetch('/search', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.error) {
            resultsDiv.innerHTML = '<div class="error">Error: ' + data.error + '</div>';
            return;
        }
        
        currentData = data;
        currentFilename = data.saved_filename;
        displayResults(data);
        
    } catch (error) {
        resultsDiv.innerHTML = '<div class="error">Error: ' + error.message + '</div>';
    }
}

function displayResults(data) {
    const summary = data.statistics;
    const posts = data.posts;
    
    let summaryHtml = `
        <h3>Search Summary for "${data.search_query}"</h3>
        <p><strong>Posts Found:</strong> ${summary.total_posts} | 
        <strong>Total Upvotes:</strong> ${summary.total_upvotes.toLocaleString()} | 
        <strong>Average Score:</strong> ${summary.average_score}</p>
    `;
    
    let postsHtml = '';
    posts.forEach((post, index) => {
        postsHtml += `
            <div class="post">
                <div class="post-title">${escapeHtml(post.title)}</div>
                <div class="post-meta">
                    <strong>u/${post.author}</strong> in <strong>r/${post.subreddit}</strong> | 
                    ${post.upvotes.toLocaleString()} upvotes | 
                    ${post.comment_count} comments | 
                    ${post.post_date}
                </div>
                <div class="post-links">
                    <a href="${post.external_url}" target="_blank">Original Link</a>
                    <a href="${post.reddit_permalink}" target="_blank">Reddit Discussion</a>
                </div>
                ${post.text_content ? `<div class="post-content">${escapeHtml(post.text_content.substring(0, 200))}${post.text_content.length > 200 ? '...' : ''}</div>` : ''}
                ${post.top_comments.length > 0 ? `
                    <div class="comments">
                        <h4>Top Comments:</h4>
                        ${post.top_comments.slice(0, 3).map(comment => `
                            <div class="comment">
                                <div class="comment-author">u/${comment.comment_author} (${comment.comment_score} points)</div>
                                <div class="comment-text">${escapeHtml(comment.comment_text.substring(0, 300))}${comment.comment_text.length > 300 ? '...' : ''}</div>
                            </div>
                        `).join('')}
                    </div>
                ` : ''}
            </div>
        `;
    });
    
    document.getElementById('results').innerHTML = `
        <div id="summary" class="summary">${summaryHtml}</div>
        <div id="posts">${postsHtml}</div>
        <div class="export-section">
            <button id="downloadCsv" class="btn btn-success" onclick="downloadCsv()">Download CSV</button>
        </div>
    `;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

async function downloadCsv() {
    if (!currentFilename) {
        alert('No data to download');
        return;
    }
    
    try {
        const response = await fetch('/export/' + currentFilename);
        if (!response.ok) {
            throw new Error('Export failed');
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = currentFilename.replace('.json', '.csv');
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    } catch (error) {
        alert('Error downloading CSV: ' + error.message);
    }
}

