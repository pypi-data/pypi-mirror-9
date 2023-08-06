#!/bin/bash
PASSCOUNT=0
FAILCOUNT=0
echo testing tooltool\'s command line interface

function fail() {
    echo TEST-FAIL: "$@"
    FAILCOUNT=$((FAILCOUNT + 1))
}

function pass() {
    echo TEST-PASS: "$@"
    PASSCOUNT=$((PASSCOUNT + 1))
}

function error() {
    echo TEST-ERROR: "$@"
}

function info() {
    echo TEST-INFO: "$@"
}

function setup() {
    #cleanup
    rm -rf manifest.tt a b c d test_file.ogg
    echo 1 > a
    echo 2 > b
    echo 3 > c
    echo 4 > d
}

function assert_zero() {
    if [ $1 -ne 0 ] ; then
        fail "$2"
    else
        pass "$2"
    fi
}

function assert_nonzero() {
    if [ $1 -eq 0 ] ; then
        fail "$2"
    else
        pass "$2"
    fi
}

# set up a tooltool "server"

rm -rf testdir
mkdir -p testdir
cd testdir

mkdir serverdir
python -c '
import SimpleHTTPServer, SocketServer, os
Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
httpd = SocketServer.TCPServer(("", 0), Handler)
with open("web_port", "w") as f:
    print >>f, httpd.socket.getsockname()[1]
os.chdir("serverdir")
httpd.serve_forever()
' &
while ! test -f web_port; do sleep 0.1; done
TEST_BASE_URL="http://localhost:$(<web_port)"
rm web_port
if ! curl -LI $TEST_BASE_URL &> /dev/null; then
    echo "ERROR: web server not running"
    exit 1
fi

trap "kill %1; wait" EXIT SIGINT SIGQUIT SIGTERM

# set up the serverdir

mkdir serverdir/sha512
for content in 1 2; do
    sha512=$(echo $content | sha512sum | sed -e 's/ .*//')
    echo $content > serverdir/sha512/$sha512
done

# set up tooltool

tt="../tooltool.py --verbose --url $TEST_BASE_URL"
info "$tt"

# tests

setup
$tt list
assert_nonzero $? "listing empty manifest"
###############
setup
$tt add a
assert_zero $? "adding file to manifest"
test -f manifest.tt
assert_zero $? "manifest file created"
###############
$tt add a
# TODO assert_nonzero $? "adding the same file a second time"
###############
$tt add notafile
#TODO this will always pass until the program is fixed
assert_nonzero $? "adding non-existant file"
###############
$tt list
assert_zero $? "listing valid manifest"
###############
rm a
$tt list
assert_zero $? "listing should work when there are absent files"
###############
$tt add b
assert_zero $? "adding a second file"
###############
$tt add b
assert_nonzero $? "adding a duplicate file shouldn't work"
###############
rm -f a b
$tt fetch a
assert_zero $? "fetching a single file"
echo 1 > ta
diff a ta &> /dev/null
assert_zero $? "a fetched correctly"
rm -f ta
test ! -e b
assert_zero $? "un-fetched file should be absent"
##############
$tt fetch
assert_zero $? "fetching all files in manifest"
test -f a
assert_zero $? "a fetched"
test -f b
assert_zero $? "b fetched"
##############
echo OMGWTFBBQ > a
$tt fetch a
assert_zero $? "should overwrite bad files"
test `cat a` -eq 1
assert_zero $? "contents should be per manifest"
#############
$tt validate
assert_zero $? "validate works"








echo ==============================================
echo TEST-PASSES: $PASSCOUNT, TEST-FAILS: $FAILCOUNT
if [[ $FAILCOUNT -ne 0 || $PASSCOUNT -lt 1 ]] ; then
    echo TESTS FAILED
    exit 1
else
    (cd .. && rm -rf testdir)
    exit 0
fi
