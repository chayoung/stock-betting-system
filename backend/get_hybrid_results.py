import sys
import os
import json

# Add current directory to path to import backtest
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backtest import run_backtest

def main():
    start_date = "2026-02-01"
    end_date = "2026-02-20"
    
    # run_backtest may need to be modified to pass mode, 
    # but since I set HYBRID as default in select_betting_stocks, it should work.
    
    print(f"Running backtest (Hybrid Strategy) for {start_date} to {end_date}...")
    try:
        results = run_backtest(start_date, end_date)
        
        if "error" in results:
            print(f"Error: {results['error']}")
            return

        print("\n[Summary - Hybrid Strategy]")
        print(f"Total Profit Rate: {results['summary']['total_profit_rate']}%")
        print(f"Win Rate: {results['summary']['win_rate']}%")
        print(f"Total Trades: {results['summary']['total_trades']}")
        
        print("\n[Daily Results]")
        for day in results['daily_returns']:
            print(f"{day['date']}: Avg Return {day['avg_return']}% (KOSPI: {day['kospi_return']}%), Trades: {day['count']}")
            
    except Exception as e:
        print(f"Exception occurred: {e}")

if __name__ == "__main__":
    main()
