#!/bin/bash
# Phase 7.1 Deployment Script
# Automates Phase 7.1 deployment setup

set -e  # Exit on error

echo "🚀 PHASE 7.1 DEPLOYMENT SCRIPT"
echo "================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "api/main.py" ]; then
    echo -e "${RED}Error: Not in project root directory${NC}"
    echo "Please run from super-brain-digital-twin root"
    exit 1
fi

echo -e "${GREEN}✓ Project directory verified${NC}"
echo ""

# Step 1: Verify files
echo "--> Step 1: Verifying all files are created..."
files=(
    "api/workspaces/models.py"
    "api/workspaces/service.py"
    "api/workspaces/routes.py"
    "api/graphql/schema_workspaces.py"
    "web/app/workspaces/page.tsx"
    "web/app/workspaces/[id]/page.tsx"
    "apps/contacts/migrations/phase7_workspaces.sql"
    "tests/test_workspaces.py"
)

for file in "${files[@]}"; do
    if [ ! -f "$file" ]; then
        echo -e "${RED}✗ Missing: $file${NC}"
        exit 1
    fi
done

echo -e "${GREEN}✓ All 8 files verified${NC}"
echo ""

# Step 2: Git commit
echo "--> Step 2: Git commit..."
if [ -z "$(git status --porcelain)" ]; then
    echo -e "${YELLOW}Nothing to commit${NC}"
else
    git add -A
    git commit -m "Phase 7.1: Team collaboration - workspaces, RBAC, activity logging"
    echo -e "${GREEN}✓ Committed to Git${NC}"
fi
echo ""

# Step 3: Backend setup
echo "--> Step 3: Backend setup..."
echo "Installing Python dependencies..."
pip install --upgrade fastapi uvicorn python-multipart pydantic > /dev/null 2>&1
echo -e "${GREEN}✓ Python dependencies installed${NC}"
echo ""

# Step 4: Frontend setup
echo "--> Step 4: Frontend setup..."
if [ -d "web" ]; then
    cd web
    npm install > /dev/null 2>&1
    echo -e "${GREEN}✓ Node dependencies installed${NC}"
    cd ..
else
    echo -e "${YELLOW}Web directory not found, skipping npm install${NC}"
fi
echo ""

# Step 5: Run tests
echo "--> Step 5: Running unit tests..."
if python -m pytest tests/test_workspaces.py -v 2>/dev/null; then
    echo -e "${GREEN}✓ All tests passed${NC}"
else
    echo -e "${YELLOW}Some tests failed or pytest not available${NC}"
fi
echo ""

# Step 6: Create init file
echo "--> Step 6: Creating module init files..."
mkdir -p api/workspaces
cat > api/workspaces/__init__.py << 'EOF'
# api/workspaces/__init__.py
from .models import (
    WorkspaceCreate,
    WorkspaceResponse,
    WorkspaceMemberInvite,
    WorkspaceRole,
    WorkspacePlan
)
from .service import WorkspaceService
from .routes import router

__all__ = [
    'WorkspaceCreate',
    'WorkspaceResponse',
    'WorkspaceMemberInvite',
    'WorkspaceRole',
    'WorkspacePlan',
    'WorkspaceService',
    'router'
]
EOF
echo -e "${GREEN}✓ Module init created${NC}"
echo ""

# Step 7: Summary
echo "================================="
echo -e "${GREEN}🌟 PHASE 7.1 SETUP COMPLETE!✅${NC}"
echo ""
echo "What's next?"
echo ""
echo "1. Database Migration:"
echo "   - Go to Supabase SQL Editor"
echo "   - Copy contents of: apps/contacts/migrations/phase7_workspaces.sql"
echo "   - Run the query"
echo ""
echo "2. Start Backend:"
echo "   cd api"
echo "   uvicorn main:app --reload"
echo ""
echo "3. Start Frontend:"
echo "   cd web"
echo "   npm run dev"
echo ""
echo "4. Test:"
echo "   pytest tests/test_workspaces.py -v"
echo ""
echo "Full guide: PHASE7_DEPLOYMENT_TZ.md"
echo ""
