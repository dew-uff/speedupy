#!/usr/bin/env bash

DBS_DIR="/app/dbs"

start_redis() {
  if [ -f "$DBS_DIR/redis.pid" ] && kill -0 $(cat "$DBS_DIR/redis.pid") 2>/dev/null; then
    echo "Redis is already running (PID $(cat "$DBS_DIR/redis.pid"))."
    return 0
  fi

  echo "Starting Redis with dir: $DBS_DIR/redis"
  conda activate dev_env
  redis-server --dir "$DBS_DIR/redis" &> "$DBS_DIR/redis.log" &
  echo $! > "$DBS_DIR/redis.pid"
  conda deactivate
}

start_mongo() {
  if [ -f "$DBS_DIR/mongo.pid" ] && kill -0 $(cat "$DBS_DIR/mongo.pid") 2>/dev/null; then
    echo "MongoDB is already running (PID $(cat "$DBS_DIR/mongo.pid"))."
    return 0
  fi

  echo "Starting MongoDB with dbpath: $DBS_DIR/mongo"
  conda activate dev_env
  mongod --dbpath "$DBS_DIR/mongo" > "$DBS_DIR/mongo.log" 2>&1 &
  echo $! > "$DBS_DIR/mongo.pid"
  conda deactivate
}

start_mysql() {
  if [ -f "$DBS_DIR/mysql.pid" ] && kill -0 $(cat "$DBS_DIR/mysql.pid") 2>/dev/null; then
    echo "MySQL is already running (PID $(cat "$DBS_DIR/mysql.pid"))."
    return 0
  fi

  echo "Starting MySQL with datadir: $DBS_DIR/mysql"
  conda activate dev_env
  if [ ! -d "$DBS_DIR/mysql" ] || [ -z "$(ls -A "$DBS_DIR/mysql")" ]; then
    echo "Initializing MySQL data directory..."
    mysqld --no-defaults --initialize-insecure --user=root --datadir="$DBS_DIR/mysql"
  fi
  mysqld --no-defaults --user=root --datadir="$DBS_DIR/mysql" --max_allowed_packet=512M &> "$DBS_DIR/mysql.log" &
  echo $! > "$DBS_DIR/mysql.pid"
  conda deactivate
}

start_memcached() {
  if [ -f "$DBS_DIR/memcached.pid" ] && kill -0 $(cat "$DBS_DIR/memcached.pid") 2>/dev/null; then
    echo "Memcached is already running (PID $(cat "$DBS_DIR/memcached.pid"))."
    return 0
  fi

  echo "Starting Memcached..."
  conda activate dev_env
  memcached -u root -m 4096 -I 512m &> "$DBS_DIR/memcached.log" &
  echo $! > "$DBS_DIR/memcached.pid"
  conda deactivate
}

stop_redis(){
  if [ -f "$DBS_DIR/redis.pid" ]; then
    echo "Stopping Redis..."
    kill $(cat "$DBS_DIR/redis.pid") && rm "$DBS_DIR/redis.pid"
  else
    echo "Redis PID file not found."
  fi
}

stop_mongo() {
  if [ -f "$DBS_DIR/mongo.pid" ]; then
    echo "Stopping MongoDB..."
    kill $(cat "$DBS_DIR/mongo.pid") && rm "$DBS_DIR/mongo.pid"
  else
    echo "MongoDB PID file not found."
  fi
}

stop_mysql() {
  if [ -f "$DBS_DIR/mysql.pid" ]; then
    echo "Stopping MySQL..."
    kill $(cat "$DBS_DIR/mysql.pid") && rm "$DBS_DIR/mysql.pid"
  else
    echo "MySQL PID file not found."
  fi
}

stop_memcached(){
  if [ -f "$DBS_DIR/memcached.pid" ]; then
    echo "Stopping Memcached..."
    kill $(cat "$DBS_DIR/memcached.pid") && rm "$DBS_DIR/memcached.pid"
  else
    echo "Memcached PID file not found."
  fi
}

print_help() {
  cat <<EOF
Usage: $0 {start|stop|help} {redis|mongo|mysql|memcached|all}

Commands:
  start redis     Start Redis server
  start mongo     Start MongoDB server
  start mysql     Start MySQL server
  start memcached Start Memcached server
  start all       Start all servers

  stop redis      Stop Redis server
  stop mongo      Stop MongoDB server
  stop mysql      Stop MySQL server
  stop memcached  Stop Memcached server
  stop all        Stop all servers

  help            Show this help message

Notes:
  - Redis logs:   $DBS_DIR/redis.log
  - MongoDB logs: $DBS_DIR/mongo.log
  - MySQL logs:   $DBS_DIR/mysql.log
  - Memcached logs: $DBS_DIR/memcached.log
EOF
}


if command -v conda >/dev/null 2>&1; then
    CONDA_BASE=$(conda info --base)
    source "$CONDA_BASE/etc/profile.d/conda.sh"
else
    echo "Error: Conda not found or not initialized."
    exit 1
fi


case "$1" in
  start)
    case "$2" in
      redis) start_redis ;;
      mongo) start_mongo ;;
      mysql) start_mysql ;;
      memcached) start_memcached ;;
      all)
        start_redis
        start_mongo
        start_mysql
        start_memcached
        ;;
      *) print_help ;;
    esac
    ;;
  stop)
    case "$2" in
      redis) stop_redis ;;
      mongo) stop_mongo ;;
      mysql) stop_mysql ;;
      memcached) stop_memcached ;;
      all)
        stop_redis
        stop_mongo
        stop_mysql
        stop_memcached
        ;;
      *) print_help ;;
    esac
    ;;
  *)
    print_help
    ;;
esac
