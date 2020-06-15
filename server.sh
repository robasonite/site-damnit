# NOTE: Python 3x required to make Site Damnit work!
# Go to https://sass-lang.com/install and pick the best option to install 'sass' on your system.
echo "Running SASS"
sass --style=compressed templates/sass/main.scss templates/static/css/main.css

# This one requires Node.js (https://nodejs.org/en/).
# Should be as simple as 'npm install -g terser'
echo "Running Terser"
terser templates/terser-js/header/*.js -c toplevel,sequences=false,drop_console=true --mangle > templates/static/js/header.js
terser templates/terser-js/footer/*.js -c toplevel,sequences=false,drop_console=true --mangle > templates/static/js/footer.js
echo "Running Site Damnit"
python damnit.py build

# This section is required to build the LunrJS index.
#cat output/index.json | node lunr-build-index.js > output/lunr.json
#rm output/index.json

# Serve the site for testing.
cd output
python -m http.server
cd ..

