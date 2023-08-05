## This init script is run on guest

while [ ! -e /var/lib/vmonere/guest/host_config.txt ]
do
	sleep 5
done

/bin/nohup /bin/python /var/lib/vmonere/guest/vmonere_agent.py &
