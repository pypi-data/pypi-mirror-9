#!/bin/bash
#   author:martinmhan@yahoo.com date:  22/04/2014
#   regexf is a bash command line interface to the tango scada (and in future epics)
#   Copyright (C) <2014>  <Martin Mohan>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software Foundation,
#   Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA

#set -x
#source $(dirname $0)/regexf_unittest.sh

export PATH=.:$PATH
echo "Call: `which regexf`"

# no_match returns false=1, match returns true=0
configFile=/usr/local/bin/regexf.ini
assertEqual.sh "regexf aa/bb/cc" "$configFile:re.match<aa/bb/cc> no_match"
assertFalse.sh "regexf aa/bb/cc"
assertEqual.sh "regexf aa/bb/cc vac/bb/cc" "$configFile:re.match<aa/bb/cc> no_match"
assertGrep.sh "regexf vac/bb/cc -v" " match"
assertTrue.sh "regexf vac/bb/cc"
assertGrep.sh "regexf -i -f $configFile" "regexf_version"
# Even 1 no_match returns false
assertTrue.sh "regexf vac/vac1/1 vac/vac2/2" # matches return True
assertFalse.sh "regexf aa/bb/cc vac/vac1/1 vac/vac2/2" # 1 no_match return False
assertFalse.sh "regexf vac/vac1/1 aa/bb/cc vac/vac2/2" # 1 no_match return False

#configFile=regexf.ini
assertGrep.sh "regexf -f $configFile -s test1 -i" "test1"
assertGrep.sh "regexf -f $configFile -s test1 a/d/g -v" "match"
assertGrep.sh "regexf -f $configFile -s test1 d/d/g -v" " no_match"
assertGrep.sh "regexf -f $configFile -s ego_test V1:A_B/bb/cc -v" " match"
assertGrep.sh "regexf -f $configFile -s ego_test V2:A_B/bb/cc -v" " no_match"

test_file=/usr/local/bin/regexf_test.ini
assertEqual.sh "regexf -f $test_file aa/bb/cc" "$test_file:re.match<aa/bb/cc> no_match"
assertFalse.sh "regexf -f $test_file aa/bb/cc"
assertEqual.sh "regexf -f $test_file m/bb/cc" ""
assertGrep.sh "regexf -f $test_file -s ego -i" "A-Za-z"
assertGrep.sh "regexf -f $test_file -s ego aa/bb/cc" "$test_file:re.match<aa/bb/cc> no_match"
assertGrep.sh "regexf -f $test_file  a/bb/cc -v" " match"
assertGrep.sh "regexf -f $test_file  b/bb/cc -v" " no_match"
assertGrep.sh "regexf -f $test_file V1:A_B/bb/cc -v" " no_match"
assertGrep.sh "regexf -f $test_file -s ego V1:A_B/bb/cc -v" " match"
assertGrep.sh "regexf -f $test_file -s ego V2:A_B/bb/cc -v" " no_match"

