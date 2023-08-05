# !/bin/sh

# This script regenerates the .diff files in this directory.  It's these files
# that are kept under vesion control instead of the scripts themselves.

for f in [a-zA-Z]*.py; do
    # We use custom labels to suppress the time stamps which are unnecessary
    # here and would only lead to noise in version control.
    grep -v '#HIDDEN' ../tutorial/$f |
    diff -u --label original --label modified - $f >$f.diff_
    if cmp $f.diff_ $f.diff >/dev/null 2>&1; then
        rm $f.diff_
    else
        mv $f.diff_ $f.diff
    fi
done
