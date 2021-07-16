#!/bin/sh
#
# A git commit hook to validate the YAML files when committing and
# will fail the commit if it doesn't parse correctly.
#
# To enable this hook, run `ls -s ../../pre-commit.sh .git/hooks/pre-commit`.

# Redirect output to stderr.
exec 1>&2

# run yamllint on all yaml files in the repo
changedyamlfiles=`git diff --diff-filter=ACMR --staged --name-only | egrep '\.yamllint$|\.yml$|\.yaml$'`
if [ -n "$changedyamlfiles" ]; then
  while IFS= read -r filename; do
    yamllint --no-warnings --config-file=.yamllint $filename
  done <<< "$changedyamlfiles"
fi
