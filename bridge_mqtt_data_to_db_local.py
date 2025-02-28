import sys
import json
import logging
import paho.mqtt.client as mqtt
import psycopg2
import datetime as dt

try:
    config_file_path = sys.argv[1]

    # Konfiguration laden
    config_file = open(config_file_path)
    config_json = config_file.read()
    parsed_json = json.loads(config_json)

    #MQTT
    mqtt_info = parsed_json["MQTT"]
    MQTT_BROKER = (mqtt_info["mqtt_broker"])
    MQTT_PORT = (mqtt_info["mqtt_port"])
    MQTT_TOPIC = (mqtt_info["mqtt_topic"])
    MQTT_USERNAME = (mqtt_info["mqtt_username"])
    MQTT_PASSWORD = (mqtt_info["mqtt_password"])

    #DB
    mqtt_info = parsed_json["DB"]
    db_name = (mqtt_info["db_name"])
    db_user = (mqtt_info["db_user"])
    db_pw   = (mqtt_info["db_pw"])
    db_host = (mqtt_info["db_host"])
    db_port = (mqtt_info["db_port"])

    #ConnectionData
    con_info = parsed_json["ConData"]
    update_interval = (con_info["update_interval"])
except:
    print("Fehler beim Laden der KonfigurationsDatei")
finally:
    print("MQTT_BROKER = " + MQTT_BROKER)
    print("MQTT_PORT   = " + str(MQTT_PORT))
    print("MQTT_TOPIC  = " + MQTT_TOPIC)
    print("db_host     = " + db_host)
    print("db_name     = " + db_name)
   
    print("Konfiguration erfolgreich geladen")

#########################################################################################

def on_connect(client, userdata, flags, rc):
    #logging.info(f"Connected with result code {rc}")
    print(f"Connected with result code {rc}")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    #logging.info(f"Message received on topic {msg.topic}")
    print(f"Message received on topic {msg.topic}")
    try:
        json_data = json.loads(msg.payload.decode('utf-8'))
        formated_latest_json = json.dumps(json_data)
        payload = str(formated_latest_json)
        set_data(payload)
    except json.JSONDecodeError:
        logging.error("Error decoding JSON")

def set_data(payload):
    print("###################################")
    print(MQTT_TOPIC)
    print("Begin Send Data -> " + str(dt.datetime.now()))
    conn = psycopg2.connect(    database = db_name, 
                                user = db_user, 
                                host= db_host,
                                password = db_pw,
                                port = db_port
                                )
    
    # Command String
    cmd = "call data.sp_set_data_live ('" + payload + "')";
    # Open a cursor to perform database operations
    cur = conn.cursor()
    # Execute a command
    cur.execute(cmd)
    # Make the changes to the database persistent
    conn.commit()
    # Close cursor and communication with the database
    cur.close()
    conn.close()
    print("End Send Data -> " + str(dt.datetime.now()))

#########################################################################################

if __name__ == "__main__":
    client = mqtt.Client()
    if MQTT_USERNAME and MQTT_PASSWORD:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    client.on_connect = on_connect
    client.on_message = on_message
    
    client.connect(MQTT_BROKER, MQTT_PORT, update_interval)
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        logging.info("Shutting down client...")
        client.disconnect()
