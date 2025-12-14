# Git Workflow: Deleting Files in `main` and Syncing Branches

When you delete files in the `main` branch, you often want those deletions reflected in other branches. Here’s the streamlined workflow:

## Steps

1. **Delete in `main`**
 ```bash
    git switch main
    git rm path/to/file        # or delete manually, then stage
    git commit -m "Remove unwanted files"
    git push origin main

2. **Sync with another branch**
```bash
    git switch your-branch
    git rebase main
    git push origin your-branch --force-with-lease
