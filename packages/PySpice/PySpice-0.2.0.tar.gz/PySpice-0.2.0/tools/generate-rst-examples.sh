####################################################################################################

examples=doc/sphinx/source/examples
# rm -rf ${examples}
mkdir -p ${examples}

echo
echo Generate RST examples files
# ./tools/generate-rst-examples --skip-circuit-figure --skip-figure
./tools/generate-rst-examples --force

echo
echo Run Sphinx
pushd doc/sphinx/
./make-html # --clean
popd

####################################################################################################
#
# End
#
####################################################################################################

