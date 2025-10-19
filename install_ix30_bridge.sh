#!/bin/bash

ARCHIVE_PATH="/tmp/packages/"
ARCHIVE_NAME="IX30_modbus_bridge".tar.gz
PYTHON_PACKAGE_PATH="/tmp/packages/pymodbus-3.11.1-py3-none-any.whl"

FINAL_PATH="/opt/custom/"


PYMODBUS_VERSION=$(pip show pymodbus | grep  "Version: 3.11.1" > /dev/null 2>&1; echo $?)

echo "Instalando IX30 Modbus Bridge..."
tar -xzf "$ARCHIVE_PATH/$ARCHIVE_NAME" -C /tmp/


if [ $? -ne 0 ]; then
    echo "❌ Error al descomprimir el archivo."
    exit 1
fi

if [ $PYMODBUS_VERSION -ne 0 ]; then
    pip install "$PYTHON_PACKAGE_PATH"
else 
    echo "🔹 pymodbus ya está instalado en la versión 3.11.1, omitiendo instalación."
fi

if [ $? -ne 0 ]; then
    echo "❌ Error al instalar el paquete pymodbus."
    exit 2
fi

if [ ! -d $FINAL_PATH ]; then
    mkdir -p $FINAL_PATH
    if [ $? -ne 0 ]; then
        echo "❌ Error al crear el directorio $FINAL_PATH."
        exit 3
    fi
fi


if [ -d /tmp/main/ ]; then
    rm -rf /tmp/main/
fi

mv /tmp/src/ /tmp/main/

if [ $? -ne 0 ]; then
    echo "❌ Error al renombrar el directorio descomprimido."
    exit 4
fi

if [ -d "$FINAL_PATH/main" ]; then
    rm -rf $FINAL_PATH/main
    if [ $? -ne 0 ]; then
        echo "❌ Error al eliminar el directorio existente $FINAL_PATH/main."
        exit 4
    fi
fi

mv /tmp/main/ $FINAL_PATH

if [ $? -ne 0 ]; then
    echo "❌ Error al mover los archivos a $FINAL_PATH."
    exit 4
fi

echo "✅ IX30 Modbus Bridge instalado correctamente en $FINAL_PATH."


echo "desea ejecutar el puente modbus ahora? (s/n)"
read RESPUESTA
if [[ "$RESPUESTA" == "s" || "$RESPUESTA" == "S" ]]; then
    echo "Iniciando IX30 Modbus Bridge..."
    OLD_PID=$(ps | grep "python3 /opt/custom/main/main.py" | grep -v grep | awk '{print $1}')

    for pid in $OLD_PID; do
        echo "Encontrada instancia en ejecución del puente modbus (PID: $pid)"
        if [ -n "$pid" ]; then
            echo "Deteniendo instancia anterior del puente modbus (PID: $pid)..."
            kill -9 "$pid"
            sleep 2
        fi

        if ps -p "$pid" > /dev/null 2>&1; then
            echo "⚠️  Forzando terminación del proceso..."
            kill -9 "$pid"
            sleep 2
        fi
    done

    python3 /opt/custom/main/main.py > /dev/null 2>&1 &

    if [ $? -ne 0 ]; then
        echo "❌ Error al iniciar el puente modbus."
        exit 5
    fi
    echo "✅ Puente modbus iniciado correctamente."
    ps | grep "python3 /opt/custom/main/main.py" | grep -v grep 
else
    echo "Puedes iniciar el puente modbus más tarde ejecutando:"
    echo "python3 /opt/custom/main/main.py &"
fi

exit 0
