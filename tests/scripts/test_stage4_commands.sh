#!/bin/sh
# Stage 4: the startup script with ls, cd, wc, echo (ends with an error).
. "$(dirname "$0")/lib.sh"

run_emu 'exit\n' --no-gui --vfs "$VFS/deep.xml" \
    --script "$STARTUP/stage4_commands.emu"
expect_status 1
expect_output "Hello, emulator!"
expect_output "- 18 notes.txt"
expect_output "/bin:"
expect_output ".hidden"
expect_output ":/home/user/docs/drafts$ ls -l"
expect_output " 1  3 18 readme.txt"
expect_output "cd: nosuch: No such file or directory"
expect_output "line 30 failed with status 1, script stopped"
expect_no_output "never printed"
finish
