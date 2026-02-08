# Stock Trader Information

A comprehensive stock information web application with a ChatGPT-like interface for fetching real-time stock data and company information.

## 📁 Project Structure

```
stock-trader-information/
├── app.py                          # Main Flask application
├── Stock Trader Information.py     # Stock analysis script
├── requirements.txt                # Python dependencies
├── runtime.txt                     # Python runtime version
├── Procfile                        # Process file for deployment
├── start_web.sh                    # Startup script
├── setup_github.sh                 # GitHub setup helper
├── static/                         # Static files (CSS, JS)
│   ├── style.css
│   └── script.js
├── templates/                      # HTML templates
│   └── index.html
├── Company Finance Prompt/         # Additional resources
├── DEPLOYMENT_GUIDE.md             # Deployment instructions
├── QUICK_DEPLOY.md                 # Quick deployment guide
├── QUICK_START.md                  # Quick start guide
├── STOCK_USAGE.md                  # Stock usage documentation
└── WEB_APP_README.md               # Web app documentation
```

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

2. **Start the web server:**
   ```bash
   ./start_web.sh
   # or
   python3 app.py
   ```

3. **Open in browser:**
   Navigate to `http://localhost:5001`

## ✨ Features

- Real-time stock data from Yahoo Finance
- ChatGPT-like conversational interface
- Comprehensive company information and financial metrics
- Responsive design for desktop and mobile
- No API keys required

## 📚 Documentation

- **WEB_APP_README.md** - Web application usage guide
- **STOCK_USAGE.md** - Stock analysis features
- **DEPLOYMENT_GUIDE.md** - Deployment instructions
- **QUICK_DEPLOY.md** - Quick deployment guide

## 🛠️ Technologies

- **Backend:** Flask (Python)
- **Frontend:** HTML, CSS, JavaScript
- **Data Source:** Yahoo Finance (yfinance)
- **Deployment:** Supports Fly.io, Render, and other platforms

## 📝 License

This project is open source and available for personal and commercial use.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

For detailed usage instructions, see [WEB_APP_README.md](WEB_APP_README.md)
