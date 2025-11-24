#!/bin/bash

DESTINATION=~/Library/Services

workflows=(
    "Capex_Opex.workflow"
    "Cluster.workflow"
    "Complexity_1.workflow"
    "Complexity_2.workflow"
    "Complexity_3.workflow"
    "Examples.workflow"
    "Expertise_Project_Process_Organization.workflow"
    "Expertise.workflow"
    "Generate Glossary.workflow"
    "Generate Image.workflow"
    "MindManager AI.workflow"
    "Process_Organization.workflow"
    "Project_Organization.workflow"
    "Project_Process_Organization.workflow"
    "Refine_Development.workflow"
    "Refine_General.workflow"
    "Translate_DE.workflow"
    "Translate_EN.workflow"
)

for dir in "${workflows[@]}"; do
    target="$DESTINATION/$dir"
    if [ -d "$target" ]; then
        echo "Deleting $target"
        rm -rf "$target"
    fi
done

echo "Delete completed."
