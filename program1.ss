sensor_node emp_sensor;
buffer readings[10];

emp_sensor = 1;
readings = "orice;

monitor (temp_sensor == 1) {
    detect (temp_sensor >= 100) {
        emit 1;
    } otherwise {
        emit 0;
    }
}