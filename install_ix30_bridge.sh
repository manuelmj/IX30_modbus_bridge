#!/bin/bash

# ================================
# CONFIGURACIÓN - VARIABLES DE RUTAS
# ================================

# Rutas de archivos y directorios
ARCHIVE_PATH="/tmp/packages/"
ARCHIVE_NAME="IX30_modbus_bridge.tar.gz"
PYTHON_PACKAGE_PATH="/tmp/packages/pymodbus-3.11.1-py3-none-any.whl"
FINAL_PATH="/etc/config/scripts/"
APP_NAME="IX30 Modbus Bridge"

# Rutas temporales
TEMP_EXTRACT_PATH="/tmp/"
TEMP_SRC_DIR="/tmp/src/"
TEMP_MAIN_DIR="/tmp/main/"

# Rutas de la aplicación
APP_INSTALL_PATH="${FINAL_PATH}main/"
APP_MAIN_SCRIPT="${APP_INSTALL_PATH}main.py"
APP_EXECUTABLE="python3 ${APP_MAIN_SCRIPT}"

# Comandos de sistema
PYTHON_CMD="python3"
PIP_CMD="pip"
PS_CMD="ps"
GREP_CMD="grep"
AWK_CMD="awk"
KILL_CMD="kill"

# ================================
# LÓGICA DE INSTALACIÓN
# ================================

PYMODBUS_VERSION=$(${PIP_CMD} show pymodbus | ${GREP_CMD} "Version: 3.11.1" > /dev/null 2>&1; echo $?)

echo "Instalando ${APP_NAME}..."
tar -xzf "${ARCHIVE_PATH}${ARCHIVE_NAME}" -C ${TEMP_EXTRACT_PATH}

if [ $? -ne 0 ]; then
    echo "❌ Error al descomprimir el archivo."
    exit 1
fi

if [ $PYMODBUS_VERSION -ne 0 ]; then
    ${PIP_CMD} install "${PYTHON_PACKAGE_PATH}"
else 
    echo "🔹 pymodbus ya está instalado en la versión 3.11.1, omitiendo instalación."
fi

if [ $? -ne 0 ]; then
    echo "❌ Error al instalar el paquete pymodbus."
    exit 2
fi

if [ ! -d ${FINAL_PATH} ]; then
    mkdir -p ${FINAL_PATH}
    if [ $? -ne 0 ]; then
        echo "❌ Error al crear el directorio ${FINAL_PATH}."
        exit 3
    fi
fi

if [ -d ${TEMP_MAIN_DIR} ]; then
    rm -rf ${TEMP_MAIN_DIR}
fi

mv ${TEMP_SRC_DIR} ${TEMP_MAIN_DIR}

if [ $? -ne 0 ]; then
    echo "❌ Error al renombrar el directorio descomprimido."
    exit 4
fi

if [ -d "${APP_INSTALL_PATH}" ]; then
    rm -rf ${APP_INSTALL_PATH}
    if [ $? -ne 0 ]; then
        echo "❌ Error al eliminar el directorio existente ${APP_INSTALL_PATH}."
        exit 4
    fi
fi

mv ${TEMP_MAIN_DIR} ${FINAL_PATH}

if [ $? -ne 0 ]; then
    echo "❌ Error al mover los archivos a ${FINAL_PATH}."
    exit 4
fi

echo "✅ ${APP_NAME} instalado correctamente en ${FINAL_PATH}."

# ================================
# EJECUCIÓN DE LA APLICACIÓN
# ================================

echo "¿Desea ejecutar el puente modbus ahora? (s/n)"
read RESPUESTA

if [[ "${RESPUESTA}" == "s" || "${RESPUESTA}" == "S" ]]; then
    echo "Iniciando ${APP_NAME}..."
    
    # Buscar procesos existentes
    OLD_PID=$(${PS_CMD} | ${GREP_CMD} "${APP_EXECUTABLE}" | ${GREP_CMD} -v ${GREP_CMD} | ${AWK_CMD} '{print $1}')

    for pid in ${OLD_PID}; do
        echo "Encontrada instancia en ejecución del puente modbus (PID: ${pid})"
        if [ -n "${pid}" ]; then
            echo "Deteniendo instancia anterior del puente modbus (PID: ${pid})..."
            ${KILL_CMD} -9 "${pid}"
            sleep 2
        fi

        if ${PS_CMD} -p "${pid}" > /dev/null 2>&1; then
            echo "⚠️  Forzando terminación del proceso..."
            ${KILL_CMD} -9 "${pid}"
            sleep 2
        fi
    done

    # Ejecutar nueva instancia
    ${APP_EXECUTABLE} > /dev/null 2>&1 &

    if [ $? -ne 0 ]; then
        echo "❌ Error al iniciar el puente modbus."
        exit 5
    fi
    
    echo "✅ Puente modbus iniciado correctamente."
    ${PS_CMD} | ${GREP_CMD} "${APP_EXECUTABLE}" | ${GREP_CMD} -v ${GREP_CMD}
else
    echo "Puedes iniciar el puente modbus más tarde ejecutando:"
    echo "${APP_EXECUTABLE} &"
fi

exit 0