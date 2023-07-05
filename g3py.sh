# start the metrics hub and local producer(s)
# See https://stackoverflow.com/questions/3004811/how-do-you-run-multiple-programs-in-parallel-from-a-bash-script
(
    trap 'kill 0' SIGINT
    uvicorn g3py.hub:app --host 0.0.0.0 --port 1234 &
    python -m fake.fakemetrics -h http://localhost:1234 &
    (cd ../beaver-sim && python monitor.py --mock -i 1 -h http://localhost:1234 -l debug) &
    wait
)