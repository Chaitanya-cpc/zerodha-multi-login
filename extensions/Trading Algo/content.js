
            // Trading Algo Extension
            console.log('Trading Algo extension loaded on Zerodha');
            
            // Add extension functionality here
            function initTradingAlgo() {
                console.log('Trading Algo initialized');
                // Add your trading algo features here
            }
            
            // Initialize when page loads
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', initTradingAlgo);
            } else {
                initTradingAlgo();
            }
            