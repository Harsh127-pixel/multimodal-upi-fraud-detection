#!/bin/bash
git status
git add .
git commit -m "chore: add GitHub collaboration setup — CODEOWNERS, CI, issue templates"
git branch -M main
git push -u origin main
git checkout -b develop
git push -u origin develop
git checkout develop
