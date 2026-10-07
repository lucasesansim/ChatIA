#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
python -m PyInstaller --noconfirm --clean --windowed --onedir --name ChatIA --paths src launcher.py
arch="$(dpkg --print-architecture)"
stage="$(mktemp -d)"
trap 'rm -rf -- "$stage"' EXIT
mkdir -p "$stage/DEBIAN" "$stage/opt/chatia" "$stage/usr/share/applications" "$stage/usr/share/doc/chatia"
cp -a dist/ChatIA/. "$stage/opt/chatia/"
cp LICENSE "$stage/usr/share/doc/chatia/copyright"
cat > "$stage/DEBIAN/control" <<EOF
Package: chatia
Version: 0.1.0
Section: utils
Priority: optional
Architecture: $arch
Maintainer: ChatIA contributors
Depends: libc6, libx11-6, libxext6, libxrender1, libfontconfig1, libfreetype6, libxft2
Description: Asistente de escritorio para WhatsApp Cloud API
 Generacion de borradores y transcripcion de audio con revision humana.
EOF
cat > "$stage/usr/share/applications/chatia.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=ChatIA
Comment=Respuestas y transcripciones con revision
Exec=/opt/chatia/ChatIA
Terminal=false
Categories=Utility;Network;
EOF
chmod 755 "$stage/opt/chatia/ChatIA"
dpkg-deb --root-owner-group --build "$stage" "dist/chatia_0.1.0_${arch}.deb"
