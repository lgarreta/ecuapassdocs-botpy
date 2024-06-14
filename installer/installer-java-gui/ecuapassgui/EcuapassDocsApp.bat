taskkill /IM "ecuapass_app.exe" /F

echo "Actualizando Ecuapassdocs..."

git reset --hard
git pull

ecuapass_app.exe
