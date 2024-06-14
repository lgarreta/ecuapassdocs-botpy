:: Initialize git repo and fetch latest release
git init
git remote add origin https://github.com/lgarreta/ecuapassdocs-windev.git
git fetch origin main
git reset --hard origin/main
