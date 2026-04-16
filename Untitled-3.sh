
# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$('/opt/anaconda3/bin/conda' 'shell.zsh' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "/opt/anaconda3/etc/profile.d/conda.sh" ]; then
        . "/opt/anaconda3/etc/profile.d/conda.sh"
    else
        export PATH="/opt/anaconda3/bin:$PATH"
    fi
fi
unset __conda_setup
# <<< conda initialize <<<

# Stock ticker command handler - allows typing just the ticker symbol (e.g., AAPL)
command_not_found_handler() {
    local cmd="$1"
    # Check if command looks like a stock ticker (1-5 uppercase letters, no special chars)
    if [[ "$cmd" =~ ^[A-Z]{1,5}$ ]]; then
        # Run the stock information script
        python3 "/Users/shashy/Desktop/AIProjects/Stock Trader Information.py" "$cmd"
        return $?
    fi
    # If not a ticker, return error (command not found)
    return 127
}

