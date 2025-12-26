#!/bin/bash
# Quick fix script for common issues

echo "🔍 Practical Data Work - Quick Diagnostics"
echo "=========================================="
echo ""

echo "1. Checking local files..."
echo "   Blog files:"
ls -1 blog/*.html | wc -l | xargs echo "      Found blog posts:"

echo "   Favicon files:"
ls favicon*.png favicon.ico 2>/dev/null | wc -l | xargs echo "      Found favicon files:"

echo "   Contact function:"
if [ -f "functions/api/contact.js" ]; then
    echo "      ✅ functions/api/contact.js exists"
else
    echo "      ❌ functions/api/contact.js MISSING"
fi

echo ""
echo "2. Checking routing files..."
if [ -f "_redirects" ]; then
    echo "   ⚠️  _redirects exists (may conflict with _routes.json)"
    echo "   Consider removing: git rm _redirects && git commit -m 'Remove _redirects' && git push"
else
    echo "   ✅ _redirects not present (good)"
fi

if [ -f "_routes.json" ]; then
    echo "   ✅ _routes.json exists"
else
    echo "   ❌ _routes.json MISSING"
fi

echo ""
echo "3. Checking git status..."
git status --short

echo ""
echo "4. Recent commits:"
git log --oneline -3

echo ""
echo "=========================================="
echo "🧪 Next Steps:"
echo "1. Visit: https://practicaldatawork.com/test-site.html"
echo "2. Run tests to identify specific issues"
echo "3. Apply fixes from IMMEDIATE_FIXES.md"
echo "=========================================="
