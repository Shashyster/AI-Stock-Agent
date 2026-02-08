// Wait for DOM to load
document.addEventListener('DOMContentLoaded', function() {
    const chatContainer = document.getElementById('chatContainer');
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendButton');
    
    if (!chatContainer || !messageInput || !sendButton) {
        console.error('Required DOM elements not found');
        return;
    }
    
    // Auto-resize textarea
    messageInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });
    
    // Collapsible section functionality
    function initCollapsibleSections() {
        document.querySelectorAll('.collapsible-header').forEach(header => {
            header.addEventListener('click', function() {
                const section = this.parentElement;
                section.classList.toggle('collapsed');
            });
        });
    }
    
    // Scroll to section
    function scrollToSection(sectionId) {
        const element = document.getElementById(sectionId);
        if (element) {
            element.scrollIntoView({ behavior: 'smooth', block: 'start' });
            // Highlight briefly
            element.style.transition = 'background 0.3s';
            element.style.background = '#fff3cd';
            setTimeout(() => {
                element.style.background = '';
            }, 1000);
        }
    }
    
    // Make functions globally accessible
    window.sendUserMessage = sendUserMessage;
    window.sendMessage = sendMessage;
    window.handleKeyDown = handleKeyDown;
    window.scrollToSection = scrollToSection;
    
    function sendUserMessage() {
        const message = messageInput.value.trim().toUpperCase();
        
        if (!message) {
            return;
        }
        
        // Extract ticker symbol (1-5 uppercase letters)
        const tickerMatch = message.match(/\b([A-Z]{1,5})\b/);
        if (!tickerMatch) {
            addMessage('bot', 'Please enter a valid ticker symbol (e.g., AAPL, MSFT, TSLA)');
            return;
        }
        
        const ticker = tickerMatch[1];
        
        // Add user message
        addMessage('user', ticker);
        
        // Clear input
        messageInput.value = '';
        messageInput.style.height = 'auto';
        
        // Disable send button
        sendButton.disabled = true;
        
        // Add loading message
        const loadingId = addLoadingMessage();
        
        // Fetch stock information
        fetch(`/api/stock/${ticker}`)
            .then(response => response.json())
            .then(data => {
                removeLoadingMessage(loadingId);
                sendButton.disabled = false;
                
                if (data.error) {
                    addMessage('bot', `❌ ${data.error}`);
                } else {
                    displayStockInfo(data);
                }
            })
            .catch(error => {
                removeLoadingMessage(loadingId);
                sendButton.disabled = false;
                addMessage('bot', `❌ Error: ${error.message}`);
            });
    }
    
    function sendMessage(ticker) {
        messageInput.value = ticker;
        sendUserMessage();
    }
    
    function handleKeyDown(event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            sendUserMessage();
        }
    }
    
    function addMessage(type, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        if (type === 'bot' && content.includes('❌')) {
            contentDiv.className += ' error-message';
            contentDiv.textContent = content;
        } else if (type === 'user') {
            contentDiv.textContent = content;
        } else {
            contentDiv.innerHTML = content;
        }
        
        messageDiv.appendChild(contentDiv);
        chatContainer.appendChild(messageDiv);
        
        // Remove welcome message if it exists
        const welcomeMessage = document.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.remove();
        }
        
        scrollToBottom();
    }
    
    function addLoadingMessage() {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message bot-message';
        messageDiv.id = 'loading-message';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.innerHTML = '<span class="loading"></span>Fetching stock information...';
        
        messageDiv.appendChild(contentDiv);
        chatContainer.appendChild(messageDiv);
        scrollToBottom();
        
        return 'loading-message';
    }
    
    function removeLoadingMessage(id) {
        const loadingMessage = document.getElementById(id);
        if (loadingMessage) {
            loadingMessage.remove();
        }
    }
    
    function scrollToBottom() {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
    
    function displayStockInfo(data) {
        let html = `
            <div class="stock-info">
                <div style="text-align: center; padding: 24px; background: var(--primary-dark); color: white; border-radius: 10px; margin-bottom: 20px; box-shadow: var(--shadow-md); border: 1px solid rgba(255, 255, 255, 0.1);">
                    <h2 style="margin: 0 0 6px 0; font-size: 26px; font-weight: 600; letter-spacing: -0.5px;">${data.companyName}</h2>
                    <div style="font-size: 14px; opacity: 0.9; font-weight: 400; letter-spacing: 0.5px;">${data.symbol}${data.shortName && data.shortName !== 'N/A' ? ` • ${data.shortName}` : ''}</div>
                </div>
                
                <div class="section-group" id="section-company">
                <div class="collapsible-section collapsed">
                    <div class="collapsible-header">Company Information</div>
                    <div class="collapsible-content">
                        <div class="collapsible-inner">
                <div class="info-grid">
                    <div class="info-item">
                        <div class="info-label">Sector</div>
                        <div class="info-value">${data.sector}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Industry</div>
                        <div class="info-value">${data.industry}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Country</div>
                        <div class="info-value">${data.country}</div>
                    </div>
                    ${data.city && data.city !== 'N/A' ? `
                    <div class="info-item">
                        <div class="info-label">Location</div>
                        <div class="info-value">${data.city}${data.state && data.state !== 'N/A' ? `, ${data.state}` : ''}</div>
                    </div>` : ''}
                    <div class="info-item">
                        <div class="info-label">Exchange</div>
                        <div class="info-value">${data.exchange}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Currency</div>
                        <div class="info-value">${data.currency}</div>
                    </div>
                    ${data.fullTimeEmployees && data.fullTimeEmployees !== 'N/A' ? `
                    <div class="info-item">
                        <div class="info-label">Employees</div>
                        <div class="info-value">${formatNumber(data.fullTimeEmployees)}</div>
                    </div>` : ''}
                    ${data.phone && data.phone !== 'N/A' ? `
                    <div class="info-item">
                        <div class="info-label">Phone</div>
                        <div class="info-value">${data.phone}</div>
                    </div>` : ''}
                    <div class="info-item">
                        <div class="info-label">Website</div>
                        <div class="info-value">${data.website !== 'N/A' ? `<a href="${data.website}" target="_blank" style="color: var(--accent-blue); text-decoration: none;">${data.website}</a>` : 'N/A'}</div>
                    </div>
                        </div>
                        ${data.description && data.description !== 'N/A' ? `<div style="margin-top: 12px; padding: 12px; background: #1a1a1a; border-radius: 8px; color: #e0e0e0; line-height: 1.6; font-size: 13px; border: 1px solid #333;"><strong style="color: var(--accent-teal);">About:</strong> ${data.description}</div>` : ''}
                    </div>
                </div>
                </div>
                
                ${data.companyOfficers && data.companyOfficers.length > 0 ? `
                <div class="section-group">
                <div class="collapsible-section collapsed">
                    <div class="collapsible-header">Key Executives</div>
                    <div class="collapsible-content">
                        <div class="collapsible-inner">
                            <div class="compact-grid">
                    ${data.companyOfficers.map(officer => `
                        <div class="info-item">
                            <div class="info-label">${officer.title || 'N/A'}</div>
                            <div class="info-value">${officer.name || 'N/A'}</div>
                            ${officer.totalPay && officer.totalPay.value ? `<div style="font-size: 11px; color: #b0b0b0; margin-top: 4px;">Total Pay: ${formatNumber(officer.totalPay.value)}</div>` : ''}
                        </div>
                            `).join('')}
                            </div>
                        </div>
                    </div>
                </div>
                </div>
                ` : ''}
                
                <div class="section-group" id="section-market">
                <div class="collapsible-section collapsed">
                    <div class="collapsible-header">Current Market Data</div>
                    <div class="collapsible-content">
                        <div class="collapsible-inner">
                            <div class="compact-grid">
                    <div class="info-item">
                        <div class="info-label">Current Price</div>
                        <div class="info-value">$${formatNumber(data.currentPrice)}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Previous Close</div>
                        <div class="info-value">$${formatNumber(data.previousClose)}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Open</div>
                        <div class="info-value">$${formatNumber(data.open)}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Day Range</div>
                        <div class="info-value">$${formatNumber(data.dayLow)} - $${formatNumber(data.dayHigh)}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">52 Week Range</div>
                        <div class="info-value">$${formatNumber(data.fiftyTwoWeekLow)} - $${formatNumber(data.fiftyTwoWeekHigh)}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Volume</div>
                        <div class="info-value">${formatNumber(data.volume)}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Avg Volume</div>
                        <div class="info-value">${formatNumber(data.averageVolume)}</div>
                            </div>
                        </div>
                    </div>
                </div>
                </div>
                
                <div class="section-group" id="section-financials">
                <div class="collapsible-section collapsed">
                    <div class="collapsible-header">Valuation Metrics</div>
                    <div class="collapsible-content">
                        <div class="collapsible-inner">
                            <div class="compact-grid">
                    <div class="info-item">
                        <div class="info-label">Market Cap</div>
                        <div class="info-value">${data.marketCap}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Enterprise Value</div>
                        <div class="info-value">${data.enterpriseValue}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">P/E Ratio (Trailing)</div>
                        <div class="info-value">${formatNumber(data.trailingPE)}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">P/E Ratio (Forward)</div>
                        <div class="info-value">${formatNumber(data.forwardPE)}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Price to Book</div>
                        <div class="info-value">${formatNumber(data.priceToBook)}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Price to Sales</div>
                        <div class="info-value">${formatNumber(data.priceToSales)}</div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="collapsible-section collapsed">
                    <div class="collapsible-header">Financial Performance</div>
                    <div class="collapsible-content">
                        <div class="collapsible-inner">
                            <div class="compact-grid">
                    <div class="info-item">
                        <div class="info-label">Revenue (TTM)</div>
                        <div class="info-value">${data.revenue}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Revenue Per Share</div>
                        <div class="info-value">$${formatNumber(data.revenuePerShare)}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Profit Margin</div>
                        <div class="info-value">${data.profitMargin}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Operating Margin</div>
                        <div class="info-value">${data.operatingMargin}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Return on Assets</div>
                        <div class="info-value">${data.returnOnAssets}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Return on Equity</div>
                        <div class="info-value">${data.returnOnEquity}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">EPS</div>
                        <div class="info-value">$${formatNumber(data.eps)}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Revenue Growth</div>
                        <div class="info-value">${data.revenueGrowth}</div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="collapsible-section collapsed">
                    <div class="collapsible-header">Dividend Information</div>
                    <div class="collapsible-content">
                        <div class="collapsible-inner">
                            <div class="compact-grid">
                    <div class="info-item">
                        <div class="info-label">Dividend Rate</div>
                        <div class="info-value">$${formatNumber(data.dividendRate)}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Dividend Yield</div>
                        <div class="info-value">${data.dividendYield}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Payout Ratio</div>
                        <div class="info-value">${data.payoutRatio}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Ex-Dividend Date</div>
                        <div class="info-value">${data.exDividendDate}</div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="collapsible-section collapsed">
                    <div class="collapsible-header">Analyst Recommendations</div>
                    <div class="collapsible-content">
                        <div class="collapsible-inner">
                            <div class="compact-grid">
                    <div class="info-item">
                        <div class="info-label">Recommendation</div>
                        <div class="info-value">${data.recommendation ? data.recommendation.toUpperCase() : 'N/A'}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Target Mean Price</div>
                        <div class="info-value">$${formatNumber(data.targetMeanPrice)}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Target High</div>
                        <div class="info-value">$${formatNumber(data.targetHighPrice)}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Target Low</div>
                        <div class="info-value">$${formatNumber(data.targetLowPrice)}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Analyst Opinions</div>
                        <div class="info-value">${data.numberOfAnalystOpinions}</div>
                            </div>
                        </div>
                    </div>
                </div>
                </div>
                
                ${data.hasHistoricalData ? `
                <div class="section-group">
                <div class="collapsible-section collapsed">
                    <div class="collapsible-header">Historical Stock Data</div>
                    <div class="collapsible-content">
                        <div class="collapsible-inner">
                            <div class="compact-grid">
                    <div class="info-item">
                        <div class="info-label">Data Period</div>
                        <div class="info-value">${data.dataStartDate} to ${data.dataEndDate}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Years of Data</div>
                        <div class="info-value">${data.yearsOfData ? data.yearsOfData.toFixed(1) : 'N/A'} years</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Total Trading Days</div>
                        <div class="info-value">${formatNumber(data.totalTradingDays)}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Starting Price</div>
                        <div class="info-value">$${formatNumber(data.startPrice)}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Total Return (All Time)</div>
                        <div class="info-value" style="color: ${data.totalReturnFromStart && parseFloat(data.totalReturnFromStart) >= 0 ? '#00ff88' : '#ff4444'}; font-weight: bold;">${data.totalReturnFromStart || 'N/A'}</div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="collapsible-section collapsed">
                    <div class="collapsible-header">All-Time Statistics</div>
                    <div class="collapsible-content">
                        <div class="collapsible-inner">
                            <div class="compact-grid">
                    <div class="info-item">
                        <div class="info-label">All-Time High</div>
                        <div class="info-value">$${formatNumber(data.allTimeHigh)}</div>
                        <div style="font-size: 11px; color: #b0b0b0;">${data.allTimeHighDate || ''}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">All-Time Low</div>
                        <div class="info-value">$${formatNumber(data.allTimeLow)}</div>
                        <div style="font-size: 11px; color: #b0b0b0;">${data.allTimeLowDate || ''}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">All-Time Average</div>
                        <div class="info-value">$${formatNumber(data.allTimeAverage)}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">All-Time Median</div>
                        <div class="info-value">$${formatNumber(data.allTimeMedian)}</div>
                    </div>
                    ${data.oneYearHigh ? `
                    <div class="info-item">
                        <div class="info-label">1-Year High</div>
                        <div class="info-value">$${formatNumber(data.oneYearHigh)}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">1-Year Low</div>
                        <div class="info-value">$${formatNumber(data.oneYearLow)}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">1-Year Return</div>
                        <div class="info-value" style="color: ${data.oneYearReturn && parseFloat(data.oneYearReturn) >= 0 ? '#00ff88' : '#ff4444'}; font-weight: bold;">${data.oneYearReturn || 'N/A'}</div>
                    </div>` : ''}
                    ${data.fiveYearHigh ? `
                    <div class="info-item">
                        <div class="info-label">5-Year High</div>
                        <div class="info-value">$${formatNumber(data.fiveYearHigh)}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">5-Year Low</div>
                        <div class="info-value">$${formatNumber(data.fiveYearLow)}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">5-Year Return</div>
                        <div class="info-value" style="color: ${data.fiveYearReturn && parseFloat(data.fiveYearReturn) >= 0 ? '#00ff88' : '#ff4444'}; font-weight: bold;">${data.fiveYearReturn || 'N/A'}</div>
                    </div>` : ''}
                </div>
                
                ${data.yearlyPerformance && data.yearlyPerformance.length > 0 ? `
                <h3>📅 Year-by-Year Performance</h3>
                <div style="overflow-x: auto; margin-top: 10px;">
                    <table style="width: 100%; border-collapse: collapse; background: #1a1a1a; border-radius: 8px; overflow: hidden; color: #e0e0e0;">
                        <thead>
                            <tr style="background: var(--primary-slate); color: white;">
                                <th style="padding: 12px; text-align: left; font-weight: 600;">Year</th>
                                <th style="padding: 12px; text-align: right; font-weight: 600;">Open</th>
                                <th style="padding: 12px; text-align: right; font-weight: 600;">Close</th>
                                <th style="padding: 12px; text-align: right; font-weight: 600;">High</th>
                                <th style="padding: 12px; text-align: right; font-weight: 600;">Low</th>
                                <th style="padding: 12px; text-align: right; font-weight: 600;">Return %</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${data.yearlyPerformance.slice().reverse().map((year, idx) => `
                                <tr style="border-bottom: 1px solid #333; background: #1a1a1a;">
                                    <td style="padding: 10px; font-weight: 600; color: #e0e0e0;">${year.year}</td>
                                    <td style="padding: 10px; text-align: right; color: #e0e0e0;">$${formatNumber(year.open)}</td>
                                    <td style="padding: 10px; text-align: right; color: #e0e0e0;">$${formatNumber(year.close)}</td>
                                    <td style="padding: 10px; text-align: right; color: #e0e0e0;">$${formatNumber(year.high)}</td>
                                    <td style="padding: 10px; text-align: right; color: #e0e0e0;">$${formatNumber(year.low)}</td>
                                    <td style="padding: 10px; text-align: right; color: ${year.return >= 0 ? '#00ff88' : '#ff4444'}; font-weight: 600;">${year.return.toFixed(2)}%</td>
                                </tr>
                            `).join('')}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
                ` : ''}
                </div>
                ` : ''}
                
                <div class="section-group">
                <div class="collapsible-section collapsed">
                    <div class="collapsible-header">Additional Financial Metrics</div>
                    <div class="collapsible-content">
                        <div class="collapsible-inner">
                            <div class="compact-grid">
                    ${data.totalCash && data.totalCash !== 'N/A' ? `
                    <div class="info-item">
                        <div class="info-label">Total Cash</div>
                        <div class="info-value">${data.totalCash}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Cash Per Share</div>
                        <div class="info-value">$${formatNumber(data.totalCashPerShare)}</div>
                    </div>` : ''}
                    ${data.totalDebt && data.totalDebt !== 'N/A' ? `
                    <div class="info-item">
                        <div class="info-label">Total Debt</div>
                        <div class="info-value">${data.totalDebt}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Debt Per Share</div>
                        <div class="info-value">$${formatNumber(data.totalDebtPerShare)}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Debt to Equity</div>
                        <div class="info-value">${formatNumber(data.debtToEquity)}</div>
                    </div>` : ''}
                    ${data.currentRatio && data.currentRatio !== 'N/A' ? `
                    <div class="info-item">
                        <div class="info-label">Current Ratio</div>
                        <div class="info-value">${formatNumber(data.currentRatio)}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Quick Ratio</div>
                        <div class="info-value">${formatNumber(data.quickRatio)}</div>
                    </div>` : ''}
                    ${data.bookValue && data.bookValue !== 'N/A' ? `
                    <div class="info-item">
                        <div class="info-label">Book Value</div>
                        <div class="info-value">$${formatNumber(data.bookValue)}</div>
                    </div>` : ''}
                    ${data.ebitda && data.ebitda !== 'N/A' ? `
                    <div class="info-item">
                        <div class="info-label">EBITDA</div>
                        <div class="info-value">${data.ebitda}</div>
                    </div>` : ''}
                    ${data.freeCashflow && data.freeCashflow !== 'N/A' ? `
                    <div class="info-item">
                        <div class="info-label">Free Cash Flow</div>
                        <div class="info-value">${data.freeCashflow}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Operating Cash Flow</div>
                        <div class="info-value">${data.operatingCashflow}</div>
                    </div>` : ''}
                    ${data.grossMargins && data.grossMargins !== 'N/A' ? `
                    <div class="info-item">
                        <div class="info-label">Gross Margins</div>
                        <div class="info-value">${data.grossMargins}</div>
                    </div>` : ''}
                    ${data.enterpriseToRevenue && data.enterpriseToRevenue !== 'N/A' ? `
                    <div class="info-item">
                        <div class="info-label">Enterprise to Revenue</div>
                        <div class="info-value">${formatNumber(data.enterpriseToRevenue)}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Enterprise to EBITDA</div>
                        <div class="info-value">${formatNumber(data.enterpriseToEbitda)}</div>
                    </div>` : ''}
                </div>
                
                <h3>📊 Stock Statistics</h3>
                <div class="info-grid">
                    ${data.beta && data.beta !== 'N/A' ? `
                    <div class="info-item">
                        <div class="info-label">Beta</div>
                        <div class="info-value">${formatNumber(data.beta)}</div>
                    </div>` : ''}
                    ${data.sharesOutstanding && data.sharesOutstanding !== 'N/A' ? `
                    <div class="info-item">
                        <div class="info-label">Shares Outstanding</div>
                        <div class="info-value">${data.sharesOutstanding}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Float Shares</div>
                        <div class="info-value">${data.floatShares}</div>
                    </div>` : ''}
                    ${data.sharesShort && data.sharesShort !== 'N/A' ? `
                    <div class="info-item">
                        <div class="info-label">Shares Short</div>
                        <div class="info-value">${data.sharesShort}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Short Ratio</div>
                        <div class="info-value">${formatNumber(data.shortRatio)}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Short % of Float</div>
                        <div class="info-value">${data.shortPercentOfFloat}</div>
                    </div>` : ''}
                    ${data.heldPercentInsiders && data.heldPercentInsiders !== 'N/A' ? `
                    <div class="info-item">
                        <div class="info-label">% Held by Insiders</div>
                        <div class="info-value">${data.heldPercentInsiders}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">% Held by Institutions</div>
                        <div class="info-value">${data.heldPercentInstitutions}</div>
                    </div>` : ''}
                    ${data['52WeekChange'] && data['52WeekChange'] !== 'N/A' ? `
                    <div class="info-item">
                        <div class="info-label">52-Week Change</div>
                        <div class="info-value" style="color: ${data['52WeekChange'] && parseFloat(data['52WeekChange']) >= 0 ? '#00ff88' : '#ff4444'}; font-weight: bold;">${data['52WeekChange']}</div>
                    </div>` : ''}
                </div>
                
                ${data.rsi && data.rsi !== 'N/A' ? `
                <h3>📊 Technical Indicators</h3>
                <div class="info-grid">
                    <div class="info-item">
                        <div class="info-label">RSI (14)</div>
                        <div class="info-value" style="color: ${data.rsi > 70 ? '#ff4444' : data.rsi < 30 ? '#00ff88' : '#e0e0e0'};">${data.rsi}</div>
                        <div style="font-size: 11px; color: #b0b0b0; margin-top: 4px;">
                            ${data.rsi > 70 ? 'Overbought' : data.rsi < 30 ? 'Oversold' : 'Neutral'}
                        </div>
                    </div>
                    ${data.macd && data.macd !== 'N/A' ? `
                    <div class="info-item">
                        <div class="info-label">MACD</div>
                        <div class="info-value">${formatNumber(data.macd)}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">MACD Signal</div>
                        <div class="info-value">${formatNumber(data.macdSignal)}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">MACD Histogram</div>
                        <div class="info-value" style="color: ${data.macdHistogram && parseFloat(data.macdHistogram) >= 0 ? '#00ff88' : '#ff4444'};">${formatNumber(data.macdHistogram)}</div>
                    </div>` : ''}
                    ${data.sma20 && data.sma20 !== 'N/A' ? `
                    <div class="info-item">
                        <div class="info-label">SMA (20)</div>
                        <div class="info-value">$${formatNumber(data.sma20)}</div>
                        ${data.priceVsSMA20 ? `<div style="font-size: 11px; color: ${data.priceVsSMA20 >= 0 ? '#00ff88' : '#ff4444'}; margin-top: 4px;">${data.priceVsSMA20 >= 0 ? '+' : ''}${data.priceVsSMA20.toFixed(2)}%</div>` : ''}
                    </div>
                    <div class="info-item">
                        <div class="info-label">SMA (50)</div>
                        <div class="info-value">$${formatNumber(data.sma50)}</div>
                        ${data.priceVsSMA50 ? `<div style="font-size: 11px; color: ${data.priceVsSMA50 >= 0 ? '#00ff88' : '#ff4444'}; margin-top: 4px;">${data.priceVsSMA50 >= 0 ? '+' : ''}${data.priceVsSMA50.toFixed(2)}%</div>` : ''}
                    </div>
                    <div class="info-item">
                        <div class="info-label">SMA (200)</div>
                        <div class="info-value">$${formatNumber(data.sma200)}</div>
                        ${data.priceVsSMA200 ? `<div style="font-size: 11px; color: ${data.priceVsSMA200 >= 0 ? '#00ff88' : '#ff4444'}; margin-top: 4px;">${data.priceVsSMA200 >= 0 ? '+' : ''}${data.priceVsSMA200.toFixed(2)}%</div>` : ''}
                    </div>` : ''}
                    ${data.bbUpper && data.bbUpper !== 'N/A' ? `
                    <div class="info-item">
                        <div class="info-label">Bollinger Upper</div>
                        <div class="info-value">$${formatNumber(data.bbUpper)}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Bollinger Middle</div>
                        <div class="info-value">$${formatNumber(data.bbMiddle)}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Bollinger Lower</div>
                        <div class="info-value">$${formatNumber(data.bbLower)}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">%B (Position in Bands)</div>
                        <div class="info-value">${data.bbPercentB ? data.bbPercentB.toFixed(2) + '%' : 'N/A'}</div>
                    </div>` : ''}
                    ${data.stochK && data.stochK !== 'N/A' ? `
                    <div class="info-item">
                        <div class="info-label">Stochastic %K</div>
                        <div class="info-value">${formatNumber(data.stochK)}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Stochastic %D</div>
                        <div class="info-value">${formatNumber(data.stochD)}</div>
                    </div>` : ''}
                    ${data.atr && data.atr !== 'N/A' ? `
                    <div class="info-item">
                        <div class="info-label">ATR (14)</div>
                        <div class="info-value">$${formatNumber(data.atr)}</div>
                    </div>` : ''}
                    ${data.volumeRatio ? `
                    <div class="info-item">
                        <div class="info-label">Volume Ratio (vs 20-day avg)</div>
                        <div class="info-value" style="color: ${data.volumeRatio >= 120 ? '#00ff88' : data.volumeRatio <= 80 ? '#ff4444' : '#e0e0e0'};">${data.volumeRatio.toFixed(1)}%</div>
                    </div>` : ''}
                    ${data.volatility30d ? `
                    <div class="info-item">
                        <div class="info-label">30-Day Volatility (Annualized)</div>
                        <div class="info-value">${data.volatility30d}</div>
                            </div>` : ''}
                        </div>
                    </div>
                </div>
                </div>
                ` : ''}
                
                ${data.aiAnalysis ? `
                <div class="section-group" id="section-ai">
                <div class="collapsible-section collapsed">
                    <div class="collapsible-header">AI Analysis and Predictions</div>
                    <div class="collapsible-content">
                        <div class="collapsible-inner">
                            <div class="ai-rating-box">
                                <div>
                                    <div class="rating-label">Overall Rating</div>
                                    <div class="rating-value">${data.aiAnalysis.overallRating || 'N/A'}</div>
                                </div>
                                <div>
                                    <div class="rating-label">Confidence Score</div>
                                    <div class="rating-value">${data.aiAnalysis.confidence || 0}/100</div>
                                </div>
                                <div>
                                    <div class="rating-label">Recommendation</div>
                                    <div class="rating-value" style="font-size: 18px;">${data.aiAnalysis.investmentRecommendation || 'N/A'}</div>
                                </div>
                            </div>
                            
                            <div class="summary-card">
                                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; font-size: 12px;">
                                    <div><strong>Outlook:</strong> ${data.aiAnalysis.longTermOutlook || 'N/A'}</div>
                                    <div><strong>Risk:</strong> ${data.aiAnalysis.riskLevel || 'N/A'}</div>
                                    ${data.aiAnalysis.priceTarget ? `<div><strong>Target:</strong> $${formatNumber(data.aiAnalysis.priceTarget)}</div>` : ''}
                                    <div><strong>Horizon:</strong> ${data.aiAnalysis.timeHorizon || '12-24 months'}</div>
                                </div>
                            </div>
                            
                            <div style="margin: 16px 0;">
                                <h4 style="color: var(--text-primary); margin-bottom: 10px; font-size: 14px; font-weight: 600;">Analysis Scores</h4>
                                <div class="compact-grid">
                        ${data.aiAnalysis.scores ? `
                                    <div class="compact-item">
                                        <div class="compact-label">Technical</div>
                                        <div class="compact-value">${data.aiAnalysis.scores.technical || 0}/100</div>
                                        <div class="score-bar"><div class="score-bar-fill" style="width: ${data.aiAnalysis.scores.technical || 0}%; background: #667eea;"></div></div>
                                    </div>
                                    <div class="compact-item">
                                        <div class="compact-label">Fundamental</div>
                                        <div class="compact-value">${data.aiAnalysis.scores.fundamental || 0}/100</div>
                                        <div style="margin-top: 4px; height: 4px; background: rgba(255,255,255,0.2); border-radius: 2px; overflow: hidden;"><div style="height: 100%; width: ${data.aiAnalysis.scores.fundamental || 0}%; background: white;"></div></div>
                                    </div>
                                    <div class="compact-item">
                                        <div class="compact-label">Momentum</div>
                                        <div class="compact-value">${data.aiAnalysis.scores.momentum || 0}/100</div>
                                        <div style="margin-top: 4px; height: 4px; background: rgba(255,255,255,0.2); border-radius: 2px; overflow: hidden;"><div style="height: 100%; width: ${data.aiAnalysis.scores.momentum || 0}%; background: white;"></div></div>
                                    </div>
                                    <div class="compact-item">
                                        <div class="compact-label">Value</div>
                                        <div class="compact-value">${data.aiAnalysis.scores.value || 0}/100</div>
                                        <div style="margin-top: 4px; height: 4px; background: rgba(255,255,255,0.2); border-radius: 2px; overflow: hidden;"><div style="height: 100%; width: ${data.aiAnalysis.scores.value || 0}%; background: white;"></div></div>
                                    </div>
                                    <div class="compact-item">
                                        <div class="compact-label">Growth</div>
                                        <div class="compact-value">${data.aiAnalysis.scores.growth || 0}/100</div>
                                        <div style="margin-top: 4px; height: 4px; background: rgba(255,255,255,0.2); border-radius: 2px; overflow: hidden;"><div style="height: 100%; width: ${data.aiAnalysis.scores.growth || 0}%; background: white;"></div></div>
                                    </div>
                                ` : ''}
                            </div>
                        </div>
                        
                        ${data.aiAnalysis.summary ? `
                        <div class="summary-card" style="margin-top: 12px;">
                            <h4 style="margin: 0 0 8px 0; font-size: 14px; font-weight: 600;">Quick Summary</h4>
                            <p style="margin: 0; font-size: 12px;">${data.aiAnalysis.summary}</p>
                        </div>
                        ` : ''}
                        
                        ${data.aiAnalysis.opportunities && data.aiAnalysis.opportunities.length > 0 ? `
                        <div class="collapsible-section collapsed" style="margin-top: 12px;">
                            <div class="collapsible-header">Key Opportunities (${data.aiAnalysis.opportunities.length})</div>
                            <div class="collapsible-content">
                                <div class="collapsible-inner">
                                    <ul style="margin: 0; padding-left: 20px; color: #e0e0e0; line-height: 1.6; font-size: 13px;">
                                        ${data.aiAnalysis.opportunities.map(opp => `<li style="margin-bottom: 6px; color: #e0e0e0;">${opp}</li>`).join('')}
                                    </ul>
                                </div>
                            </div>
                        </div>
                        ` : ''}
                        
                        ${data.aiAnalysis.riskFactors && data.aiAnalysis.riskFactors.length > 0 ? `
                        <div class="collapsible-section collapsed" style="margin-top: 12px;">
                            <div class="collapsible-header">Risk Factors (${data.aiAnalysis.riskFactors.length})</div>
                            <div class="collapsible-content">
                                <div class="collapsible-inner">
                                    <ul style="margin: 0; padding-left: 20px; color: #e0e0e0; line-height: 1.6; font-size: 13px;">
                                        ${data.aiAnalysis.riskFactors.map(risk => `<li style="margin-bottom: 6px; color: #e0e0e0;">${risk}</li>`).join('')}
                                    </ul>
                                </div>
                            </div>
                        </div>
                        ` : ''}
                        
                        ${data.aiAnalysis.technicalSignals && data.aiAnalysis.technicalSignals.length > 0 ? `
                        <div class="collapsible-section collapsed" style="margin-top: 12px;">
                            <div class="collapsible-header">Technical Signals (${data.aiAnalysis.technicalSignals.length})</div>
                            <div class="collapsible-content">
                                <div class="collapsible-inner">
                                    <div class="compact-grid">
                                        ${data.aiAnalysis.technicalSignals.map(signal => `
                                            <div class="compact-item" style="font-size: 12px;">${signal}</div>
                                        `).join('')}
                                    </div>
                                </div>
                            </div>
                        </div>
                        ` : ''}
                
                ${data.aiAnalysis.dcfValuation && data.aiAnalysis.dcfValuation.intrinsicValue ? `
                <div class="collapsible-section collapsed" style="margin-top: 12px;">
                    <div class="collapsible-header">DCF Valuation Model</div>
                    <div class="collapsible-content">
                        <div class="collapsible-inner">
                            <div class="compact-grid">
                                <div class="compact-item">
                                    <div class="compact-label">Intrinsic Value (DCF)</div>
                                    <div class="compact-value">$${formatNumber(data.aiAnalysis.dcfValuation.intrinsicValue)}</div>
                                </div>
                                <div class="compact-item">
                                    <div class="compact-label">Current Price</div>
                                    <div class="compact-value">$${formatNumber(data.aiAnalysis.dcfValuation.currentPrice)}</div>
                                </div>
                                <div class="compact-item">
                                    <div class="compact-label">Upside/Downside</div>
                                    <div class="compact-value" style="color: ${data.aiAnalysis.dcfValuation.upsideDownside >= 0 ? '#00ff88' : '#ff4444'};">
                                        ${data.aiAnalysis.dcfValuation.upsideDownside >= 0 ? '+' : ''}${data.aiAnalysis.dcfValuation.upsideDownside.toFixed(2)}%
                                    </div>
                                </div>
                            </div>
                            ${data.aiAnalysis.dcfValuation.assumptions ? `
                            <div style="margin-top: 12px; padding: 10px; background: #1a1a1a; border-radius: 6px; font-size: 11px; color: #e0e0e0; border: 1px solid #333;">
                                <strong>Assumptions:</strong> Growth: ${(data.aiAnalysis.dcfValuation.assumptions.growth_rate * 100).toFixed(1)}%, 
                                Discount: ${(data.aiAnalysis.dcfValuation.assumptions.discount_rate * 100).toFixed(1)}%, 
                                Terminal: ${(data.aiAnalysis.dcfValuation.assumptions.terminal_growth * 100).toFixed(1)}%
                            </div>
                            ` : ''}
                        </div>
                    </div>
                </div>
                ` : ''}
                
                ${data.aiAnalysis.relativeValuation && data.aiAnalysis.relativeValuation.overall_valuation ? `
                <div class="collapsible-section collapsed" style="margin-top: 12px;">
                    <div class="collapsible-header">Relative Valuation Analysis</div>
                    <div class="collapsible-content">
                        <div class="collapsible-inner">
                            <div class="compact-grid">
                                <div class="compact-item">
                                    <div class="compact-label">Overall Valuation vs Market</div>
                                    <div class="compact-value" style="color: ${data.aiAnalysis.relativeValuation.overall_valuation === 'CHEAP' ? '#00ff88' : data.aiAnalysis.relativeValuation.overall_valuation === 'EXPENSIVE' ? '#ff4444' : '#e0e0e0'};">
                                        ${data.aiAnalysis.relativeValuation.overall_valuation}
                                    </div>
                                </div>
                                ${data.aiAnalysis.relativeValuation.pe_vs_market && data.aiAnalysis.relativeValuation.pe_vs_market !== 'N/A' ? `
                                <div class="compact-item">
                                    <div class="compact-label">P/E vs Market</div>
                                    <div class="compact-value">${data.aiAnalysis.relativeValuation.pe_vs_market}</div>
                                </div>
                                ` : ''}
                                ${data.aiAnalysis.relativeValuation.pb_vs_market && data.aiAnalysis.relativeValuation.pb_vs_market !== 'N/A' ? `
                                <div class="compact-item">
                                    <div class="compact-label">P/B vs Market</div>
                                    <div class="compact-value">${data.aiAnalysis.relativeValuation.pb_vs_market}</div>
                                </div>
                                ` : ''}
                                ${data.aiAnalysis.relativeValuation.ps_vs_market && data.aiAnalysis.relativeValuation.ps_vs_market !== 'N/A' ? `
                                <div class="compact-item">
                                    <div class="compact-label">P/S vs Market</div>
                                    <div class="compact-value">${data.aiAnalysis.relativeValuation.ps_vs_market}</div>
                                </div>
                                ` : ''}
                            </div>
                        </div>
                </div>
                ` : ''}
                
                ${data.aiAnalysis.macroAnalysis && Object.keys(data.aiAnalysis.macroAnalysis).length > 0 ? `
                <div class="collapsible-section collapsed" style="margin-top: 12px; background: #1a1a1a; border-left: 3px solid var(--accent-yellow);">
                    <div class="collapsible-header" style="background: var(--bg-light); color: var(--text-primary); border-left: 3px solid var(--warning);">Macroeconomic Analysis</div>
                    <div class="collapsible-content">
                        <div class="collapsible-inner">
                            <div class="compact-grid">
                                ${data.aiAnalysis.macroAnalysis.sector_outlook ? `
                                <div class="compact-item">
                                    <div class="compact-label">Sector Outlook</div>
                                    <div class="compact-value">${data.aiAnalysis.macroAnalysis.sector_outlook}</div>
                                </div>
                                ` : ''}
                                ${data.aiAnalysis.macroAnalysis.interest_rate_sensitivity ? `
                                <div class="compact-item">
                                    <div class="compact-label">Interest Rate Sensitivity</div>
                                    <div class="compact-value">${data.aiAnalysis.macroAnalysis.interest_rate_sensitivity}</div>
                                </div>
                                ` : ''}
                                ${data.aiAnalysis.macroAnalysis.recession_resilience ? `
                                <div class="compact-item">
                                    <div class="compact-label">Recession Resilience</div>
                                    <div class="compact-value">${data.aiAnalysis.macroAnalysis.recession_resilience}</div>
                                </div>
                                ` : ''}
                            </div>
                    ${data.aiAnalysis.macroAnalysis.economic_pressures && data.aiAnalysis.macroAnalysis.economic_pressures.length > 0 ? `
                    <div style="margin-top: 15px; padding: 12px; background: #1a1a1a; border-radius: 8px; color: #e0e0e0; border: 1px solid #333;">
                        <strong style="color: var(--accent-yellow);">Economic Pressures:</strong>
                        <ul style="margin: 8px 0 0 20px; color: #e0e0e0; line-height: 1.6;">
                            ${data.aiAnalysis.macroAnalysis.economic_pressures.map(pressure => `<li>${pressure}</li>`).join('')}
                            </ul>
                            ` : ''}
                        </div>
                    </div>
                </div>
                ` : ''}
                
                ${data.aiAnalysis.sentimentAnalysis && Object.keys(data.aiAnalysis.sentimentAnalysis).length > 0 ? `
                <div class="collapsible-section collapsed" style="margin-top: 12px; background: #d1ecf1; border-left: 3px solid #17a2b8;">
                    <div class="collapsible-header" style="background: var(--bg-light); color: var(--text-primary); border-left: 3px solid var(--accent-teal);">Market Sentiment Analysis</div>
                    <div class="collapsible-content">
                        <div class="collapsible-inner">
                            <div class="compact-grid">
                                ${data.aiAnalysis.sentimentAnalysis.overall_sentiment ? `
                                <div class="compact-item">
                                    <div class="compact-label">Overall Sentiment</div>
                                    <div class="compact-value" style="color: ${data.aiAnalysis.sentimentAnalysis.overall_sentiment === 'BULLISH' ? '#00ff88' : data.aiAnalysis.sentimentAnalysis.overall_sentiment === 'BEARISH' ? '#ff4444' : '#e0e0e0'};">
                                        ${data.aiAnalysis.sentimentAnalysis.overall_sentiment}
                                    </div>
                                </div>
                                ` : ''}
                                ${data.aiAnalysis.sentimentAnalysis.analyst_sentiment ? `
                                <div class="compact-item">
                                    <div class="compact-label">Analyst Sentiment</div>
                                    <div class="compact-value">${data.aiAnalysis.sentimentAnalysis.analyst_sentiment}</div>
                                </div>
                                ` : ''}
                                ${data.aiAnalysis.sentimentAnalysis.momentum_sentiment ? `
                                <div class="compact-item">
                                    <div class="compact-label">Momentum Sentiment</div>
                                    <div class="compact-value">${data.aiAnalysis.sentimentAnalysis.momentum_sentiment}</div>
                                </div>
                                ` : ''}
                                ${data.aiAnalysis.sentimentAnalysis.retail_interest ? `
                                <div class="compact-item">
                                    <div class="compact-label">Retail Interest</div>
                                    <div class="compact-value">${data.aiAnalysis.sentimentAnalysis.retail_interest}</div>
                                </div>
                                ` : ''}
                                ${data.aiAnalysis.sentimentAnalysis.institutional_interest ? `
                                <div class="compact-item">
                                    <div class="compact-label">Institutional Interest</div>
                                    <div class="compact-value">${data.aiAnalysis.sentimentAnalysis.institutional_interest}</div>
                                </div>
                                ` : ''}
                            </div>
                    ${data.aiAnalysis.sentimentAnalysis.indicators && data.aiAnalysis.sentimentAnalysis.indicators.length > 0 ? `
                    <div style="margin-top: 15px; padding: 12px; background: #1a1a1a; border-radius: 8px; font-size: 13px; color: #e0e0e0; border: 1px solid #333;">
                        <strong>Sentiment Indicators:</strong>
                        <ul style="margin: 8px 0 0 20px; color: #e0e0e0; line-height: 1.6;">
                            ${data.aiAnalysis.sentimentAnalysis.indicators.map(ind => `<li>${ind}</li>`).join('')}
                            </ul>
                            ` : ''}
                        </div>
                    </div>
                </div>
                ` : ''}
                        </div>
                    </div>
                </div>
                ` : ''}
                
                ${data.aiAnalysis.detailedReasoning && Object.keys(data.aiAnalysis.detailedReasoning).length > 0 ? `
                <div class="collapsible-section collapsed" style="margin-top: 16px;">
                    <div class="collapsible-header" style="background: var(--primary-slate); color: white; font-size: 15px; font-weight: 600;">Detailed Analysis: Why This Recommendation?</div>
                    <div class="collapsible-content">
                        <div class="collapsible-inner" style="background: var(--primary-slate); color: white; padding: 18px;">
                    
                            ${data.aiAnalysis.detailedReasoning.executiveSummary ? `
                            <div class="summary-card" style="margin-bottom: 12px;">
                                <h4 style="margin: 0 0 8px 0; font-size: 14px; font-weight: 600;">Executive Summary</h4>
                                <p style="margin: 0; font-size: 12px; line-height: 1.6;">${data.aiAnalysis.detailedReasoning.executiveSummary}</p>
                            </div>
                            ` : ''}
                            
                            ${data.aiAnalysis.detailedReasoning.technicalAnalysis && data.aiAnalysis.detailedReasoning.technicalAnalysis.summary ? `
                            <div class="collapsible-section collapsed" style="margin-bottom: 12px; background: rgba(255,255,255,0.1);">
                                <div class="collapsible-header" style="background: rgba(255,255,255,0.12); color: white; font-size: 13px;">Technical Analysis (Score: ${data.aiAnalysis.detailedReasoning.technicalAnalysis.score || 0}/100)</div>
                                <div class="collapsible-content">
                                    <div class="collapsible-inner" style="padding: 12px; font-size: 12px; line-height: 1.6;">
                                        <p style="margin: 0 0 8px 0;">${data.aiAnalysis.detailedReasoning.technicalAnalysis.summary}</p>
                                        ${data.aiAnalysis.detailedReasoning.technicalAnalysis.keyIndicators && data.aiAnalysis.detailedReasoning.technicalAnalysis.keyIndicators.length > 0 ? `
                                        <ul style="margin: 8px 0 0 20px; padding: 0;">
                                            ${data.aiAnalysis.detailedReasoning.technicalAnalysis.keyIndicators.map(ind => `<li style="margin-bottom: 4px;">${ind}</li>`).join('')}
                                        </ul>
                                        ` : ''}
                                    </div>
                                </div>
                            </div>
                            ` : ''}
                            
                            ${data.aiAnalysis.detailedReasoning.fundamentalAnalysis && data.aiAnalysis.detailedReasoning.fundamentalAnalysis.summary ? `
                            <div class="collapsible-section collapsed" style="margin-bottom: 12px; background: rgba(255,255,255,0.1);">
                                <div class="collapsible-header" style="background: rgba(255,255,255,0.12); color: white; font-size: 13px;">Fundamental Analysis (Score: ${data.aiAnalysis.detailedReasoning.fundamentalAnalysis.score || 0}/100)</div>
                                <div class="collapsible-content">
                                    <div class="collapsible-inner" style="padding: 12px; font-size: 12px; line-height: 1.6;">
                                        <p style="margin: 0 0 8px 0;">${data.aiAnalysis.detailedReasoning.fundamentalAnalysis.summary}</p>
                                        ${data.aiAnalysis.detailedReasoning.fundamentalAnalysis.keyMetrics && data.aiAnalysis.detailedReasoning.fundamentalAnalysis.keyMetrics.length > 0 ? `
                                        <ul style="margin: 8px 0 0 20px; padding: 0;">
                                            ${data.aiAnalysis.detailedReasoning.fundamentalAnalysis.keyMetrics.map(metric => `<li style="margin-bottom: 4px;">${metric}</li>`).join('')}
                                        </ul>
                                        ` : ''}
                                    </div>
                                </div>
                            </div>
                            ` : ''}
                            
                            ${data.aiAnalysis.detailedReasoning.valuationAnalysis && data.aiAnalysis.detailedReasoning.valuationAnalysis.summary ? `
                            <div class="collapsible-section collapsed" style="margin-bottom: 12px; background: rgba(255,255,255,0.1);">
                                <div class="collapsible-header" style="background: rgba(255,255,255,0.12); color: white; font-size: 13px;">Valuation Analysis</div>
                                <div class="collapsible-content">
                                    <div class="collapsible-inner" style="padding: 12px; font-size: 12px; line-height: 1.6;">
                                        <p style="margin: 0 0 8px 0;">${data.aiAnalysis.detailedReasoning.valuationAnalysis.summary}</p>
                                        ${data.aiAnalysis.detailedReasoning.valuationAnalysis.details && data.aiAnalysis.detailedReasoning.valuationAnalysis.details.length > 0 ? `
                                        <ul style="margin: 8px 0 0 20px; padding: 0;">
                                            ${data.aiAnalysis.detailedReasoning.valuationAnalysis.details.map(detail => `<li style="margin-bottom: 4px;">${detail}</li>`).join('')}
                                        </ul>
                                        ` : ''}
                                    </div>
                                </div>
                            </div>
                            ` : ''}
                            
                            ${data.aiAnalysis.detailedReasoning.macroEconomicFactors && data.aiAnalysis.detailedReasoning.macroEconomicFactors.summary ? `
                            <div class="collapsible-section collapsed" style="margin-bottom: 12px; background: rgba(255,255,255,0.1);">
                                <div class="collapsible-header" style="background: rgba(255,255,255,0.12); color: white; font-size: 13px;">Macroeconomic Factors</div>
                                <div class="collapsible-content">
                                    <div class="collapsible-inner" style="padding: 12px; font-size: 12px; line-height: 1.6;">
                                        <p style="margin: 0;">${data.aiAnalysis.detailedReasoning.macroEconomicFactors.summary}</p>
                                    </div>
                                </div>
                            </div>
                            ` : ''}
                            
                            ${data.aiAnalysis.detailedReasoning.sentimentFactors && data.aiAnalysis.detailedReasoning.sentimentFactors.summary ? `
                            <div class="collapsible-section collapsed" style="margin-bottom: 12px; background: rgba(255,255,255,0.1);">
                                <div class="collapsible-header" style="background: rgba(255,255,255,0.12); color: white; font-size: 13px;">Market Sentiment</div>
                                <div class="collapsible-content">
                                    <div class="collapsible-inner" style="padding: 12px; font-size: 12px; line-height: 1.6;">
                                        <p style="margin: 0;">${data.aiAnalysis.detailedReasoning.sentimentFactors.summary}</p>
                                    </div>
                                </div>
                            </div>
                            ` : ''}
                            
                            ${data.aiAnalysis.detailedReasoning.riskAssessment && data.aiAnalysis.detailedReasoning.riskAssessment.summary ? `
                            <div class="collapsible-section collapsed" style="margin-bottom: 12px; background: rgba(220, 53, 69, 0.2);">
                                <div class="collapsible-header" style="background: rgba(231, 76, 60, 0.2); color: white; font-size: 13px;">Risk Assessment (${data.aiAnalysis.detailedReasoning.riskAssessment.riskLevel || 'MEDIUM'})</div>
                                <div class="collapsible-content">
                                    <div class="collapsible-inner" style="padding: 12px; font-size: 12px; line-height: 1.6;">
                                        <p style="margin: 0;">${data.aiAnalysis.detailedReasoning.riskAssessment.summary}</p>
                                    </div>
                                </div>
                            </div>
                            ` : ''}
                            
                            ${data.aiAnalysis.detailedReasoning.investmentThesis ? `
                            <div class="summary-card" style="margin-bottom: 12px;">
                                <h4 style="margin: 0 0 8px 0; font-size: 14px; font-weight: 600;">Investment Thesis</h4>
                                <p style="margin: 0; font-size: 12px; line-height: 1.6;">${data.aiAnalysis.detailedReasoning.investmentThesis}</p>
                            </div>
                            ` : ''}
                            
                            ${data.aiAnalysis.detailedReasoning.conclusion ? `
                            <div class="summary-card" style="border: 2px solid rgba(255,255,255,0.3);">
                                <h4 style="margin: 0 0 8px 0; font-size: 14px; font-weight: 600;">Final Conclusion</h4>
                                <p style="margin: 0; font-size: 12px; line-height: 1.6;">${data.aiAnalysis.detailedReasoning.conclusion}</p>
                            </div>
                            ` : ''}
                        </div>
                    </div>
                </div>
                ` : ''}
            </div>
        `;
        
        addMessage('bot', html);
        
        // Initialize collapsible sections after a short delay
        setTimeout(() => {
            initCollapsibleSections();
        }, 100);
    }
    
    function formatNumber(value) {
        if (value === 'N/A' || value === null || value === undefined) {
            return 'N/A';
        }
        if (typeof value === 'number') {
            return value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        }
        return value;
    }
});

