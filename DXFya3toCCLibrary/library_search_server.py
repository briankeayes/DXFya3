#!/usr/bin/env python3
"""
Simple Flask server for searching Creative Cloud Libraries via web interface.
"""

from flask import Flask, render_template_string, jsonify, request
import sqlite3
import json
from pathlib import Path
from datetime import datetime

app = Flask(__name__)

DB_PATH = Path(__file__).parent / "cc_libraries_enhanced.db"
USER_MAP_PATH = Path(__file__).parent / "user_map.json"

def load_user_map():
    """Load user ID to name mapping."""
    if not USER_MAP_PATH.exists():
        return {}
    try:
        with open(USER_MAP_PATH) as f:
            data = json.load(f)
            return data.get('users', {})
    except:
        return {}

def get_user_name(user_id):
    """Get human-readable name for a user ID."""
    if not user_id:
        return "Unknown"
    
    user_map = load_user_map()
    
    if user_id in user_map:
        return user_map[user_id].get('name', user_id)
    
    short_id = user_id.split('@')[0]
    return f"{short_id}..."

def timestamp_to_date(ts):
    """Convert millisecond timestamp to readable date."""
    if not ts:
        return "N/A"
    try:
        return datetime.fromtimestamp(ts / 1000).strftime('%Y-%m-%d %H:%M')
    except:
        return "N/A"

