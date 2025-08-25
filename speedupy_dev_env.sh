#!/usr/bin/env bash

DBS_DIR="/app/dbs"

start_redis() {
  echo "Starting Redis with dir: $DBS_DIR/redis"
  conda activate dev_env
  redis-server --dir "$DBS_DIR/redis" &> "$DBS_DIR/redis.log" &
  echo $! > "$DBS_DIR/redis.pid"
  conda deactivate
}

start_mongo() {
  echo "Starting MongoDB with dbpath: $DBS_DIR/mongo"
  conda activate dev_env
  mongod --dbpath "$DBS_DIR/mongo" > "$DBS_DIR/mongo.log" 2>&1 &
  echo $! > "$DBS_DIR/mongo.pid"
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

print_help() {
  cat <<EOF
Usage: $0 {start|stop|help} {redis|mongo|all}

Commands:
  start redis     Start Redis server
  start mongo     Start MongoDB server
  start all       Start both Redis and MongoDB servers

  stop redis      Stop Redis server
  stop mongo      Stop MongoDB server
  stop all        Stop both Redis and MongoDB servers

  help            Show this help message

Notes:
  - Redis logs:   $DBS_DIR/redis.log
  - MongoDB logs: $DBS_DIR/mongo.log
EOF
}


if command -v conda >/dev/null 2>&1; then
    CONDA_BASE=$(conda info --base)
    # If conda is installed and initialized, use the base environment
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
      all)
        start_redis
        start_mongo
        ;;
      *) print_help ;;
    esac
    ;;
  stop)
    case "$2" in
      redis) stop_redis ;;
      mongo) stop_mongo ;;
      all)
        stop_redis
        stop_mongo
        ;;
      *) print_help ;;
    esac
    ;;
  help|-h|--help)
    print_help
    ;;
  *)
    print_help
    ;;
esac

