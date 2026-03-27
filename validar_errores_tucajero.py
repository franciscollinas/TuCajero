#!/usr/bin/env python3
"""
Script de Validación - TuCajero POS
Valida los 12 puntos críticos identificados

Uso: python validar_errores_tucajero.py
"""

import os
import sys
from pathlib import Path
import re

# Colores para output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}\n")

def print_pass(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")

def print_fail(text):
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.RESET}")

# ============================================================================
# VALIDACIONES
# ============================================================================

def validar_1_inventario_view():
    """1. Verificar que inventario_view.py esté eliminado"""
    print_header("1. VALIDAR: inventario_view.py eliminado")
    
    archivo = Path("tucajero/ui/inventario_view.py")
    
    if archivo.exists():
        print_fail(f"El archivo {archivo} TODAVÍA EXISTE")
        print_info("Debe eliminarse y remover todas las referencias")
        return False
    else:
        print_pass(f"Archivo {archivo} no existe")
    
    # Buscar referencias
    archivos_py = list(Path("tucajero").rglob("*.py"))
    referencias = []
    
    for archivo_py in archivos_py:
        try:
            with open(archivo_py, 'r', encoding='utf-8') as f:
                contenido = f.read()
                if 'inventario_view' in contenido or 'InventarioView' in contenido:
                    referencias.append(archivo_py)
        except:
            pass
    
    if referencias:
        print_fail(f"Se encontraron {len(referencias)} archivos con referencias:")
        for ref in referencias:
            print(f"   - {ref}")
        return False
    else:
        print_pass("No se encontraron referencias a inventario_view")
    
    return True