@app.route('/')
def index():
    """Serve the main search interface."""
    html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Creative Cloud Library Search</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        
        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .search-box {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            margin-bottom: 30px;
        }
        
        .search-input-group {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
        }
        
        .search-input {
            flex: 1;
            padding: 15px 20px;
            font-size: 16px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            transition: border-color 0.3s;
        }
        
        .search-input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .search-button {
            padding: 15px 40px;
            font-size: 16px;
            font-weight: 600;
            color: white;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 10px;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .search-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .filters {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        .filter-button {
            padding: 8px 16px;
            font-size: 14px;
            border: 2px solid #e0e0e0;
            background: white;
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .filter-button.active {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }
        
        .stats {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            display: none;
        }
        
        .stats.visible {
            display: block;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }
        
        .stat-item {
            text-align: center;
        }
        
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }
        
        .stat-label {
            color: #666;
            margin-top: 5px;
        }
        
        .results {
            display: none;
        }
        
        .results.visible {
            display: block;
        }
        
        .result-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            margin-bottom: 15px;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .result-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 30px rgba(0,0,0,0.15);
        }
        
        .result-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 15px;
        }
        
        .result-title {
            font-size: 1.3em;
            font-weight: 600;
            color: #333;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .file-icon {
            font-size: 1.5em;
        }
        
        .library-badge {
            display: inline-block;
            padding: 5px 12px;
            background: #f0f0f0;
            border-radius: 15px;
            font-size: 0.85em;
            color: #666;
        }
        
        .library-badge.shared {
            background: #e3f2fd;
            color: #1976d2;
        }
        
        .result-meta {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #e0e0e0;
        }
        
        .meta-item {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }
        
        .meta-label {
            font-size: 0.85em;
            color: #999;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .meta-value {
            font-size: 0.95em;
            color: #333;
            font-weight: 500;
        }
        
        .action-buttons {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }
        
        .action-button {
            padding: 8px 16px;
            font-size: 0.9em;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: background 0.3s;
        }
        
        .action-button.primary {
            background: #667eea;
            color: white;
        }
        
        .action-button.primary:hover {
            background: #5568d3;
        }
        
        .action-button.secondary {
            background: #f0f0f0;
            color: #333;
        }
        
        .action-button.secondary:hover {
            background: #e0e0e0;
        }
        
        .version-badge {
            display: inline-block;
            padding: 5px 12px;
            background: #ffd54f;
            color: #f57f17;
            border-radius: 15px;
            font-size: 0.85em;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.3s;
        }
        
        .version-badge:hover {
            background: #ffc107;
        }
        
        .version-list {
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #e0e0e0;
            display: none;
        }
        
        .version-list.expanded {
            display: block;
        }
        
        .version-item {
            padding: 10px;
            margin: 5px 0;
            background: #f9f9f9;
            border-radius: 5px;
            font-size: 0.9em;
        }
        
        .version-item.current {
            background: #e8f5e9;
            border-left: 3px solid #4caf50;
        }
        
        .version-label {
            display: inline-block;
            padding: 2px 8px;
            background: #4caf50;
            color: white;
            border-radius: 10px;
            font-size: 0.8em;
            margin-left: 10px;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: white;
            font-size: 1.2em;
            display: none;
        }
        
        .loading.visible {
            display: block;
        }
        
        .no-results {
            background: white;
            padding: 40px;
            border-radius: 10px;
            text-align: center;
            color: #666;
            display: none;
        }
        
        .no-results.visible {
            display: block;
        }
        
        .error {
            background: #ffebee;
            color: #c62828;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            display: none;
        }
        
        .error.visible {
            display: block;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎨 Creative Cloud Library Search</h1>
            <p>Search across all your libraries instantly</p>
        </div>
        
        <div class="search-box">
            <div class="search-input-group">
                <input type="text" id="searchInput" class="search-input" 
                       placeholder="Search for files, elements, or libraries..." 
                       autofocus>
                <button class="search-button" onclick="performSearch()">Search</button>
            </div>
            
            <div class="filters">
                <button class="filter-button active" data-filter="all" onclick="setFilter('all')">All Types</button>
                <button class="filter-button" data-filter="illustrator" onclick="setFilter('illustrator')">Illustrator</button>
                <button class="filter-button" data-filter="color" onclick="setFilter('color')">Colors</button>
                <button class="filter-button" data-filter="shared" onclick="setFilter('shared')">Shared Only</button>
                <button class="filter-button" data-filter="private" onclick="setFilter('private')">Private Only</button>
            </div>
        </div>
        
        <div id="stats" class="stats"></div>
        <div id="error" class="error"></div>
        <div id="loading" class="loading">Searching...</div>
        <div id="noResults" class="no-results">
            <h3>No results found</h3>
            <p>Try a different search term or filter</p>
        </div>
        <div id="results" class="results"></div>
    </div>
    
    <script>
        let currentFilter = 'all';
        
        // Search on Enter key
        document.getElementById('searchInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                performSearch();
            }
        });
        
        // Load stats on page load
        window.addEventListener('load', loadStats);
        
        function setFilter(filter) {
            currentFilter = filter;
            document.querySelectorAll('.filter-button').forEach(btn => {
                btn.classList.remove('active');
            });
            document.querySelector(`[data-filter="${filter}"]`).classList.add('active');
            
            // Re-run search if there are results
            if (document.getElementById('results').classList.contains('visible')) {
                performSearch();
            }
        }
        
        function loadStats() {
            fetch('/api/stats')
                .then(response => response.json())
                .then(data => {
                    const statsHtml = `
                        <div class="stats-grid">
                            <div class="stat-item">
                                <div class="stat-number">${data.total_elements}</div>
                                <div class="stat-label">Total Elements</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-number">${data.total_libraries}</div>
                                <div class="stat-label">Libraries</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-number">${data.total_files}</div>
                                <div class="stat-label">Files</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-number">${data.unique_users}</div>
                                <div class="stat-label">Collaborators</div>
                            </div>
                        </div>
                    `;
                    document.getElementById('stats').innerHTML = statsHtml;
                    document.getElementById('stats').classList.add('visible');
                });
        }
        
        function performSearch() {
            const query = document.getElementById('searchInput').value.trim();
            
            if (!query) {
                return;
            }
            
            // Show loading
            document.getElementById('loading').classList.add('visible');
            document.getElementById('results').classList.remove('visible');
            document.getElementById('noResults').classList.remove('visible');
            document.getElementById('error').classList.remove('visible');
            
            // Perform search
            fetch(`/api/search?q=${encodeURIComponent(query)}&filter=${currentFilter}`)
                .then(response => response.json())
                .then(data => {
                    document.getElementById('loading').classList.remove('visible');
                    
                    if (data.error) {
                        document.getElementById('error').textContent = data.error;
                        document.getElementById('error').classList.add('visible');
                        return;
                    }
                    
                    if (data.results.length === 0) {
                        document.getElementById('noResults').classList.add('visible');
                        return;
                    }
                    
                    displayResults(data.results);
                })
                .catch(error => {
                    document.getElementById('loading').classList.remove('visible');
                    document.getElementById('error').textContent = 'Search failed: ' + error.message;
                    document.getElementById('error').classList.add('visible');
                });
        }
        
        function displayResults(results) {
            const resultsContainer = document.getElementById('results');
            
            let html = '';
            results.forEach((item, index) => {
                const fileIcon = getFileIcon(item.file_type);
                const libraryClass = item.library_type === 'shared' ? 'shared' : '';
                const versionBadge = item.version_count > 1 ? 
                    `<span class="version-badge" onclick="toggleVersions(${index})">📚 ${item.version_count} versions</span>` : '';
                
                html += `
                    <div class="result-card">
                        <div class="result-header">
                            <div class="result-title">
                                <span class="file-icon">${fileIcon}</span>
                                ${item.element_name}
                                ${versionBadge}
                            </div>
                            <span class="library-badge ${libraryClass}">${item.library_name}</span>
                        </div>
                        
                        <div class="result-meta">
                            <div class="meta-item">
                                <span class="meta-label">File Type</span>
                                <span class="meta-value">${item.file_name || 'N/A'}</span>
                            </div>
                            <div class="meta-item">
                                <span class="meta-label">Size</span>
                                <span class="meta-value">${formatFileSize(item.file_size)}</span>
                            </div>
                            <div class="meta-item">
                                <span class="meta-label">Modified</span>
                                <span class="meta-value">${item.modified_at}</span>
                            </div>
                            <div class="meta-item">
                                <span class="meta-label">Modified By</span>
                                <span class="meta-value">${item.modified_by}</span>
                            </div>
                        </div>
                        
                        <div class="action-buttons">
                            <button class="action-button primary" onclick="viewDetails('${item.element_id}')">View Details</button>
                            ${item.component_path ? `<button class="action-button secondary" onclick="copyPath('${escapeHtml(item.component_path)}')">Copy Path</button>` : ''}
                        </div>
                        
                        ${item.version_count > 1 ? createVersionList(item.versions, index) : ''}
                    </div>
                `;
            });
            
            resultsContainer.innerHTML = html;
            resultsContainer.classList.add('visible');
        }
        
        function createVersionList(versions, cardIndex) {
            let html = `<div class="version-list" id="versions-${cardIndex}">`;
            html += `<strong>Version History:</strong>`;
            
            versions.forEach((version, idx) => {
                const isCurrent = idx === 0;
                const versionLabel = isCurrent ? '<span class="version-label">CURRENT</span>' : '';
                
                html += `
                    <div class="version-item ${isCurrent ? 'current' : ''}">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <strong>${version.element_name}</strong> ${versionLabel}
                                <br>
                                <small>Modified: ${version.modified_at_formatted} by ${version.modified_by}</small>
                            </div>
                            <div>
                                <button class="action-button primary" style="padding: 5px 10px; font-size: 0.85em;" 
                                        onclick="viewDetails('${version.element_id}')">Details</button>
                            </div>
                        </div>
                    </div>
                `;
            });
            
            html += '</div>';
            return html;
        }
        
        function toggleVersions(index) {
            const versionList = document.getElementById(`versions-${index}`);
            if (versionList) {
                versionList.classList.toggle('expanded');
            }
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        function getFileIcon(fileType) {
            if (!fileType) return '📄';
            if (fileType.includes('illustrator')) return '🎨';
            if (fileType.includes('image')) return '🖼️';
            if (fileType.includes('color')) return '🎨';
            return '📄';
        }
        
        function formatFileSize(bytes) {
            if (!bytes) return 'N/A';
            if (bytes < 1024) return bytes + ' B';
            if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
            return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
        }
        
        function viewDetails(elementId) {
            window.open(`/api/details/${elementId}`, '_blank');
        }
        
        function copyPath(path) {
            navigator.clipboard.writeText(path).then(() => {
                alert('Path copied to clipboard!');
            });
        }
    </script>
</body>
</html>
    '''
    return render_template_string(html)

@app.route('/api/stats')
def get_stats():
    """Get database statistics."""
    if not DB_PATH.exists():
        return jsonify({'error': 'Database not found'}), 404
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Total elements
    cursor.execute('SELECT COUNT(*) FROM elements')
    total_elements = cursor.fetchone()[0]
    
    # Total libraries
    cursor.execute('SELECT COUNT(*) FROM libraries')
    total_libraries = cursor.fetchone()[0]
    
    # Total files (with component_path)
    cursor.execute('SELECT COUNT(*) FROM elements WHERE component_path IS NOT NULL')
    total_files = cursor.fetchone()[0]
    
    # Unique users
    cursor.execute('SELECT COUNT(DISTINCT created_by_user) FROM elements WHERE created_by_user IS NOT NULL')
    unique_users = cursor.fetchone()[0]
    
    conn.close()
    
    return jsonify({
        'total_elements': total_elements,
        'total_libraries': total_libraries,
        'total_files': total_files,
        'unique_users': unique_users
    })

@app.route('/api/search')
def search():
    """Search the database with version grouping."""
    query = request.args.get('q', '')
    filter_type = request.args.get('filter', 'all')
    
    if not query:
        return jsonify({'error': 'No search query provided'}), 400
    
    if not DB_PATH.exists():
        return jsonify({'error': 'Database not found'}), 404
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Build query based on filter
    sql = '''
        SELECT e.element_id, e.element_name, e.file_name, e.file_type, e.file_size,
               e.modified_at, e.modified_by_user, e.component_path, e.created_at,
               l.library_name, l.library_type
        FROM elements e
        JOIN libraries l ON e.library_id = l.library_id
        WHERE (e.element_name LIKE ? OR e.file_name LIKE ? OR l.library_name LIKE ?)
    '''
    
    params = [f'%{query}%', f'%{query}%', f'%{query}%']
    
    # Apply filters
    if filter_type == 'illustrator':
        sql += ' AND e.file_type LIKE "%illustrator%"'
    elif filter_type == 'color':
        sql += ' AND e.element_type LIKE "%color%"'
    elif filter_type == 'shared':
        sql += ' AND l.library_type = "shared"'
    elif filter_type == 'private':
        sql += ' AND l.library_type = "private"'
    
    sql += ' ORDER BY e.modified_at DESC'
    
    cursor.execute(sql, params)
    results = cursor.fetchall()
    
    conn.close()
    
    # Group results by element_name
    grouped = {}
    for row in results:
        element_name = row[1]
        
        version_data = {
            'element_id': row[0],
            'element_name': row[1],
            'file_name': row[2],
            'file_type': row[3],
            'file_size': row[4],
            'modified_at': row[5],
            'modified_at_formatted': timestamp_to_date(row[5]),
            'modified_by': get_user_name(row[6]),
            'component_path': row[7],
            'created_at': row[8],
            'library_name': row[9],
            'library_type': row[10]
        }
        
        if element_name not in grouped:
            grouped[element_name] = {
                'versions': [],
                'latest': None
            }
        
        grouped[element_name]['versions'].append(version_data)
    
    # Format results - take the most recent version as the main item
    formatted_results = []
    for element_name, data in grouped.items():
        # Sort versions by modified_at descending
        data['versions'].sort(key=lambda x: x['modified_at'], reverse=True)
        latest = data['versions'][0]
        
        formatted_results.append({
            'element_id': latest['element_id'],
            'element_name': latest['element_name'],
            'file_name': latest['file_name'],
            'file_type': latest['file_type'],
            'file_size': latest['file_size'],
            'modified_at': latest['modified_at_formatted'],
            'modified_by': latest['modified_by'],
            'component_path': latest['component_path'],
            'library_name': latest['library_name'],
            'library_type': latest['library_type'],
            'version_count': len(data['versions']),
            'versions': data['versions']  # Include all versions for expansion
        })
    
    # Sort by most recent modification
    formatted_results.sort(key=lambda x: x['versions'][0]['modified_at'], reverse=True)
    
    # Limit to top 50 groups
    formatted_results = formatted_results[:50]
    
    return jsonify({'results': formatted_results, 'count': len(formatted_results)})

@app.route('/api/details/<element_id>')
def get_details(element_id):
    """Get detailed information about an element."""
    if not DB_PATH.exists():
        return "Database not found", 404
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT e.*, l.library_name, l.library_type
        FROM elements e
        JOIN libraries l ON e.library_id = l.library_id
        WHERE e.element_id = ?
    ''', (element_id,))
    
    result = cursor.fetchone()
    
    if not result:
        conn.close()
        return "Element not found", 404
    
    columns = [desc[0] for desc in cursor.description]
    elem = dict(zip(columns, result))
    
    # Get version history
    cursor.execute('''
        SELECT * FROM version_history
        WHERE element_id = ?
        ORDER BY version_number DESC
    ''', (element_id,))
    
    versions = cursor.fetchall()
    version_cols = [desc[0] for desc in cursor.description]
    
    conn.close()
    
    # Build HTML response
    html = f'''
<!DOCTYPE html>
<html>
<head>
    <title>{elem['element_name']} - Details</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 900px; margin: 40px auto; padding: 20px; }}
        h1 {{ color: #333; }}
        .meta {{ background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .meta-item {{ margin: 10px 0; }}
        .label {{ font-weight: bold; color: #666; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #667eea; color: white; }}
    </style>
</head>
<body>
    <h1>📄 {elem['element_name']}</h1>
    
    <div class="meta">
        <div class="meta-item"><span class="label">Library:</span> {elem['library_name']} ({elem['library_type']})</div>
        <div class="meta-item"><span class="label">File:</span> {elem['file_name'] or 'N/A'}</div>
        <div class="meta-item"><span class="label">Size:</span> {elem['file_size']:,} bytes</div>
        <div class="meta-item"><span class="label">Created:</span> {timestamp_to_date(elem['created_at'])}</div>
        <div class="meta-item"><span class="label">Created By:</span> {get_user_name(elem['created_by_user'])}</div>
        <div class="meta-item"><span class="label">Modified:</span> {timestamp_to_date(elem['modified_at'])}</div>
        <div class="meta-item"><span class="label">Modified By:</span> {get_user_name(elem['modified_by_user'])}</div>
        {f'<div class="meta-item"><span class="label">Local Path:</span> {elem["component_path"]}</div>' if elem['component_path'] else ''}
    </div>
    
    <h2>Version History ({len(versions)} versions)</h2>
    <table>
        <tr>
            <th>Version</th>
            <th>Modified</th>
            <th>Modified By</th>
            <th>Asset Version</th>
        </tr>
    '''
    
    for version in versions[:20]:
        ver_dict = dict(zip(version_cols, version))
        html += f'''
        <tr>
            <td>{ver_dict['version_number']}</td>
            <td>{timestamp_to_date(ver_dict['modified_at'])}</td>
            <td>{get_user_name(ver_dict['modified_by'])}</td>
            <td>{ver_dict['asset_version'] or 'N/A'}</td>
        </tr>
        '''
    
    html += '''
    </table>
</body>
</html>
    '''
    
    return html

if __name__ == '__main__':
    print("=" * 60)
    print("🎨 Creative Cloud Library Search Server")
    print("=" * 60)
    print()
    print("Starting server...")
    print("Open your browser to: http://localhost:5001")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    app.run(debug=True, port=5001)

