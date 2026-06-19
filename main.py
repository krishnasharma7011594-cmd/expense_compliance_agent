import argparse
import asyncio
import json
import sys
import structlog
from typing import Dict, Any

# Configure logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer()
    ]
)
logger = structlog.get_logger(__name__)

def main():
    try:
        from config.settings import settings
        from agents.expense_agent import expense_agent
        
        parser = argparse.ArgumentParser(description="Google ADK Expense Compliance Agent")
        parser.add_argument("--mode", choices=["interactive", "cli", "test", "eval"], default="interactive")
        parser.add_argument("--input", type=str)
        args = parser.parse_args()

        if args.mode == "interactive":
            asyncio.run(run_interactive_mode(expense_agent))
        elif args.mode == "cli":
            asyncio.run(run_cli_mode(expense_agent, args.input))
        elif args.mode == "test":
            run_test_mode()
        elif args.mode == "eval":
            run_eval_mode()

    except Exception as e:
        print(f"\nCRITICAL STARTUP ERROR: {e}")
        sys.exit(1)

async def run_interactive_mode(agent):
    print("\n--- 🤖 Expense Compliance Agent Interactive Mode ---")
    print("Enter expense details to audit (e.g., Merchant, Amount, Category).")
    
    user_id = "cli_tester"
    while True:
        try:
            merchant = input("\nMerchant Name (or 'exit'): ")
            if merchant.lower() == 'exit': break
            
            amount_str = input("Amount: ")
            try:
                amount = float(amount_str)
            except ValueError:
                amount = 0.0
                
            category = input("Category (software, meals, travel, etc.): ")
            
            expense_data = {
                "transaction_id": f"TXN_{int(asyncio.get_event_loop().time())}",
                "merchant_name": merchant,
                "amount": amount,
                "currency": "USD",
                "category": category or "general",
                "description": "Interactive session entry",
                "timestamp": "2024-06-19T10:00:00Z"
            }
            
            print(f"⏳ Auditing {merchant} (${amount})...")
            result = await agent.process_expense(user_id, expense_data)
            
            print("\n📋 AUDIT VERDICT:")
            print(json.dumps(result, indent=2))
            
        except EOFError: break
        except Exception as e:
            print(f"Error during audit: {e}")

async def run_cli_mode(agent, data_path: str):
    with open(data_path, 'r') as f:
        data = json.load(f)
    result = await agent.process_expense("cli_user", data)
    print(json.dumps(result, indent=2))

def run_test_mode():
    import subprocess
    subprocess.run(["pytest", "evals/test_runner.py", "-v"])

def run_eval_mode():
    import subprocess
    subprocess.run(["python", "evals/test_runner.py"])

if __name__ == "__main__":
    main()
