#!/bin/bash
# Create Modal secrets for deployment.
# Prerequisites: modal setup, MODAL_PROJECT in .env (e.g. cody-99083)
# If MODAL_PROJECT is set, add -e $MODAL_PROJECT to each modal command.
set -e
echo "Create Modal secrets. If MODAL_PROJECT is in .env (e.g. cody-99083), use:"
echo "  modal secret create -e \$MODAL_PROJECT supabase-credentials-develop SUPABASE_URL=... SUPABASE_SECRET_KEY=... TRANSACTION_POOLER_URL=..."
echo "  modal secret create -e \$MODAL_PROJECT app-config-develop ENVIRONMENT=develop JOB_STUCK_TIMEOUT_MINUTES=15"
echo ""
echo "Or without project (default workspace):"
echo "  modal secret create supabase-credentials-develop SUPABASE_URL=... SUPABASE_SECRET_KEY=... TRANSACTION_POOLER_URL=..."
echo "  modal secret create app-config-develop ENVIRONMENT=develop JOB_STUCK_TIMEOUT_MINUTES=15"
