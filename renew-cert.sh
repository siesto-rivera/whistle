#!/bin/bash
#
# Let's Encrypt 인증서 갱신 스크립트 (호스트 cron 용)
#
# 배포가 docker-compose가 아닌 수동 docker run(whistle_web/whistle_nginx)으로
# 이뤄지면서 docker-compose.yml의 certbot 갱신 서비스가 동작하지 않게 되었다.
# 이 스크립트를 호스트 cron에 등록해 인증서를 주기적으로 갱신/반영한다.
#
# 등록 예시 (root crontab — docker 권한 때문에 root 권장):
#   sudo crontab -e
#   0 4 * * 1 /github/whistle/renew-cert.sh >> /var/log/certbot-renew.log 2>&1
#   (매주 월요일 04:00 KST에 실행. certbot은 만료 30일 이내일 때만 실제 갱신함)

set -euo pipefail

PROJECT_DIR="/github/whistle"
CERT_CONF="${PROJECT_DIR}/data/certbot/conf"
CERT_WWW="${PROJECT_DIR}/data/certbot/www"
NGINX_CONTAINER="whistle_nginx"

echo "===== $(date '+%Y-%m-%d %H:%M:%S') 인증서 갱신 시작 ====="

# 1) 인증서 갱신 시도 (만료 임박 시에만 실제 갱신됨)
#    webroot 방식은 최초 발급 시 저장된 renewal conf를 재사용한다.
#    --no-random-sleep-on-renew: certbot이 비대화형 실행 시 기본으로 넣는
#    최대 ~8분 랜덤 지연을 끈다(서버 1대라 부하 분산 불필요, 즉시 갱신).
docker run --rm \
  -v "${CERT_CONF}:/etc/letsencrypt" \
  -v "${CERT_WWW}:/var/www/certbot" \
  certbot/certbot renew --webroot -w /var/www/certbot --no-random-sleep-on-renew

# 2) 갱신된 인증서를 nginx가 다시 읽도록 reload
if docker ps --format '{{.Names}}' | grep -q "^${NGINX_CONTAINER}$"; then
  docker exec "${NGINX_CONTAINER}" nginx -s reload
  echo "nginx(${NGINX_CONTAINER}) reload 완료"
else
  echo "경고: ${NGINX_CONTAINER} 컨테이너가 실행 중이 아니라 reload를 건너뜀" >&2
fi

echo "===== $(date '+%Y-%m-%d %H:%M:%S') 인증서 갱신 종료 ====="