def validar_2_relacion_producto():
    """2. Validar relación recursiva de Producto"""
    print_header("2. VALIDAR: Relación recursiva Producto")
    
    archivo = Path("tucajero/models/producto.py")
    
    if not archivo.exists():
        print_fail(f"No se encuentra {archivo}")
        return False
    
    with open(archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Buscar remote_side
    if 'remote_side' not in contenido:
        print_fail("Falta 'remote_side' en la relación producto_fraccion")
        print_info("Debe agregarse: remote_side='Producto.id'")
        return False
    else:
        print_pass("Encontrado 'remote_side' en relación")
    
    # Buscar ondelete
    if 'ondelete' not in contenido:
        print_warning("Falta 'ondelete' en ForeignKey de producto_fraccion_id")
        print_info("Recomendado: ondelete='SET NULL'")
    else:
        print_pass("Encontrado 'ondelete' en ForeignKey")
    
    # Buscar validación de ciclos
    archivo_service = Path("tucajero/services/producto_service.py")
    if archivo_service.exists():
        with open(archivo_service, 'r', encoding='utf-8') as f:
            service_contenido = f.read()
        
        if 'validar_producto_fraccion' in service_contenido:
            print_pass("Encontrada validación de ciclos en ProductoService")
        else:
            print_warning("No se encuentra método 'validar_producto_fraccion'")
            print_info("Debe agregarse para evitar ciclos")
    
    return True


def validar_3_indices_db():
    """3. Validar índices de base de datos"""
    print_header("3. VALIDAR: Índices de base de datos")
    
    archivo = Path("tucajero/config/database.py")
    
    if not archivo.exists():
        print_fail(f"No se encuentra {archivo}")
        return False
    
    with open(archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    if 'crear_indices' not in contenido:
        print_fail("No se encuentra función 'crear_indices()'")
        print_info("Debe agregarse para crear índices de optimización")
        return False
    else:
        print_pass("Encontrada función 'crear_indices()'")
    
    # Verificar que se llame desde init_db
    if 'crear_indices()' in contenido and 'def init_db' in contenido:
        print_pass("crear_indices() se llama desde init_db()")
    else:
        print_warning("crear_indices() podría no estar siendo llamada")
    
    # Contar índices esperados
    indices_esperados = [
        'idx_productos_codigo',
        'idx_productos_activo',
        'idx_ventas_fecha',
        'idx_ventas_anulada',
        'idx_clientes_nombre'
    ]
    
    indices_encontrados = sum(1 for idx in indices_esperados if idx in contenido)
    print_info(f"Índices encontrados: {indices_encontrados}/{len(indices_esperados)}")
    
    return True


def validar_4_stock_negativo():
    """4. Validar que stock negativo esté bloqueado"""
    print_header("4. VALIDAR: Stock negativo bloqueado")
    
    archivo_repo = Path("tucajero/repositories/producto_repo.py")
    archivo_venta = Path("tucajero/repositories/venta_repo.py")
    
    validaciones = 0
    
    # Validar en producto_repo
    if archivo_repo.exists():
        with open(archivo_repo, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        if 'stock' in contenido and 'ValueError' in contenido and 'negativo' in contenido:
            print_pass("Validación de stock negativo en producto_repo.py")
            validaciones += 1
        else:
            print_fail("Falta validación de stock negativo en update()")
    else:
        print_fail(f"No se encuentra {archivo_repo}")
    
    # Validar en venta_repo
    if archivo_venta.exists():
        with open(archivo_venta, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        if 'stock' in contenido and ('insuficiente' in contenido or 'ValueError' in contenido):
            print_pass("Validación de stock en venta_repo.py")
            validaciones += 1
        else:
            print_fail("Falta validación antes de registrar venta")
    else:
        print_fail(f"No se encuentra {archivo_venta}")
    
    return validaciones >= 1


def validar_5_fecha_vencimiento():
    """5. Validar fecha de vencimiento"""
    print_header("5. VALIDAR: Fecha de vencimiento")
    
    archivo = Path("tucajero/ui/productos_view.py")
    
    if not archivo.exists():
        print_fail(f"No se encuentra {archivo}")
        return False
    
    with open(archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    validaciones = 0
    
    # Validar setMinimumDate
    if 'setMinimumDate' in contenido and 'QDate.currentDate()' in contenido:
        print_pass("setMinimumDate configurado en QDateEdit")
        validaciones += 1
    else:
        print_fail("Falta setMinimumDate en fecha_vencimiento")
    
    # Validar en servicio
    archivo_service = Path("tucajero/services/producto_service.py")
    if archivo_service.exists():
        with open(archivo_service, 'r', encoding='utf-8') as f:
            service_contenido = f.read()
        
        if 'fecha_vencimiento' in service_contenido and 'ValueError' in service_contenido:
            print_pass("Validación de fecha en ProductoService")
            validaciones += 1
        else:
            print_warning("Falta validación de fecha en servicio")
    
    return validaciones >= 1


def validar_6_persistencia_carrito():
    """6. Validar persistencia de carrito"""
    print_header("6. VALIDAR: Persistencia de carrito")
    
    archivo = Path("tucajero/ui/ventas_view.py")
    
    if not archivo.exists():
        print_fail(f"No se encuentra {archivo}")
        return False
    
    with open(archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    metodos_esperados = [
        'guardar_carrito_temporal',
        'cargar_carrito_guardado',
        'limpiar_carrito_temporal'
    ]
    
    encontrados = 0
    for metodo in metodos_esperados:
        if metodo in contenido:
            print_pass(f"Encontrado método: {metodo}()")
            encontrados += 1
        else:
            print_fail(f"Falta método: {metodo}()")
    
    # Validar import json
    if 'import json' in contenido:
        print_pass("Import json presente")
    else:
        print_warning("Falta import json")
    
    return encontrados >= 2


def validar_7_limites_descuentos():
    """7. Validar límites en descuentos"""
    print_header("7. VALIDAR: Límites de descuentos")
    
    archivo = Path("tucajero/ui/descuento_dialog.py")
    
    if not archivo.exists():
        print_fail(f"No se encuentra {archivo}")
        return False
    
    with open(archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    validaciones = 0
    
    # Validar parámetro es_admin
    if 'es_admin' in contenido:
        print_pass("Parámetro 'es_admin' presente en __init__")
        validaciones += 1
    else:
        print_fail("Falta parámetro 'es_admin' en __init__")
    
    # Validar max_descuento
    if 'max_descuento' in contenido:
        print_pass("Variable 'max_descuento' presente")
        validaciones += 1
    else:
        print_fail("Falta variable 'max_descuento'")
    
    # Validar método de validación
    if 'validar_descuento' in contenido:
        print_pass("Método 'validar_descuento()' encontrado")
        validaciones += 1
    else:
        print_warning("Falta método 'validar_descuento()'")
    
    return validaciones >= 2


def validar_8_comprobante_pagos():
    """8. Validar comprobante en pagos electrónicos"""
    print_header("8. VALIDAR: Comprobante en pagos electrónicos")
    
    # Validar campo en modelo
    archivo_modelo = Path("tucajero/models/producto.py")
    if archivo_modelo.exists():
        with open(archivo_modelo, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        if 'comprobante' in contenido and 'class Venta' in contenido:
            print_pass("Campo 'comprobante' agregado al modelo Venta")
        else:
            print_fail("Falta campo 'comprobante' en modelo Venta")
            return False
    
    # Validar solicitud en UI
    archivo_ui = Path("tucajero/ui/ventas_view.py")
    if archivo_ui.exists():
        with open(archivo_ui, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        if 'Transferencia' in contenido and 'QInputDialog' in contenido and 'comprobante' in contenido:
            print_pass("Solicitud de comprobante en confirmar_pago()")
        else:
            print_fail("Falta solicitud de comprobante para pagos electrónicos")
            return False
    
    return True


def validar_9_diferencias_corte():
    """9. Validar diferencias en corte de caja"""
    print_header("9. VALIDAR: Diferencias en corte de caja")
    
    archivo = Path("tucajero/ui/corte_view.py")
    
    if not archivo.exists():
        print_fail(f"No se encuentra {archivo}")
        return False
    
    with open(archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    validaciones = 0
    
    # Buscar cálculo de diferencia
    if 'diferencia' in contenido and 'efectivo_esperado' in contenido:
        print_pass("Cálculo de diferencia presente")
        validaciones += 1
    else:
        print_fail("Falta cálculo de diferencia")
    
    # Buscar tolerancia
    if 'tolerancia' in contenido or 'TOLERANCIA' in contenido:
        print_pass("Tolerancia definida")
        validaciones += 1
    else:
        print_warning("Falta definición de tolerancia")
    
    # Buscar alerta
    if 'FALTANTE' in contenido or 'SOBRANTE' in contenido:
        print_pass("Alertas de FALTANTE/SOBRANTE presentes")
        validaciones += 1
    else:
        print_fail("Faltan alertas de diferencias")
    
    return validaciones >= 2


def validar_10_busqueda_parcial():
    """10. Validar búsqueda parcial de productos"""
    print_header("10. VALIDAR: Búsqueda parcial de productos")
    
    archivo = Path("tucajero/ui/ventas_view.py")
    
    if not archivo.exists():
        print_fail(f"No se encuentra {archivo}")
        return False
    
    with open(archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    validaciones = 0
    
    # Buscar ilike
    if 'ilike' in contenido:
        print_pass("Búsqueda con 'ilike' implementada")
        validaciones += 1
    else:
        print_fail("Falta búsqueda parcial con 'ilike'")
    
    # Buscar nombre en búsqueda
    if 'Producto.nombre' in contenido and 'buscar' in contenido:
        print_pass("Búsqueda por nombre presente")
        validaciones += 1
    else:
        print_warning("Podría faltar búsqueda por nombre")
    
    return validaciones >= 1


def validar_11_auto_refresh():
    """11. Validar auto-refresh en dashboard"""
    print_header("11. VALIDAR: Auto-refresh en dashboard")
    
    archivo = Path("tucajero/ui/dashboard_view.py")
    
    if not archivo.exists():
        print_fail(f"No se encuentra {archivo}")
        return False
    
    with open(archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    validaciones = 0
    
    # Buscar QTimer
    if 'QTimer' in contenido:
        print_pass("QTimer importado")
        validaciones += 1
    else:
        print_fail("Falta import de QTimer")
    
    # Buscar refresh_timer
    if 'refresh_timer' in contenido:
        print_pass("Timer de refresh creado")
        validaciones += 1
    else:
        print_fail("Falta crear refresh_timer")
    
    # Buscar showEvent
    if 'showEvent' in contenido:
        print_pass("Método showEvent() implementado")
        validaciones += 1
    else:
        print_warning("Falta método showEvent()")
    
    return validaciones >= 2


def validar_12_consecutivo_facturas():
    """12. Validar consecutivo de facturas"""
    print_header("12. VALIDAR: Consecutivo de facturas")
    
    # Validar modelo
    archivo_modelo = Path("tucajero/models/producto.py")
    tiene_modelo = False
    tiene_campo = False
    
    if archivo_modelo.exists():
        with open(archivo_modelo, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        if 'ConsecutivoFactura' in contenido:
            print_pass("Modelo ConsecutivoFactura creado")
            tiene_modelo = True
        else:
            print_fail("Falta modelo ConsecutivoFactura")
        
        if 'numero_factura' in contenido and 'class Venta' in contenido:
            print_pass("Campo 'numero_factura' en Venta")
            tiene_campo = True
        else:
            print_fail("Falta campo 'numero_factura' en Venta")
    
    # Validar método en repositorio
    archivo_repo = Path("tucajero/repositories/venta_repo.py")
    tiene_metodo = False
    
    if archivo_repo.exists():
        with open(archivo_repo, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        if 'obtener_siguiente_consecutivo' in contenido:
            print_pass("Método obtener_siguiente_consecutivo() presente")
            tiene_metodo = True
        else:
            print_fail("Falta método obtener_siguiente_consecutivo()")
    
    return tiene_modelo and tiene_campo and tiene_metodo


# ============================================================================
# MAIN
# ============================================================================

def main():
    print(f"\n{Colors.BOLD}{Colors.CYAN}")
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║          VALIDACIÓN DE CORRECCIONES - TuCajero POS               ║")
    print("║                    12 Puntos Críticos                             ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}")
    
    # Verificar que estamos en el directorio correcto
    if not Path("tucajero").exists():
        print_fail("No se encuentra el directorio 'tucajero'")
        print_info("Ejecuta este script desde la raíz del proyecto TuCajeroPOS")
        sys.exit(1)
    
    resultados = []
    
    # Ejecutar validaciones
    validaciones = [
        ("1. Inventario View eliminado", validar_1_inventario_view),
        ("2. Relación recursiva Producto", validar_2_relacion_producto),
        ("3. Índices de base de datos", validar_3_indices_db),
        ("4. Stock negativo bloqueado", validar_4_stock_negativo),
        ("5. Fecha de vencimiento", validar_5_fecha_vencimiento),
        ("6. Persistencia de carrito", validar_6_persistencia_carrito),
        ("7. Límites de descuentos", validar_7_limites_descuentos),
        ("8. Comprobante pagos", validar_8_comprobante_pagos),
        ("9. Diferencias corte caja", validar_9_diferencias_corte),
        ("10. Búsqueda parcial", validar_10_busqueda_parcial),
        ("11. Auto-refresh dashboard", validar_11_auto_refresh),
        ("12. Consecutivo facturas", validar_12_consecutivo_facturas),
    ]
    
    for nombre, validacion in validaciones:
        try:
            resultado = validacion()
            resultados.append((nombre, resultado))
        except Exception as e:
            print_fail(f"Error ejecutando validación: {e}")
            resultados.append((nombre, False))
    
    # Resumen final
    print_header("RESUMEN DE VALIDACIÓN")
    
    total = len(resultados)
    aprobados = sum(1 for _, r in resultados if r)
    fallados = total - aprobados
    
    print(f"\n{Colors.BOLD}Total de validaciones: {total}{Colors.RESET}")
    print(f"{Colors.GREEN}✅ Aprobadas: {aprobados}{Colors.RESET}")
    print(f"{Colors.RED}❌ Falladas: {fallados}{Colors.RESET}")
    
    porcentaje = (aprobados / total * 100) if total > 0 else 0
    
    print(f"\n{Colors.BOLD}Progreso: {porcentaje:.1f}%{Colors.RESET}")
    
    # Barra de progreso
    barra_width = 50
    barra_llena = int(barra_width * aprobados / total)
    barra_vacia = barra_width - barra_llena
    
    barra = f"{Colors.GREEN}{'█' * barra_llena}{Colors.RED}{'░' * barra_vacia}{Colors.RESET}"
    print(f"[{barra}]")
    
    # Estado por categoría
    print(f"\n{Colors.BOLD}Detalle por corrección:{Colors.RESET}\n")
    
    for nombre, resultado in resultados:
        icono = f"{Colors.GREEN}✅{Colors.RESET}" if resultado else f"{Colors.RED}❌{Colors.RESET}"
        print(f"{icono} {nombre}")
    
    # Prioridades pendientes
    print(f"\n{Colors.BOLD}Prioridades:{Colors.RESET}\n")
    
    criticas = resultados[0:3]
    altas = resultados[3:9]
    bajas = resultados[9:12]
    
    criticas_ok = sum(1 for _, r in criticas if r)
    altas_ok = sum(1 for _, r in altas if r)
    bajas_ok = sum(1 for _, r in bajas if r)
    
    print(f"🔴 Críticas:  {criticas_ok}/3")
    print(f"🟡 Altas:     {altas_ok}/6")
    print(f"🔵 Bajas:     {bajas_ok}/3")
    
    # Recomendación
    print(f"\n{Colors.BOLD}Recomendación:{Colors.RESET}")
    
    if criticas_ok < 3:
        print(f"{Colors.RED}⚠️  Completar correcciones CRÍTICAS primero{Colors.RESET}")
    elif altas_ok < 6:
        print(f"{Colors.YELLOW}⚠️  Continuar con correcciones de PRIORIDAD ALTA{Colors.RESET}")
    elif bajas_ok < 3:
        print(f"{Colors.BLUE}ℹ️  Implementar mejoras de UX restantes{Colors.RESET}")
    else:
        print(f"{Colors.GREEN}✨ ¡Todas las correcciones implementadas!{Colors.RESET}")
    
    print("\n")
    
    return 0 if aprobados == total else 1


if __name__ == "__main__":
    sys.exit(main())
