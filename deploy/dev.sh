
ROOT_DIR=$(cd -- "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && cd .. && pwd)

#echo $ROOT_DIR
docker compose -f $ROOT_DIR/compose.yml --profile dev up --build --force-recreate --watch