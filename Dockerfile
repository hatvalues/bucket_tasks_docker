# As Scrapy runs on Python, I choose the official Python 3 Docker image.
FROM python:3.9-slim
 
# Set the working directory to /usr/src/app.
WORKDIR /usr/src/app

RUN apt-get update
RUN apt-get install git gcc -y
# Copy the file from the local host to the filesystem of the container at the working directory.
COPY requirements.txt ./
 
# Install Scrapy specified in requirements.txt.
RUN pip3 install --no-cache-dir -r requirements.txt
 
# Copy the project source code from the local host to the filesystem of the container at the working directory.
COPY . .

# Run scrapyd when the container launches.
CMD [ "bash" ]