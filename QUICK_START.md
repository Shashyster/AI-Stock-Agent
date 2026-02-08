# Quick Start - Type Just the Ticker!

## ✅ Setup Complete!

You can now type **just the ticker symbol** in your terminal:

```bash
AAPL
MSFT
TSLA
GOOGL
NVDA
```

That's it! No need to type `./stock` or `python3 "Stock Trader Information.py"` anymore.

## How It Works

A function has been added to your `~/.zshrc` file that automatically detects when you type a ticker symbol (1-5 uppercase letters) and runs the stock information script.

## Activate It Now

If you want to use it in your **current terminal session**, run:
```bash
source ~/.zshrc
```

Or simply **open a new terminal window** - it will work automatically!

## Examples

```bash
# Just type the ticker:
AAPL    # Apple
MSFT    # Microsoft
TSLA    # Tesla
GOOGL   # Google
NVDA    # NVIDIA
META    # Meta/Facebook
AMD     # AMD
INTC    # Intel
```

## Notes

- Works with **any valid ticker symbol** (1-5 uppercase letters)
- Works with NASDAQ, NYSE, and other exchanges
- If you type a command that doesn't exist and it looks like a ticker, it will run the stock script
- Regular commands still work normally (ls, cd, etc.)

## Disable (if needed)

If you ever want to disable this feature, just comment out or remove the `command_not_found_handler` function in your `~/.zshrc` file.


