#!/bin/sh
# Stage 4: error handling of ls, cd, wc, echo in interactive mode.
. "$(dirname "$0")/lib.sh"

run_emu 'ls nosuch\nls -x\ncd a b\ncd readme.txt\nwc\nwc /\n\
wc nosuch\nwc -z readme.txt\nexit\n' --no-gui --vfs "$VFS/deep.xml"
expect_status 0
expect_output "ls: cannot access 'nosuch': No such file or directory"
expect_output "ls: invalid option -- 'x'"
expect_output "cd: too many arguments"
expect_output "cd: readme.txt: Not a directory"
expect_output "wc: missing file operand"
expect_output "wc: /: Is a directory"
expect_output "wc: nosuch: No such file or directory"
expect_output "wc: invalid option -- 'z'"
finish
