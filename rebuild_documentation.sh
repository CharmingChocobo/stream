#!/bin/bash
cd docs/source
sphinx-apidoc -o modules ../../streamsim/src --separate --force
sed -i '' 's/automodule:: src\./automodule:: streamsim.src./g' modules/*.rst
sed -i '' 's/^src\./streamsim.src./g' modules/*.rst
cd ../..
make clean && make html
echo "✅ Documentation rebuilt successfully!"