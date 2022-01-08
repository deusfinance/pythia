# DEPRICATED
# pythia


## Run
    $ nohup python3 gateway_api.py > gateway.nohup.log &
    $ nohup python3 node_runner.py > node_1.nohup.log &
    $ nohup python3 node_runner.py -d 2 > node_2.nohup.log &


#### Find all process started with nohup python
    ps -ef | grep "command name"
    ps -ef | grep "python"
