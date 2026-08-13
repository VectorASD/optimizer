# pkg install openjdk-21 -y
# exit  # Переменная JAVA_HOME сама применится в новой интерактивной сессии

SCRIPT_DIR="$(dirname "$(realpath "$0")")"

JNI_INCLUDE="$(realpath "$SCRIPT_DIR/../../external/java-21-openjdk/include")"
JNI_LIB="$JAVA_HOME/lib/server/libjvm.so"

SRC="$SCRIPT_DIR/src/jni_server.c"
OUTPUT="$SCRIPT_DIR/jni_server.so"

clang -I"$JNI_INCLUDE" -o "$OUTPUT" "$SRC" "$JNI_LIB" -Wl,-rpath,"$(dirname "$JNI_LIB")"
err_code="$?"
echo "Compile code: $err_code"
if [ "$err_code" -eq 0 ]; then
    "$OUTPUT"
fi
