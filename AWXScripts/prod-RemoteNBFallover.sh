#!/bin/bash
cat /etc/wireguard/wg0.conf | grep "11.111.11.111"
if [ $? -eq 0 ]; then
	echo "osnova"
	ping -c 1 11.111.11.111
		if [ $? -ne 0 ]; then
			echo "osnova is bad"
			wg-quick down wg0
			sudo sed -i 's/Endpoint = 11.111.11.111/Endpoint = 22.222.22.222/' /etc/wireguard/wg0.conf
			wg-quick up wg0
		else 
			echo "osnova good"
		fi
	
else
	echo "reserv"
	ping -c 1 11.111.11.111
		if [ $? -eq 0 ]; then
			echo "osnova vernulas"
			wg-quick down wg0
			sudo sed -i 's/Endpoint = 22.222.22.222/Endpoint = 11.111.11.111/' /etc/wireguard/wg0.conf
			wg-quick up wg0
		else 
			echo "ostalis na reserve"
		fi
fi
