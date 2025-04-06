#!/bin/bash

# Navigate to the project directory
cd "$(dirname "$0")"

# Function to replace navy with slate for a specific pattern
replace_navy_slate() {
  pattern=$1
  find templates -name "*.html" -exec sed -i '' "s/$pattern-navy-\([0-9]\+\)/$pattern-slate-\1/g" {} \;
  echo "Replaced $pattern-navy-* with $pattern-slate-*"
}

# List of patterns to replace
patterns=(
  "text"
  "bg"
  "border"
  "focus:ring"
  "focus-visible:outline"
  "focus:ring-offset"
  "hover:bg"
  "hover:text"
  "ring"
  "group-hover:text"
)

# Replace each pattern
for pattern in "${patterns[@]}"; do
  replace_navy_slate "$pattern"
done

echo "Replacements complete!"