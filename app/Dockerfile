# Use an official Python runtime as an image
FROM python:3.8-alpine

# The EXPOSE instruction indicates the ports on which a container
EXPOSE 5010

# Sets the working directory for following COPY and CMD instructions
# Notice we haven’t created a directory by this name - this instruction
# creates a directory with this name if it doesn’t exist
WORKDIR /app

COPY requirements.txt /app
COPY templates /app/templates
RUN pip install -r requirements.txt

# Run webapp.py when the container launches
COPY webapp.py /app
ENTRYPOINT ["python"]
CMD ["app.py"]