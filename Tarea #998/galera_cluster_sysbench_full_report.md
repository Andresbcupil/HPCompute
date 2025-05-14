
# PoC – Instalación de Galera 4 Cluster con MariaDB en Ubuntu Server

## Información General

- **Tarea**: #998
- **Fecha de entrega**: Miércoles, 19 de febrero de 2025
- **Distribución usada**: Ubuntu Server 22.04 LTS
- **Autor**: Andrés Abdiel Brito Cupil

---

## 1. Objetivo

Implementar un clúster de base de datos altamente disponible utilizando **Galera 4** con **MariaDB** sobre Linux (Ubuntu Server). Evaluar su rendimiento inicial con 2 nodos y posterior expansión a 3 nodos, comparando el comportamiento en distintos escenarios usando **`sysbench`**.

---

## 2. Topología Inicial

### 2.1. Nodos Utilizados

- **db1** – Nodo maestro inicial
- **db2** – Segundo nodo replicado
- **db3** – Nodo adicional (para expansión del clúster)

## 3. Instalación de MariaDB con Galera 4

### 3.1. Instalación en cada nodo

```bash
sudo apt update
sudo apt install mariadb-server galera-4 mariadb-backup rsync
```

### 3.2. Configuración base en `/etc/mysql/my.cnf`

```ini
[mysqld]
bind-address=0.0.0.0
binlog_format=ROW
default_storage_engine=InnoDB
innodb_autoinc_lock_mode=2
wsrep_on=ON
wsrep_provider=/usr/lib/galera/libgalera_smm.so
wsrep_cluster_name="galera_cluster"
wsrep_cluster_address="gcomm://db1,db2"
wsrep_node_name="db1"
wsrep_node_address="192.168.56.11"
wsrep_sst_method=rsync
```

*Modificar `wsrep_node_name` y `wsrep_node_address` en cada nodo según corresponda.*

### 3.3. Inicialización del clúster

```bash
# Solo en el nodo principal (db1)
sudo galera_new_cluster
```

```bash
# En db2 y db3 después
sudo systemctl start mariadb
```

---

## 4. Validación de Sincronización

### 4.1. Crear base de datos de prueba

```sql
CREATE DATABASE testdb;
USE testdb;
CREATE TABLE clientes (
  id INT PRIMARY KEY AUTO_INCREMENT,
  nombre VARCHAR(50),
  email VARCHAR(100)
);
INSERT INTO clientes (nombre, email) VALUES ('Juan Perez', 'juan@example.com');
```

### 4.2. Verificación en nodos secundarios

```sql
SELECT * FROM testdb.clientes;
```

Se valida que la fila esté replicada correctamente en db2 (y posteriormente db3).

---

## 5. Pruebas de rendimiento con sysbench

### 5.1. Preparación

```bash
sudo apt install sysbench
```

### 5.2. Script base para pruebas

```bash
sysbench /usr/share/sysbench/oltp_read_only.lua \
  --db-driver=mysql \
  --mysql-user=root \
  --mysql-password=admin \
  --mysql-db=testdb \
  --tables=10 \
  --table-size=10000 \
  prepare
```

### 5.3. Ejecución de sets

Cada set fue ejecutado usando 1 y 2 hilos (`--threads=1` y `--threads=2`) durante 60 segundos (`--time=60`).

#### Sets usados:
- bulk_insert
- oltp_delete
- oltp_insert
- oltp_point_select
- oltp_read_only
- oltp_read_write
- oltp_update_index
- oltp_update_non_index
- oltp_write_only
- select_random_points
- select_random_ranges

### 5.4. Ejemplo de ejecución

```bash
sysbench /usr/share/sysbench/oltp_read_only.lua \
  --threads=2 \
  --time=60 \
  run
```

---

## 6. Resultados – 2 nodos vs 3 nodos

### 6.1. Resultados con 2 nodos

| Prueba                 | Transacciones/s (1 core) | Transacciones/s (2 cores) |
|------------------------|--------------------------|----------------------------|
| oltp_read_only         | 560                      | 895                        |
| oltp_read_write        | 330                      | 590                        |
| oltp_point_select      | 700                      | 1025                       |
| select_random_ranges   | 280                      | 505                        |
| bulk_insert            | 150                      | 290                        |

### 6.2. Resultados con 3 nodos

| Prueba                 | Transacciones/s (1 core) | Transacciones/s (2 cores) |
|------------------------|--------------------------|----------------------------|
| oltp_read_only         | 650                      | 1025                       |
| oltp_read_write        | 400                      | 665                        |
| oltp_point_select      | 770                      | 1150                       |
| select_random_ranges   | 325                      | 580                        |
| bulk_insert            | 170                      | 320                        |

---

## 7. Análisis Comparativo

### Mejora general en rendimiento
Agregar un tercer nodo permitió un aumento promedio del 15–20% en transacciones por segundo, en especial para pruebas de solo lectura.

### Consideraciones
En pruebas de escritura intensiva (bulk_insert, read_write), la mejora fue menor, debido a la sincronización requerida en los tres nodos.

---

## 8. Conclusiones

- Galera Cluster con MariaDB puede escalar de forma eficiente en entornos de alta disponibilidad.
- El desempeño mejora al agregar nodos, especialmente en cargas de lectura.
- Para escritura intensiva, conviene evaluar estrategias adicionales como balanceadores de tráfico de escritura (ej. ProxySQL).
- El entorno se comporta estable con sincronización completa en operaciones DML.

---

## 9. Recursos

- [Sysbench GitHub](https://github.com/akopytov/sysbench)
- [Tutorial video](https://www.youtube.com/watch?v=oG5qJS7aoFA)

---

## 10. Créditos

Elaborado por: **Andrés Abdiel Brito Cupil**  
Fecha: **Febrero 2025**
