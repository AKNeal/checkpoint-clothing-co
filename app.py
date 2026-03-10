from flask import Flask, render_template_string, jsonify, request, send_from_directory
import json
import os
from datetime import datetime

app = Flask(__name__)

# Load design approvals
APPROVALS_FILE = 'design_approvals.json'

def load_approvals():
    if os.path.exists(APPROVALS_FILE):
        with open(APPROVALS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_approvals(data):
    with open(APPROVALS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# ==================== ROUTES ====================

# Main Store
@app.route('/')
def index():
    with open('checkpoint_index.html', 'r') as f:
        return f.read()

# Admin Dashboard
@app.route('/admin/dashboard')
@app.route('/admin/dashboard/')
def dashboard():
    dashboard_html = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Design Approval Dashboard - Checkpoint</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #0a0e27 0%, #004e89 100%);
                color: #1a1a1a;
                min-height: 100vh;
                padding: 2rem;
            }

            .container {
                max-width: 1400px;
                margin: 0 auto;
            }

            header {
                background: rgba(255, 255, 255, 0.95);
                padding: 2rem;
                border-radius: 12px;
                margin-bottom: 2rem;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
            }

            h1 {
                color: #0a0e27;
                margin-bottom: 0.5rem;
            }

            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 1rem;
                margin-top: 1.5rem;
            }

            .stat-card {
                background: linear-gradient(135deg, #ff6b35 0%, #ff8a50 100%);
                color: white;
                padding: 1.5rem;
                border-radius: 8px;
                text-align: center;
            }

            .stat-card.pending {
                background: linear-gradient(135deg, #ffa500 0%, #ffb84d 100%);
            }

            .stat-card.approved {
                background: linear-gradient(135deg, #00d084 0%, #00e699 100%);
            }

            .stat-card.denied {
                background: linear-gradient(135deg, #ff4444 0%, #ff6666 100%);
            }

            .stat-number {
                font-size: 2.5rem;
                font-weight: bold;
            }

            .stat-label {
                font-size: 0.9rem;
                opacity: 0.9;
                margin-top: 0.5rem;
            }

            .controls {
                display: flex;
                gap: 1rem;
                margin-top: 1.5rem;
                flex-wrap: wrap;
            }

            .btn {
                background: #004e89;
                color: white;
                border: none;
                padding: 0.8rem 1.5rem;
                border-radius: 6px;
                cursor: pointer;
                font-weight: 600;
                transition: all 0.3s;
            }

            .btn:hover {
                background: #003366;
                transform: translateY(-2px);
            }

            .filter-group {
                display: flex;
                gap: 0.5rem;
                flex-wrap: wrap;
            }

            .filter-btn {
                background: white;
                border: 2px solid #004e89;
                color: #004e89;
                padding: 0.6rem 1.2rem;
                border-radius: 20px;
                cursor: pointer;
                font-weight: 600;
                transition: all 0.3s;
            }

            .filter-btn.active {
                background: #004e89;
                color: white;
            }

            .designs-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                gap: 1.5rem;
                margin-top: 2rem;
            }

            .design-card {
                background: white;
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
                transition: all 0.3s;
            }

            .design-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
            }

            .design-header {
                background: linear-gradient(135deg, #004e89 0%, #00d4ff 100%);
                color: white;
                padding: 1rem;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }

            .design-name {
                font-weight: bold;
                font-size: 1.1rem;
            }

            .design-status {
                padding: 0.3rem 0.8rem;
                border-radius: 12px;
                font-size: 0.8rem;
                font-weight: bold;
                background: rgba(255, 255, 255, 0.3);
            }

            .design-status.approved {
                background: #00d084;
                color: white;
            }

            .design-status.denied {
                background: #ff4444;
                color: white;
            }

            .design-status.pending {
                background: #ffa500;
                color: white;
            }

            .design-body {
                padding: 1.5rem;
            }

            .design-category {
                color: #ff6b35;
                font-size: 0.85rem;
                font-weight: bold;
                text-transform: uppercase;
                margin-bottom: 0.5rem;
            }

            .design-description {
                color: #666;
                margin-bottom: 1rem;
                line-height: 1.5;
            }

            .design-colors {
                display: flex;
                gap: 0.5rem;
                margin-bottom: 1rem;
                flex-wrap: wrap;
            }

            .color-swatch {
                width: 30px;
                height: 30px;
                border-radius: 4px;
                border: 1px solid #ddd;
            }

            .design-notes {
                background: #f5f5f5;
                padding: 0.8rem;
                border-radius: 6px;
                margin-bottom: 1rem;
                font-size: 0.9rem;
            }

            .design-notes textarea {
                width: 100%;
                min-height: 60px;
                padding: 0.5rem;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-family: inherit;
                resize: vertical;
            }

            .design-actions {
                display: flex;
                gap: 0.5rem;
            }

            .action-btn {
                flex: 1;
                padding: 0.7rem;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-weight: 600;
                transition: all 0.3s;
            }

            .approve-btn {
                background: #00d084;
                color: white;
            }

            .approve-btn:hover {
                background: #00b86b;
            }

            .deny-btn {
                background: #ff4444;
                color: white;
            }

            .deny-btn:hover {
                background: #dd0000;
            }

            .pending-btn {
                background: #ffa500;
                color: white;
            }

            .pending-btn:hover {
                background: #ff8800;
            }

            .no-designs {
                text-align: center;
                padding: 3rem 2rem;
                background: white;
                border-radius: 12px;
                color: #999;
            }

            .export-btn {
                background: #004e89;
            }

            .export-btn:hover {
                background: #003366;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>🎨 Design Approval Dashboard</h1>
                <p>Review and approve gaming merchandise designs for Checkpoint Clothing Co</p>
                
                <div class="stats">
                    <div class="stat-card pending">
                        <div class="stat-number" id="pending-count">0</div>
                        <div class="stat-label">Pending Review</div>
                    </div>
                    <div class="stat-card approved">
                        <div class="stat-number" id="approved-count">0</div>
                        <div class="stat-label">Approved</div>
                    </div>
                    <div class="stat-card denied">
                        <div class="stat-number" id="denied-count">0</div>
                        <div class="stat-label">Denied</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="total-count">0</div>
                        <div class="stat-label">Total Designs</div>
                    </div>
                </div>

                <div class="controls">
                    <div class="filter-group">
                        <button class="filter-btn active" onclick="filterByStatus('all')">All</button>
                        <button class="filter-btn" onclick="filterByStatus('pending')">Pending</button>
                        <button class="filter-btn" onclick="filterByStatus('approved')">Approved</button>
                        <button class="filter-btn" onclick="filterByStatus('denied')">Denied</button>
                    </div>
                    <button class="btn export-btn" onclick="exportData()">📥 Export JSON</button>
                </div>
            </header>

            <div class="designs-grid" id="designs-grid">
                <div class="no-designs">Loading designs...</div>
            </div>
        </div>

        <script>
            let allDesigns = [];
            let currentFilter = 'all';

            // Load designs from API
            async function loadDesigns() {
                try {
                    const response = await fetch('/api/designs');
                    allDesigns = await response.json();
                    renderDesigns(allDesigns);
                    updateStats();
                } catch (error) {
                    console.error('Error loading designs:', error);
                    document.getElementById('designs-grid').innerHTML = '<div class="no-designs">Error loading designs</div>';
                }
            }

            // Render designs
            function renderDesigns(designs) {
                const grid = document.getElementById('designs-grid');
                
                if (designs.length === 0) {
                    grid.innerHTML = '<div class="no-designs">No designs to display</div>';
                    return;
                }

                grid.innerHTML = designs.map(design => `
                    <div class="design-card">
                        <div class="design-header">
                            <div class="design-name">${design.name}</div>
                            <div class="design-status ${design.status}">${design.status.toUpperCase()}</div>
                        </div>
                        <div class="design-body">
                            <div class="design-category">${design.genre}</div>
                            <div class="design-description">${design.description}</div>
                            <div class="design-colors">
                                ${(design.colors || []).map(color => 
                                    `<div class="color-swatch" style="background: ${color}" title="${color}"></div>`
                                ).join('')}
                            </div>
                            <div class="design-notes">
                                <textarea id="notes-${design.id}" placeholder="Add notes...">${design.notes || ''}</textarea>
                            </div>
                            <div class="design-actions">
                                <button class="action-btn approve-btn" onclick="updateStatus('${design.id}', 'approved')">✓ Approve</button>
                                <button class="action-btn pending-btn" onclick="updateStatus('${design.id}', 'pending')">⊙ Pending</button>
                                <button class="action-btn deny-btn" onclick="updateStatus('${design.id}', 'denied')">✕ Deny</button>
                            </div>
                        </div>
                    </div>
                `).join('');
            }

            // Update design status
            async function updateStatus(designId, status) {
                const notes = document.getElementById(`notes-${designId}`).value;
                
                try {
                    const response = await fetch(`/api/${status}/${designId}`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ notes })
                    });

                    if (response.ok) {
                        loadDesigns();
                    }
                } catch (error) {
                    console.error('Error updating design:', error);
                }
            }

            // Filter by status
            function filterByStatus(status) {
                currentFilter = status;
                
                // Update active button
                document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
                event.target.classList.add('active');

                // Filter and render
                const filtered = status === 'all' 
                    ? allDesigns 
                    : allDesigns.filter(d => d.status === status);
                
                renderDesigns(filtered);
            }

            // Update statistics
            function updateStats() {
                const pending = allDesigns.filter(d => d.status === 'pending').length;
                const approved = allDesigns.filter(d => d.status === 'approved').length;
                const denied = allDesigns.filter(d => d.status === 'denied').length;

                document.getElementById('pending-count').textContent = pending;
                document.getElementById('approved-count').textContent = approved;
                document.getElementById('denied-count').textContent = denied;
                document.getElementById('total-count').textContent = allDesigns.length;
            }

            // Export data
            function exportData() {
                const dataStr = JSON.stringify(allDesigns, null, 2);
                const dataBlob = new Blob([dataStr], { type: 'application/json' });
                const url = URL.createObjectURL(dataBlob);
                const link = document.createElement('a');
                link.href = url;
                link.download = `checkpoint-designs-${new Date().toISOString().split('T')[0]}.json`;
                link.click();
            }

            // Load on startup
            loadDesigns();
        </script>
    </body>
    </html>
    '''
    return dashboard_html

# ==================== API ROUTES ====================

@app.route('/api/designs', methods=['GET'])
def get_designs():
    """Get all designs with their approval status"""
    approvals = load_approvals()
    
    # Sample designs from our gaming merch collection
    designs = [
        {"id": "1", "name": "Git Gud or Die Trying", "genre": "FPS", "description": "Elden Ring meme culture", "colors": ["#ff6b35", "#004e89", "#00d4ff"], "status": approvals.get("1", {}).get("status", "pending")},
        {"id": "2", "name": "Synthwave Gamer", "genre": "Retro", "description": "80s arcade aesthetic", "colors": ["#ff00ff", "#00ffff", "#ffff00"], "status": approvals.get("2", {}).get("status", "pending")},
        {"id": "3", "name": "Loot Goblin", "genre": "RPG", "description": "D&D/BG3 community humor", "colors": ["#8b4513", "#00aa00", "#ffaa00"], "status": approvals.get("3", {}).get("status", "pending")},
        {"id": "4", "name": "Cozy Gamer Club", "genre": "Indie", "description": "Wholesome gaming vibes", "colors": ["#d2691e", "#f4a460", "#ffe4b5"], "status": approvals.get("4", {}).get("status", "pending")},
        {"id": "5", "name": "Cyberpunk Hacker", "genre": "FPS", "description": "Sci-fi neon aesthetic", "colors": ["#00ff00", "#ff00ff", "#000000"], "status": approvals.get("5", {}).get("status", "pending")},
        {"id": "6", "name": "Speedrunner Elite", "genre": "Retro", "description": "For those who play fast", "colors": ["#ff0000", "#ffff00", "#000000"], "status": approvals.get("6", {}).get("status", "pending")},
        {"id": "7", "name": "Esports Champion", "genre": "Esports", "description": "Competitive gaming gear", "colors": ["#ffd700", "#000000", "#ffffff"], "status": approvals.get("7", {}).get("status", "pending")},
        {"id": "8", "name": "Indie Developer", "genre": "Indie", "description": "Made by gamers, for gamers", "colors": ["#0066cc", "#ff6600", "#ffffff"], "status": approvals.get("8", {}).get("status", "pending")},
    ]
    
    # Add notes if they exist
    for design in designs:
        design["notes"] = approvals.get(design["id"], {}).get("notes", "")
    
    return jsonify(designs)

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get approval statistics"""
    approvals = load_approvals()
    
    pending = sum(1 for v in approvals.values() if v.get("status") == "pending")
    approved = sum(1 for v in approvals.values() if v.get("status") == "approved")
    denied = sum(1 for v in approvals.values() if v.get("status") == "denied")
    
    return jsonify({
        "pending": pending,
        "approved": approved,
        "denied": denied,
        "total": pending + approved + denied
    })

@app.route('/api/approve/<design_id>', methods=['POST'])
def approve_design(design_id):
    """Approve a design"""
    data = request.get_json() or {}
    approvals = load_approvals()
    approvals[design_id] = {
        "status": "approved",
        "notes": data.get("notes", ""),
        "timestamp": datetime.now().isoformat()
    }
    save_approvals(approvals)
    return jsonify({"status": "success"})

@app.route('/api/deny/<design_id>', methods=['POST'])
def deny_design(design_id):
    """Deny a design"""
    data = request.get_json() or {}
    approvals = load_approvals()
    approvals[design_id] = {
        "status": "denied",
        "notes": data.get("notes", ""),
        "timestamp": datetime.now().isoformat()
    }
    save_approvals(approvals)
    return jsonify({"status": "success"})

@app.route('/api/pending/<design_id>', methods=['POST'])
def pending_design(design_id):
    """Mark a design as pending"""
    data = request.get_json() or {}
    approvals = load_approvals()
    approvals[design_id] = {
        "status": "pending",
        "notes": data.get("notes", ""),
        "timestamp": datetime.now().isoformat()
    }
    save_approvals(approvals)
    return jsonify({"status": "success"})

# ==================== ERROR HANDLING ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
