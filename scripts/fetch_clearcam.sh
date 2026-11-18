#!/usr/bin/env sh
# Download unmodified upstream ClearCam, independently of GARDA proprietary code.
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
TARGET="$ROOT/vendor/clearcam"
if [ -e "$TARGET" ]; then echo "Refusing to overwrite $TARGET" >&2; exit 1; fi
mkdir -p "$ROOT/vendor"
git clone https://github.com/roryclear/clearcam.git "$TARGET"
(cd "$TARGET" && git checkout --detach 553be39ba6f20ce055a7418ed54636b32059b4ad)
echo 'ClearCam cloned under GPL-3.0. Review upstream requirements.'
