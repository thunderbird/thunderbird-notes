#!/bin/bash
#
# A git commit hook to validate the YAML files when committing and
# will fail the commit if it doesn't parse correctly.
#
# To enable this hook, run `ln -s ../../.githooks/pre-commit.sh .git/hooks/pre-commit`.

# Redirect output to stderr.
exec 1>&2

# run yamllint on all yaml files in the repo
declare -a changedyamlfiles=($(git diff --diff-filter=ACMR --staged --name-only | grep -E '\.yamllint$|\.yml$|\.yaml$'))
if [ -n "${changedyamlfiles[*]}" ]; then
  for filename in "${changedyamlfiles[@]}"; do
    yamllint --no-warnings --config-file=.yamllint "$filename"
  done
fi
