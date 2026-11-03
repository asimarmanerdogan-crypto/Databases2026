SELECT machine, COUNT(*) AS n FROM readings GROUP BY machine;

SELECT machine, MAX(vib_rms) AS peak_vib FROM readings GROUP BY machine;

SELECT COUNT(*) AS alarm_readings FROM readings WHERE vib_rms > 2.0;
