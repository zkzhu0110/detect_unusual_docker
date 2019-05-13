alertmanager --config.file /etc/alertmanager/alertmanager.yml > alertmanager_out.file 2>&1 &
prometheus --config.file /etc/prometheus/prometheus.yml

