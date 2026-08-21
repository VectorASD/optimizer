#!/bin/bash
set -eu

SCRIPT_DIR="$(dirname "$(realpath "$0")")"

SRC="$SCRIPT_DIR/src"
INCLUDE="$SCRIPT_DIR/include"
OBJ="$SCRIPT_DIR/obj"
OUTPUT="$SCRIPT_DIR/jni_server.so"

JNI_INCLUDE="$(realpath "$SCRIPT_DIR/../../external/java-21-openjdk/include")"
JNI_LIB="$JAVA_HOME/lib/server/libjvm.so"
# pkg install openjdk-21 -y
# exit  # Переменная JAVA_HOME сама применится в новой интерактивной сессии
if [ -z "${JAVA_HOME:-}" ]; then
    echo "JAVA_HOME is not set." >&2
    echo "Please install openjdk-21:" >&2
    echo "    pkg install openjdk-21" >&2
    echo "Then exit this terminal session and start a new one to apply JAVA_HOME." >&2
    exit 1
fi

if command -v ccache >/dev/null 2>&1; then
    CC=("ccache" "clang")
else
    CC=("clang")
    echo "ccache is not installed. Compilation will proceed without it." >&2
    echo "To install: pkg install ccache" >&2
fi
CFLAGS=("-I$INCLUDE" "-I$JNI_INCLUDE" "-fPIC" "-MMD")

mkdir -p "$OBJ"

"${CC[@]}" "${CFLAGS[@]}" -MF "$OBJ/utils.d" -o "$OBJ/utils.o" -c "$SRC/utils.c"
"${CC[@]}" "${CFLAGS[@]}" -MF "$OBJ/jni_server.d" -o "$OBJ/jni_server.o" -c "$SRC/jni_server.c"

"${CC[@]}" -o "$OBJ/jni_server.so" "$OBJ/utils.o" "$OBJ/jni_server.o" \
    -L"$(dirname "$JNI_LIB")" -ljvm \
    -Wl,-rpath,"$(dirname "$JNI_LIB")"

strip "$OBJ/jni_server.so" -o "$OUTPUT"
"$OUTPUT"
