# 🛡️ National Data Trust Ledger

A professional blockchain-powered data integrity and trust verification system built with Flask, designed for government and enterprise data management.

## 🚀 Features

### Multi-Factor Trust Scoring System
- **Source Reliability**: Government (100%) > Academic (90%) > Private (70%) > Unknown (40%)
- **Data Freshness**: Recent data gets trust bonuses (up to 20 points)
- **Transformation History**: Edit penalties reduce trust (up to 30 points)
- **Access Pattern Analysis**: Simulated anomaly detection (up to 15 points penalty)
- **Data Integrity**: Based on edit history and source stability (up to 15 points)

### Blockchain-Inspired Ledger
- Immutable data blocks with cryptographic hashing
- Chain integrity verification
- Block explorer interface
- Previous hash linking for tamper detection

### Professional Government-Grade UI
- Modern responsive design with Bootstrap
- Color-coded risk levels (Green/Yellow/Red)
- Interactive data visualizations with Chart.js
- Government-style header and professional styling

### Advanced Features
- **Verify Integrity**: Real-time hash verification for each dataset
- **Search & Filter**: Find datasets by name or risk level
- **Data Visualization**: Trust score and risk distribution charts
- **Chain Verification**: Full blockchain integrity checking

## 🛠️ Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript
- **Data Storage**: JSON file (no database required)
- **Visualization**: Chart.js
- **Icons**: Font Awesome
- **Security**: SHA256 hashing, blockchain-style integrity

## 📋 Installation & Setup

### Prerequisites
- Python 3.7+
- No additional dependencies required (uses only standard library + Flask)

### Quick Start

1. **Clone/Download** the project files:
   ```
   app.py
   templates/index.html
   ledger.json (auto-created)
   ```

2. **Install Flask**:
   ```bash
   pip install flask
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Open your browser** and navigate to:
   ```
   http://127.0.0.1:5000
   ```

## 🎯 Usage

### Adding Datasets
1. Enter a dataset name (e.g., "Census Data 2024")
2. Select the data source from the dropdown
3. Specify the number of transformation edits
4. Click "Register Dataset"

### Understanding Trust Scores
- **80-100**: LOW RISK (Green) - High confidence data
- **60-79**: MEDIUM RISK (Yellow) - Moderate confidence
- **0-59**: HIGH RISK (Red) - Low confidence data

### Verifying Integrity
- Click "Verify Integrity" on any dataset block
- The system recalculates the hash and compares with stored hash
- Green checkmark = Valid, Red X = Tampered

### Searching & Filtering
- **Search**: Type dataset names in the search box
- **Filter**: Use dropdown to show only specific risk levels
- **Reset**: Clear all filters to show all datasets

## 🔧 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main dashboard |
| `/api/ledger` | GET | Get full ledger data |
| `/api/stats` | GET | Get statistics for dashboard |
| `/add` | POST | Add new dataset |
| `/verify/<id>` | GET | Verify specific block integrity |
| `/verify-chain` | GET | Verify entire chain integrity |
| `/search` | GET | Search datasets by name |
| `/filter` | GET | Filter by risk level |
| `/api/trust-factors/<id>` | GET | Get detailed trust breakdown |

## 🏗️ Architecture

### Trust Scoring Algorithm
```
Final Score = (Source Reliability × 0.4) +
             (Data Freshness × 0.2) +
             (Data Integrity × 0.15) -
             (Transformation Penalty × 0.3) -
             (Access Pattern Penalty × 0.15)
```

### Block Structure
```json
{
  "data": {
    "dataset": "Dataset Name",
    "source": "government",
    "edits": 0,
    "trust_score": 95,
    "risk_level": "LOW",
    "edited": false
  },
  "timestamp": "1640995200.123",
  "prev_hash": "abc123...",
  "hash": "def456...",
  "block_height": 0
}
```

## 🎨 Customization

### Adding New Source Types
Edit `SOURCE_WEIGHTS` in `app.py`:
```python
SOURCE_WEIGHTS = {
    "government": 1.0,
    "academic": 0.9,
    "private": 0.7,
    "new_source": 0.8  # Add your source
}
```

### Modifying Trust Factors
Adjust the weights in `calculate_comprehensive_trust_score()` function.

### Styling Changes
Edit the CSS variables in `templates/index.html`:
```css
:root {
  --primary-color: #1e40af;    /* Change primary color */
  --success-color: #059669;    /* Change success color */
  --danger-color: #dc2626;     /* Change danger color */
}
```

## 🔒 Security Features

- **Cryptographic Hashing**: SHA256 for data integrity
- **Immutable Ledger**: Blockchain-style data structure
- **Tamper Detection**: Hash verification on each block
- **Chain Validation**: Full chain integrity checking
- **Access Pattern Monitoring**: Simulated anomaly detection

## 📊 Sample Data

The system comes with sample datasets. You can add more using the web interface:

- **Government Census Data** (High Trust)
- **Academic Research Data** (Medium-High Trust)
- **Private Company Data** (Medium Trust)
- **Unknown Source Data** (Low Trust)

## 🚀 Production Deployment

For production use, consider:
- Using a proper WSGI server (Gunicorn, uWSGI)
- Adding user authentication
- Implementing rate limiting
- Adding database storage (PostgreSQL, MongoDB)
- SSL/TLS encryption
- Regular backup procedures

## 🤝 Contributing

This is a demonstration project. For production use, consider:
- Adding comprehensive testing
- Implementing proper logging
- Adding user management
- Database integration
- API documentation
- Security audits

## 📄 License

This project is provided as-is for educational and demonstration purposes.

---

**Built for hackathons and data integrity demonstrations. Perfect for showcasing blockchain concepts in government data management scenarios.**