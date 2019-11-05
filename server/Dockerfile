FROM debian

RUN apt-get update
RUN apt-get install -y \
	wget \
	bc \
	curl \
	python3


VOLUME ["/cyberpower"]
WORKDIR /root


COPY powerpanel_132_amd64.deb /root/powerpanel_132_amd64.deb
COPY pwrstatd.conf /root/pwrstatd.conf

# Copy the scripts
COPY start_script.sh /root/start_script.sh
COPY monitor.sh /root/monitor.sh

COPY powerFailure.sh /root/powerFailure.sh
COPY lowPower.sh /root/lowPower.sh

# Copy the notification server
COPY server.py /root/server.py
COPY sendEvent.py /root/sendEvent.py

# Make sure they are executable
RUN chmod +x /root/start_script.sh /root/monitor.sh /root/powerFailure.sh /root/lowPower.sh /root/sendEvent.py /root/server.py

RUN dpkg -i ./powerpanel_132_amd64.deb

# Remove the default files
RUN rm /etc/pwrstatd-email.sh /etc/pwrstatd-lowbatt.sh /etc/pwrstatd-powerfail.sh /etc/pwrstatd.conf

EXPOSE 8888

CMD /root/start_script.sh