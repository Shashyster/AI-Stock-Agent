#!/bin/bash

# Script to help push your project to GitHub

echo "🚀 Setting up GitHub repository for your project..."
echo ""

# Check if remote already exists
if git remote get-url origin 2>/dev/null; then
    echo "✅ GitHub remote already configured:"
    git remote -v
    echo ""
    read -p "Do you want to push to existing remote? (y/n): " push_existing
    if [ "$push_existing" = "y" ]; then
        git push -u origin main
        echo "✅ Code pushed to GitHub!"
        exit 0
    fi
fi

echo "To connect this project to GitHub, you have two options:"
echo ""
echo "OPTION 1: Create repository via GitHub website (Recommended)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. Go to https://github.com/new"
echo "2. Create a new repository (name it something like 'stock-trader-information')"
echo "3. DO NOT initialize with README, .gitignore, or license"
echo "4. Copy the repository URL (e.g., https://github.com/YOUR_USERNAME/REPO_NAME.git)"
echo "5. Run this command with your repository URL:"
echo ""
echo "   git remote add origin YOUR_REPO_URL"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "OPTION 2: Use GitHub CLI (if installed)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "If you have GitHub CLI installed, run:"
echo "   gh auth login"
echo "   gh repo create stock-trader-information --public --source=. --remote=origin --push"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Interactive mode
read -p "Do you want to enter your GitHub repository URL now? (y/n): " enter_url
if [ "$enter_url" = "y" ]; then
    read -p "Enter your GitHub repository URL: " repo_url
    if [ -n "$repo_url" ]; then
        git remote add origin "$repo_url"
        git branch -M main
        echo ""
        echo "Pushing code to GitHub..."
        git push -u origin main
        if [ $? -eq 0 ]; then
            echo "✅ Successfully pushed to GitHub!"
            git remote -v
        else
            echo "❌ Push failed. Please check:"
            echo "   - Your repository URL is correct"
            echo "   - You have push access to the repository"
            echo "   - Your GitHub credentials are configured"
        fi
    fi
fi
