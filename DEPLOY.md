# Deployment Guide

## Render Deployment
1. Link your GitHub repository to Render.
2. Select "Blueprint" to use the `render.yaml` configuration.
3. Render will automatically deploy your main branch whenever you push.

## Android APK Signing
1. Generate an upload keystore file.
2. Build the unsigned APK via Capacitor `npx cap build android`.
3. Sign the APK using `apksigner`.

## Git LFS (Large File Storage)
We use Git LFS to push trained models (`.pkl`, `.pt`, etc.) and training data without bloating the repository.
- Ensure LFS is installed locally `git lfs install`.
- It will automatically track large binaries specified in `.gitattributes`.
