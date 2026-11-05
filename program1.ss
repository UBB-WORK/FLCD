sensor_node temp_sensor;
buffer readings[10];

monitor (temp_sensor) {
    detect (temp_sensor >= 100) {
        emit 1;
    } otherwise {
        signal 0;
    }
}