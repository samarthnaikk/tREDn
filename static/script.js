let currentData = null;
let currentFilename = null;

document.addEventListener('DOMContentLoaded', function() {
    loadFiles();
    
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
        loadFiles();
        
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

async function loadFiles() {
    try {
        const response = await fetch('/files');
        const files = await response.json();
        
        let filesHtml = '';
        files.forEach(file => {
            filesHtml += `
                <div class="file-item">
                    <div class="file-info">
                        <div class="file-name">${file.file_name}</div>
                        <div class="file-meta">Modified: ${file.last_modified} | Size: ${file.file_size_kb} KB</div>
                    </div>
                    <div class="file-actions">
                        <button onclick="loadFile('${file.file_name}')" class="btn">Load</button>
                        <button onclick="downloadFile('${file.file_name}')" class="btn btn-success">CSV</button>
                    </div>
                </div>
            `;
        });
        
        document.getElementById('filesList').innerHTML = filesHtml || '<p>No saved files found.</p>';
    } catch (error) {
        console.error('Error loading files:', error);
        document.getElementById('filesList').innerHTML = '<p class="error">Error loading files.</p>';
    }
}

async function loadFile(filename) {
    try {
        const response = await fetch('/load/' + filename);
        const data = await response.json();
        
        if (data.error) {
            alert('Error: ' + data.error);
            return;
        }
        
        currentData = data;
        currentFilename = filename;
        displayResults(data);
        document.getElementById('results').style.display = 'block';
        document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
    } catch (error) {
        alert('Error loading file: ' + error.message);
    }
}

async function downloadFile(filename) {
    try {
        const response = await fetch('/export/' + filename);
        if (!response.ok) {
            throw new Error('Export failed');
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename.replace('.json', '.csv');
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    } catch (error) {
        alert('Error downloading file: ' + error.message);
    }
}