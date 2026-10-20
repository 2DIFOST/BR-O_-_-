#!/bin/sh
# Stage 5: error handling of rm and cp, and that the XML stays intact.
. "$(dirname "$0")/lib.sh"

BEFORE=$(cksum < "$VFS/deep.xml")
run_emu 'rm\nrm nosuch\nrm bin\nrm -r /\nrm .\nrm -x a\ncp\ncp a\n\
cp nosuch x\ncp readme.txt nosuch/x\ncp -r home home/user\n\
cp readme.txt readme.txt\ncp -r home readme.txt\ncp readme.txt bin/tool.bin x\n\
rm -r home\nls\nexit\n' --no-gui --vfs "$VFS/deep.xml"
expect_status 0
expect_output "rm: missing operand"
expect_output "rm: cannot remove 'nosuch': No such file or directory"
expect_output "rm: cannot remove 'bin': Is a directory"
expect_output "rm: it is dangerous to operate recursively on '/'"
expect_output "rm: refusing to remove '.' or '..' directory: skipping '.'"
expect_output "rm: invalid option -- 'x'"
expect_output "cp: missing file operand"
expect_output "cp: missing destination file operand after 'a'"
expect_output "cp: cannot stat 'nosuch': No such file or directory"
expect_output "cp: cannot create regular file 'nosuch/x': No such file or directory"
expect_output "cp: cannot copy a directory, 'home', into itself, 'home/user/home'"
expect_output "cp: 'readme.txt' and 'readme.txt' are the same file"
expect_output "cp: cannot overwrite non-directory 'readme.txt' with directory 'home'"
expect_output "cp: target 'x' is not a directory"
[ "$BEFORE" = "$(cksum < "$VFS/deep.xml")" ] \
    && pass "the XML file is not changed" || fail "the XML file was changed"
finish
