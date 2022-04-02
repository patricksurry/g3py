call activate g3py
start /b ssh pi@rpi4-panels /home/pi/dhc2-beaver-sim/startup.sh > panels.log 2>&1
uvicorn metrics:app --host 0.0.0.0 --reload
